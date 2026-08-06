from __future__ import annotations

import json

from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from db.repository.normalized_event.normalized_event_repository import (
    NormalizedEventRepository,
)
from normalization.event_types import NormalizedEventType
from signature_detection.constants import (
    BRIDGE_EVENT_MAP,
    TIME_THRESHOLDS,
    BlockConfirmationThresholds,
    EventPairFlow,
)


class AnalyserUtilsMixin:
    def pick_first(self, events: list[NormalizedEvent]) -> NormalizedEvent | None:
        """Helper function to pick the first event from a list, or return None if the list is empty."""
        return events[0] if events else None

    def _configured_flows(self, bridge: str, flow_type: str) -> tuple[EventPairFlow, ...]:
        config = BRIDGE_EVENT_MAP.get(bridge)
        if config is None:
            return ()
        return getattr(config, flow_type, ())

    def _event_value(self, event: NormalizedEvent, field_path: str):
        if field_path.startswith("extra_data."):
            key = field_path.split(".", 1)[1]
            if not event.extra_data:
                return None
            try:
                extra_data = json.loads(event.extra_data)
            except (TypeError, json.JSONDecodeError):
                return None
            return extra_data.get(key)
        return getattr(event, field_path, None)

    def _event_group_key(self, event: NormalizedEvent, fields: tuple[str, ...]) -> str | None:
        values = [self._event_value(event, field) for field in fields]
        if any(value is None for value in values):
            return None
        if len(set(map(str, values))) == 1:
            return str(values[0])
        return "|".join(str(value) for value in values)

    def _set_analysis_window(
        self, start_ts: int | None = None, end_ts: int | None = None
    ) -> None:
        self._analysis_start_ts = start_ts
        self._analysis_has_time_filter = start_ts is not None or end_ts is not None
        self._transaction_context = None
        self._analysis_blockchain_transactions_cache = None
        self._analysis_blockchain_transactions_by_hash_cache = None
        self._latest_block_numbers_by_blockchain = None
        self._latest_block_number = None
        self._cross_chain_transactions_cache = None
        self._transfers_by_transaction_hash_cache = {}
        self._events_cache = {}
        self._event_pairs_cache = {}

        if end_ts is not None:
            self._analysis_end_ts = end_ts
            return

        latest_timestamp_fetcher = getattr(self, "fetch_latest_transaction_timestamp", None)
        if latest_timestamp_fetcher is not None:
            self._analysis_end_ts = latest_timestamp_fetcher(start_ts=start_ts)
            return

        tx_timestamps = [
            tx.timestamp
            for tx in self._analysis_blockchain_transactions()
            if getattr(tx, "timestamp", None) is not None
        ]
        self._analysis_end_ts = max(tx_timestamps) if tx_timestamps else None

    def _object_timestamp(self, obj) -> int | None:
        return getattr(obj, "timestamp", None)

    def _event_timestamp(self, event: NormalizedEvent) -> int | None:
        if event.timestamp is not None:
            return event.timestamp

        _, tx_timestamps = self._blockchain_transaction_context()
        return tx_timestamps.get(event.transaction_hash)

    def _is_timestamp_in_analysis_window(self, timestamp: int | None) -> bool:
        if not self._analysis_has_time_filter:
            return True
        if timestamp is None:
            return False
        if self._analysis_start_ts is not None and timestamp < self._analysis_start_ts:
            return False
        if self._analysis_end_ts is not None and timestamp > self._analysis_end_ts:
            return False
        return True

    def _event_in_analysis_window(self, event: NormalizedEvent) -> bool:
        return self._is_timestamp_in_analysis_window(self._event_timestamp(event))

    def _filter_events_for_analysis_window(
        self, events: list[NormalizedEvent]
    ) -> list[NormalizedEvent]:
        return [event for event in events if self._event_in_analysis_window(event)]

    def _filter_objects_for_analysis_window(self, objects: list) -> list:
        return [
            obj
            for obj in objects
            if self._is_timestamp_in_analysis_window(self._object_timestamp(obj))
        ]

    def _analysis_blockchain_transactions(self) -> list:
        if self._analysis_blockchain_transactions_cache is not None:
            return self._analysis_blockchain_transactions_cache

        try:
            transactions = self.fetch_blockchain_transactions(
                start_ts=self._analysis_start_ts,
                end_ts=self._analysis_end_ts,
            )
        except TypeError:
            transactions = self.fetch_blockchain_transactions()
            transactions = self._filter_objects_for_analysis_window(transactions)

        self._analysis_blockchain_transactions_cache = transactions
        return transactions

    def _analysis_blockchain_transactions_by_hash(self) -> dict[str, object]:
        if self._analysis_blockchain_transactions_by_hash_cache is not None:
            return self._analysis_blockchain_transactions_by_hash_cache

        self._analysis_blockchain_transactions_by_hash_cache = {
            tx.transaction_hash: tx
            for tx in self._analysis_blockchain_transactions()
            if getattr(tx, "transaction_hash", None) is not None
        }
        return self._analysis_blockchain_transactions_by_hash_cache

    def _analysis_cross_chain_transactions(self) -> list:
        if self._cross_chain_transactions_cache is not None:
            return self._cross_chain_transactions_cache

        fetcher = getattr(self, "fetch_cross_chain_transactions", None)
        if fetcher is None:
            self._cross_chain_transactions_cache = []
            return self._cross_chain_transactions_cache

        try:
            cctxs = fetcher(
                start_ts=self._analysis_start_ts,
                end_ts=self._analysis_end_ts,
            )
        except TypeError:
            cctxs = fetcher()

        self._cross_chain_transactions_cache = cctxs
        return cctxs

    def _events_by_event_type(
        self, event_type: NormalizedEventType, bridge: str | None = None
    ) -> list[NormalizedEvent]:
        bridge_name = bridge or self.bridge
        cache_key = (bridge_name, self._event_type_value(event_type))
        if cache_key in self._events_cache:
            return self._events_cache[cache_key]

        try:
            events = NormalizedEventRepository.get_events_by_event_type(
                event_type,
                bridge_name,
                start_ts=self._analysis_start_ts,
                end_ts=self._analysis_end_ts,
            )
        except TypeError:
            events = NormalizedEventRepository.get_events_by_event_type(
                event_type,
                bridge_name,
            )
        filtered_events = self._filter_events_for_analysis_window(events)
        self._events_cache[cache_key] = filtered_events
        return filtered_events

    def _created_at_ts_for_event(self, event: NormalizedEvent) -> int | None:
        return self._event_timestamp(event)

    def fetch_event_pairs(
        self,
        bridge: str,
        flow_or_source: EventPairFlow | NormalizedEventType,
        destination: NormalizedEventType | None = None,
    ) -> dict[str, dict[str, list[NormalizedEvent]]]:
        """
        Fetches and groups normalized events according to a configured bridge flow.
        """
        if isinstance(flow_or_source, EventPairFlow):
            flow = flow_or_source
        else:
            if destination is None:
                raise ValueError(
                    "destination is required when fetch_event_pairs is called with event types"
                )
            flow = EventPairFlow(
                name="ad_hoc",
                source=flow_or_source,
                destination=destination,
            )

        cache_key = (bridge, flow)
        if cache_key in self._event_pairs_cache:
            return self._event_pairs_cache[cache_key]

        source_events = self._events_by_event_type(flow.source, bridge)
        destination_events = self._events_by_event_type(flow.destination, bridge)

        grouped_events = {}
        for event in source_events:
            group_key = self._event_group_key(event, flow.source_key)
            if group_key is None:
                continue
            if group_key not in grouped_events:
                grouped_events[group_key] = {"source": [], "destination": []}
            grouped_events[group_key]["source"].append(event)

        for event in destination_events:
            group_key = self._event_group_key(event, flow.destination_key)
            if group_key is None:
                continue
            if group_key not in grouped_events:
                grouped_events[group_key] = {"source": [], "destination": []}
            grouped_events[group_key]["destination"].append(event)

        for related in flow.related_events:
            related_events = self._events_by_event_type(related.event_type, bridge)
            anchors_by_value: dict[str, set[str]] = {}
            for group_key, events in grouped_events.items():
                for anchor_event in events[related.anchor_side]:
                    if anchor_event.event_type != related.anchor_event_type:
                        continue
                    anchor_value = self._event_value(anchor_event, related.anchor_field)
                    if anchor_value is None:
                        continue
                    anchors_by_value.setdefault(str(anchor_value), set()).add(group_key)

            for event in related_events:
                event_value = self._event_value(event, related.event_field)
                if event_value is None:
                    continue
                for group_key in anchors_by_value.get(str(event_value), set()):
                    if event not in grouped_events[group_key][related.side]:
                        grouped_events[group_key][related.side].append(event)

        self._event_pairs_cache[cache_key] = grouped_events
        return grouped_events

    def _blockchain_transaction_context(self) -> tuple[dict[str, int], dict[str, int]]:
        if self._transaction_context is not None:
            return self._transaction_context

        blockchain_transactions = self._analysis_blockchain_transactions()
        tx_block_numbers = {
            tx.transaction_hash: tx.block_number
            for tx in blockchain_transactions
            if tx.transaction_hash is not None and tx.block_number is not None
        }
        tx_timestamps = {
            tx.transaction_hash: tx.timestamp
            for tx in blockchain_transactions
            if tx.transaction_hash is not None and tx.timestamp is not None
        }
        self._transaction_context = (tx_block_numbers, tx_timestamps)
        return self._transaction_context

    def _analysis_latest_block_numbers_by_blockchain(self) -> dict[str, int]:
        if self._latest_block_numbers_by_blockchain is not None:
            return self._latest_block_numbers_by_blockchain

        latest_by_blockchain: dict[str, int] = {}
        latest_block_number = None
        for tx in self._analysis_blockchain_transactions():
            block_number = getattr(tx, "block_number", None)
            if block_number is None:
                continue

            if latest_block_number is None or block_number > latest_block_number:
                latest_block_number = block_number

            blockchain = self._normalized_value(getattr(tx, "blockchain", None))
            if blockchain is None:
                continue
            current = latest_by_blockchain.get(blockchain)
            if current is None or block_number > current:
                latest_by_blockchain[blockchain] = block_number

        self._latest_block_numbers_by_blockchain = latest_by_blockchain
        self._latest_block_number = latest_block_number
        return self._latest_block_numbers_by_blockchain

    def _analysis_latest_block_number(self, blockchain: str | None = None) -> int | None:
        latest_by_blockchain = self._analysis_latest_block_numbers_by_blockchain()
        normalized_blockchain = self._normalized_value(blockchain)
        if normalized_blockchain is not None:
            latest_block_number = latest_by_blockchain.get(normalized_blockchain)
            if latest_block_number is not None:
                return latest_block_number
        return self._latest_block_number

    def _transfers_by_transaction_hash(self, transfer_repository) -> dict[str, list]:
        cache_key = id(transfer_repository)
        if cache_key in self._transfers_by_transaction_hash_cache:
            return self._transfers_by_transaction_hash_cache[cache_key]

        transaction_hashes = {
            tx.transaction_hash
            for tx in self._analysis_blockchain_transactions()
            if getattr(tx, "transaction_hash", None) is not None
        }

        fetch_by_hashes = getattr(transfer_repository, "get_by_transaction_hashes", None)
        if fetch_by_hashes is not None:
            transfers = fetch_by_hashes(transaction_hashes)
        else:
            transfers = [
                transfer
                for transfer in transfer_repository.get_all()
                if getattr(transfer, "transaction_hash", None) in transaction_hashes
            ]

        transfers_by_tx: dict[str, list] = {}
        for transfer in transfers:
            transfers_by_tx.setdefault(transfer.transaction_hash, []).append(transfer)

        self._transfers_by_transaction_hash_cache[cache_key] = transfers_by_tx
        return transfers_by_tx

    def _event_is_recent(
        self,
        bridge: str,
        event_timestamp: int | None,
        event_block_number: int | None,
        event_blockchain: str | None = None,
    ) -> bool:
        end_ts = self._analysis_end_ts
        time_threshold = TIME_THRESHOLDS.get(bridge, 3600)
        number_of_blocks_to_confirm = BlockConfirmationThresholds.get(bridge, 12)
        latest_block_number = self._analysis_latest_block_number(event_blockchain)

        is_recent_block = (
            latest_block_number is not None
            and event_block_number is not None
            and event_block_number <= latest_block_number
            and latest_block_number - event_block_number <= number_of_blocks_to_confirm
        )
        event_age = (
            end_ts - event_timestamp
            if end_ts is not None and event_timestamp is not None
            else None
        )
        event_is_within_time_threshold = event_age is not None and event_age < time_threshold

        return is_recent_block or event_is_within_time_threshold

    def _event_type_value(self, event_type) -> str:
        return getattr(event_type, "value", str(event_type))

    def _normalized_value(self, value):
        if value is None:
            return None
        return str(value).lower()
