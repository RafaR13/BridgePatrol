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
        return "|".join(str(value) for value in values)

    def _set_analysis_window(
        self, start_ts: int | None = None, end_ts: int | None = None
    ) -> None:
        self._analysis_start_ts = start_ts
        self._analysis_has_time_filter = start_ts is not None or end_ts is not None
        self._transaction_context = None

        if end_ts is not None:
            self._analysis_end_ts = end_ts
            return

        tx_timestamps = [
            tx.timestamp
            for tx in self.fetch_blockchain_transactions()
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
        return self._filter_objects_for_analysis_window(self.fetch_blockchain_transactions())

    def _events_by_event_type(
        self, event_type: NormalizedEventType, bridge: str | None = None
    ) -> list[NormalizedEvent]:
        bridge_name = bridge or self.bridge
        events = NormalizedEventRepository.get_events_by_event_type(event_type, bridge_name)
        return self._filter_events_for_analysis_window(events)

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

        return grouped_events

    def _blockchain_transaction_context(self) -> tuple[dict[str, int], dict[str, int]]:
        if self._transaction_context is not None:
            return self._transaction_context

        blockchain_transactions = self.fetch_blockchain_transactions()
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

    def _event_is_recent(
        self,
        bridge: str,
        event_timestamp: int | None,
        event_block_number: int | None,
    ) -> bool:
        end_ts = self._analysis_end_ts
        time_threshold = TIME_THRESHOLDS.get(bridge, 3600)
        number_of_blocks_to_confirm = BlockConfirmationThresholds.get(bridge, 12)
        tx_block_numbers = [
            tx.block_number
            for tx in self.fetch_blockchain_transactions()
            if getattr(tx, "block_number", None) is not None
        ]
        latest_block_number = max(tx_block_numbers) if tx_block_numbers else None

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
