from __future__ import annotations

from abc import ABC, abstractmethod
import json
from typing import List

from db.repository.detection_alert.detection_alert_model import DetectionAlert
from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from db.repository.normalized_event.normalized_event_repository import (
    NormalizedEventRepository,
)
from db.repository.transfer_events.transfer_events_repository import (
    CCIPTransferRepository,
    CCTPTransferRepository,
    PolygonTransferRepository,
    RoninTransferRepository,
)
from normalization.event_types import NormalizedEventType
from signature_detection.constants import (
    BRIDGE_EVENT_MAP,
    TOKEN_CONTRACT_ATTACK_CONFIG,
    TIME_THRESHOLDS,
    VERIFIED_CONTRACTS,
    BlockConfirmationThresholds,
    AlertSeverity,
    EventPairFlow,
    SignatureType,
    TokenContractAttackConfig,
)


TRANSFER_REPOSITORIES = {
    "ccip": CCIPTransferRepository,
    "cctp": CCTPTransferRepository,
    "polygon": PolygonTransferRepository,
    "ronin": RoninTransferRepository,
}


class Analyser(ABC):
    def __init__(self, bridge: str):
        self.bridge = bridge
        self._transaction_context: tuple[dict[str, int], dict[str, int]] | None = None

    @abstractmethod
    def fetch_blockchain_transactions(self):
        pass

    @abstractmethod
    def analyse_bridge_specific_signatures(self) -> List[DetectionAlert]:
        """Run checks that only apply to this bridge."""
        pass

    def analyse_all(self, start_ts: int, end_ts: int) -> List[DetectionAlert]:
        """
        Run every configured analyser check and return a single alert list.
        """
        alerts: List[DetectionAlert] = []

        # Missing event pairs
        alerts.extend(self.lock_without_mint(self.bridge, start_ts, end_ts))
        alerts.extend(self.mint_without_lock(self.bridge, start_ts, end_ts))

        # Tokens
        alerts.extend(self.amount_mismatch(self.bridge))
        alerts.extend(self.over_mint(self.bridge))
        alerts.extend(self.over_release(self.bridge))

        # Contract authorization
        alerts.extend(self.unauthorized_contracts(self.bridge))

        # Replay / duplicate execution
        for flow_type in ("deposits", "withdrawals"):
            for flow in self._configured_flows(self.bridge, flow_type):
                alerts.extend(self.detect_replays(self.bridge, flow))

        # Bridge-specific checks
        alerts.extend(self.analyse_bridge_specific_signatures())
        return alerts

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

        source_events = NormalizedEventRepository.get_events_by_event_type(flow.source, bridge)
        destination_events = NormalizedEventRepository.get_events_by_event_type(
            flow.destination, bridge
        )

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
            related_events = NormalizedEventRepository.get_events_by_event_type(
                related.event_type, bridge
            )
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

    def create_detection_alert(
        self,
        signature_type: SignatureType,
        severity: AlertSeverity,
        bridge: str,
        correlation_id: str,
        correlation_type: str | None,
        src_event_id: int | None,
        dst_event_id: int | None,
        title: str,
        description: str,
        created_at_ts: int,
        probability: str,
    ) -> DetectionAlert:
        return DetectionAlert(
            signature_type=signature_type,
            severity=severity,
            bridge=bridge,
            correlation_id=correlation_id,
            correlation_type=correlation_type,
            src_event_id=src_event_id,
            dst_event_id=dst_event_id,
            title=title,
            description=description,
            created_at_ts=created_at_ts,
            probability=probability,
        )

    def _event_type_value(self, event_type) -> str:
        return getattr(event_type, "value", str(event_type))

    def _verified_contracts_for_event(
        self,
        bridge: str,
        flow: EventPairFlow,
        event: NormalizedEvent,
    ) -> set[str]:
        bridge_contracts = VERIFIED_CONTRACTS.get(bridge, {})
        flow_contracts = bridge_contracts.get(flow.name, {})
        event_type = self._event_type_value(event.event_type)

        for configured_event_type, contracts in flow_contracts.items():
            if self._event_type_value(configured_event_type) == event_type:
                return {contract.lower() for contract in contracts}

        return set()

    def _contract_is_verified(self, event: NormalizedEvent, verified_contracts: set[str]) -> bool:
        if not verified_contracts:
            return True
        if not event.contract_address:
            return False
        return str(event.contract_address).lower() in verified_contracts

    def unauthorized_contracts(self, bridge: str) -> list[DetectionAlert]:
        alerts: list[DetectionAlert] = []
        seen_alerts: set[tuple[str, int | None, str, str]] = set()

        for flow_type in ("deposits", "withdrawals"):
            for flow in self._configured_flows(bridge, flow_type):
                grouped_events = self.fetch_event_pairs(bridge, flow)

                for correlation_id, events in grouped_events.items():
                    destination_exists = bool(events["destination"])

                    for side in ("source", "destination"):
                        for event in events[side]:
                            verified_contracts = self._verified_contracts_for_event(
                                bridge, flow, event
                            )
                            if not verified_contracts:
                                continue
                            if self._contract_is_verified(event, verified_contracts):
                                continue

                            alert_key = (flow.name, event.id, side, correlation_id)
                            if alert_key in seen_alerts:
                                continue
                            seen_alerts.add(alert_key)

                            is_untrusted_source_consumed = side == "source" and destination_exists
                            severity = (
                                AlertSeverity.CRITICAL
                                if is_untrusted_source_consumed
                                else AlertSeverity.HIGH
                            )
                            expected_contracts = ", ".join(sorted(verified_contracts))
                            actual_contract = event.contract_address or "<missing>"
                            source_event_id = event.id if side == "source" else None
                            destination_event_id = event.id if side == "destination" else None

                            title_suffix = (
                                "destination event was paired with an unauthorized source contract"
                                if is_untrusted_source_consumed
                                else "event emitted by unauthorized contract"
                            )

                            alerts.append(
                                self.create_detection_alert(
                                    signature_type=SignatureType.UNAUTHORIZED_CONTRACT,
                                    severity=severity,
                                    bridge=bridge,
                                    correlation_id=correlation_id,
                                    correlation_type=flow.name,
                                    src_event_id=source_event_id,
                                    dst_event_id=destination_event_id,
                                    title=f"{bridge}: {title_suffix}",
                                    description=(
                                        f"Found {side} event {event.event_type} with "
                                        f"contract_address={actual_contract} for "
                                        f"correlation_id={correlation_id}. "
                                        f"Flow={flow.name}; expected one of: {expected_contracts}."
                                    ),
                                    created_at_ts=event.timestamp,
                                    probability="TODO",
                                )
                            )

        return alerts

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
        self, bridge: str, end_ts: int, event_timestamp: int | None, event_block_number: int | None
    ) -> bool:
        time_threshold = TIME_THRESHOLDS.get(bridge, 3600)
        number_of_blocks_to_confirm = BlockConfirmationThresholds.get(bridge, 12)
        latest_block_number = NormalizedEventRepository.get_latest_block_number_by_bridge(bridge)

        is_recent_block = (
            latest_block_number is not None
            and event_block_number is not None
            and event_block_number <= latest_block_number
            and latest_block_number - event_block_number <= number_of_blocks_to_confirm
        )
        event_age = end_ts - event_timestamp if event_timestamp is not None else None
        event_is_within_time_threshold = event_age is not None and event_age < time_threshold

        return is_recent_block or event_is_within_time_threshold

    def lock_without_mint(self, bridge: str, start_ts: int, end_ts: int) -> list[DetectionAlert]:
        """lock event without a corresponding mint event"""
        # TODO: check if proof was sent but no mint occured
        alerts = []

        tx_block_numbers, tx_timestamps = self._blockchain_transaction_context()

        for flow in self._configured_flows(bridge, "deposits"):
            grouped_events = self.fetch_event_pairs(bridge, flow)
            for correlation_id, events in grouped_events.items():
                if not (events["source"] and not events["destination"]):
                    continue
                lock_event = self.pick_first(events["source"])

                # no lock event too, so keep going
                if lock_event is None:
                    continue

                event_timestamp = tx_timestamps.get(
                    lock_event.transaction_hash, lock_event.timestamp
                )
                event_block_number = tx_block_numbers.get(
                    lock_event.transaction_hash, lock_event.block_number
                )
                severity = AlertSeverity.MEDIUM
                description_suffix = "No matching mint event was observed."
                if self._event_is_recent(
                    bridge,
                    end_ts,
                    event_timestamp,
                    event_block_number,
                ):
                    severity = AlertSeverity.LOW
                    description_suffix = "No matching mint event was observed yet, but the lock is still within the expected processing window."

                alerts.append(
                    self.create_detection_alert(
                        signature_type=SignatureType.LOCK_WITHOUT_MINT,
                        severity=severity,
                        bridge=bridge,
                        correlation_id=correlation_id,
                        correlation_type=None,
                        src_event_id=lock_event.id,
                        dst_event_id=None,
                        title=f"{bridge}: lock event without corresponding mint event",
                        description=(
                            f"Found lock event {lock_event.event_type} with correlation_id={correlation_id}. "
                            f"Flow={flow.name}. "
                            f"{description_suffix}"
                        ),
                        created_at_ts=(
                            event_timestamp if event_timestamp is not None else lock_event.timestamp
                        ),
                        probability="TODO",
                    )
                )
        return alerts

    def mint_without_lock(self, bridge: str, start_ts: int, end_ts: int) -> list[DetectionAlert]:
        alerts = []
        tx_block_numbers, tx_timestamps = self._blockchain_transaction_context()

        for flow in self._configured_flows(bridge, "deposits"):
            reverse_flow = EventPairFlow(
                name=flow.name,
                source=flow.destination,
                destination=flow.source,
                source_key=flow.destination_key,
                destination_key=flow.source_key,
            )
            grouped_events = self.fetch_event_pairs(bridge, reverse_flow)
            for correlation_id, events in grouped_events.items():
                if not (events["source"] and not events["destination"]):
                    continue
                mint_event = self.pick_first(events["source"])

                if mint_event is None:
                    continue

                event_timestamp = tx_timestamps.get(
                    mint_event.transaction_hash, mint_event.timestamp
                )
                event_block_number = tx_block_numbers.get(
                    mint_event.transaction_hash, mint_event.block_number
                )
                severity = AlertSeverity.HIGH
                description_suffix = "No matching lock event was observed."
                if self._event_is_recent(
                    bridge,
                    end_ts,
                    event_timestamp,
                    event_block_number,
                ):
                    severity = AlertSeverity.MEDIUM
                    description_suffix = "No matching lock event was observed yet, but the mint is still within the expected processing window."

                alerts.append(
                    self.create_detection_alert(
                        signature_type=SignatureType.MINT_WITHOUT_LOCK,
                        severity=severity,
                        bridge=bridge,
                        correlation_id=correlation_id,
                        correlation_type=None,
                        src_event_id=None,
                        dst_event_id=mint_event.id,
                        title=f"{bridge}: mint event without corresponding lock event",
                        description=(
                            f"Found mint event {mint_event.event_type} with correlation_id={correlation_id}. "
                            f"Flow={flow.name}. "
                            f"{description_suffix}"
                        ),
                        created_at_ts=(
                            event_timestamp if event_timestamp is not None else mint_event.timestamp
                        ),
                        probability="TODO",
                    )
                )
        return alerts

    def _pick_amount_event(self, events: list[NormalizedEvent]) -> NormalizedEvent | None:
        for event in events:
            if event.amount_out is not None or event.amount_in is not None:
                return event
        return None

    def _amount_for_comparison(self, event: NormalizedEvent | None):
        if event is None:
            return None
        return event.amount_out if event.amount_out is not None else event.amount_in

    def _token_for_comparison(self, event: NormalizedEvent | None):
        if event is None:
            return None
        return event.token_out if event.token_out is not None else event.token_in

    def amount_mismatch(self, bridge: str) -> list[DetectionAlert]:
        alerts = []

        for flow_type in ("deposits", "withdrawals"):
            for flow in self._configured_flows(bridge, flow_type):
                if not flow.amount_check:
                    continue

                grouped_events = self.fetch_event_pairs(bridge, flow)
                for correlation_id, events in grouped_events.items():
                    if not events["destination"] or not events["source"]:
                        continue

                    source_event = self._pick_amount_event(events["source"])
                    destination_event = self._pick_amount_event(events["destination"])
                    source_amount = self._amount_for_comparison(source_event)
                    destination_amount = self._amount_for_comparison(destination_event)

                    if (
                        source_event is None
                        or destination_event is None
                        or source_amount is None
                        or destination_amount is None
                        or source_amount == destination_amount
                    ):
                        continue

                    source_token = self._token_for_comparison(source_event)
                    destination_token = self._token_for_comparison(destination_event)
                    token_note = ""
                    if (
                        source_token is not None
                        and destination_token is not None
                        and str(source_token).lower() != str(destination_token).lower()
                    ):
                        token_note = (
                            f" Source token={source_token}; destination token={destination_token}."
                        )

                    alerts.append(
                        self.create_detection_alert(
                            signature_type=SignatureType.AMOUNT_MISMATCH,
                            severity=AlertSeverity.MEDIUM,
                            bridge=bridge,
                            correlation_id=correlation_id,
                            correlation_type=None,
                            src_event_id=source_event.id,
                            dst_event_id=destination_event.id,
                            title=f"{bridge}: token amount mismatch detected",
                            description=(
                                f"Found source event {source_event.event_type} with amount {source_amount} "
                                f"and destination event {destination_event.event_type} with amount "
                                f"{destination_amount} for correlation_id={correlation_id}. "
                                f"Flow={flow.name}.{token_note}"
                            ),
                            created_at_ts=destination_event.timestamp or source_event.timestamp,
                            probability="TODO",
                        )
                    )

        return alerts

    def over_mint(self, bridge: str) -> list[DetectionAlert]:
        alerts = []
        for flow in self._configured_flows(bridge, "deposits"):
            if not flow.amount_check:
                continue

            grouped_events = self.fetch_event_pairs(bridge, flow)
            for correlation_id, events in grouped_events.items():
                if not events["destination"] or not events["source"]:
                    continue
                mint_event = self._pick_amount_event(events["destination"])
                lock_event = self._pick_amount_event(events["source"])
                mint_amount = self._amount_for_comparison(mint_event)
                lock_amount = self._amount_for_comparison(lock_event)
                if (
                    mint_event is not None
                    and lock_event is not None
                    and mint_amount is not None
                    and lock_amount is not None
                    and mint_amount > lock_amount
                ):
                    alerts.append(
                        self.create_detection_alert(
                            signature_type=SignatureType.OVER_MINT,
                            severity=AlertSeverity.LOW,
                            bridge=bridge,
                            correlation_id=correlation_id,
                            correlation_type=None,
                            src_event_id=lock_event.id,
                            dst_event_id=mint_event.id,
                            title=f"{bridge}: over-mint detected",
                            description=(
                                f"Found mint event {mint_event.event_type} with amount {mint_amount} "
                                f"which is greater than the corresponding lock event {lock_event.event_type} "
                                f"with amount {lock_amount} for correlation_id={correlation_id}. "
                                f"Flow={flow.name}."
                            ),
                            created_at_ts=mint_event.timestamp,
                            probability="TODO",
                        )
                    )
        return alerts

    def over_release(self, bridge: str) -> list[DetectionAlert]:
        alerts = []
        for flow in self._configured_flows(bridge, "withdrawals"):
            if not flow.amount_check:
                continue

            grouped_events = self.fetch_event_pairs(bridge, flow)
            for correlation_id, events in grouped_events.items():
                if not events["destination"] or not events["source"]:
                    continue
                release_event = self._pick_amount_event(events["destination"])
                burn_event = self._pick_amount_event(events["source"])
                release_amount = self._amount_for_comparison(release_event)
                burn_amount = self._amount_for_comparison(burn_event)
                if (
                    release_event is not None
                    and burn_event is not None
                    and release_amount is not None
                    and burn_amount is not None
                    and release_amount > burn_amount
                ):
                    alerts.append(
                        self.create_detection_alert(
                            signature_type=SignatureType.OVER_RELEASE,
                            severity=AlertSeverity.LOW,
                            bridge=bridge,
                            correlation_id=correlation_id,
                            correlation_type=None,
                            src_event_id=burn_event.id,
                            dst_event_id=release_event.id,
                            title=f"{bridge}: over-release detected",
                            description=(
                                f"Found release event {release_event.event_type} with amount {release_amount} "
                                f"which is greater than the corresponding burn event {burn_event.event_type} "
                                f"with amount {burn_amount} for correlation_id={correlation_id}. "
                                f"Flow={flow.name}."
                            ),
                            created_at_ts=release_event.timestamp,
                            probability="TODO",
                        )
                    )
        return alerts

    def detect_replays(
        self,
        bridge: str,
        flow_or_source: EventPairFlow | NormalizedEventType,
        destination: NormalizedEventType | None = None,
    ) -> list[DetectionAlert]:
        if isinstance(flow_or_source, EventPairFlow):
            flow = flow_or_source
        else:
            if destination is None:
                raise ValueError(
                    "destination is required when detect_replays is called with event types"
                )
            flow = EventPairFlow(
                name="ad_hoc",
                source=flow_or_source,
                destination=destination,
            )

        grouped_events = self.fetch_event_pairs(bridge, flow)
        alerts: list[DetectionAlert] = []

        def _safe_get(event: NormalizedEvent, *names):
            for name in names:
                if hasattr(event, name):
                    return getattr(event, name)
            return None

        def _event_fingerprint(event: NormalizedEvent) -> tuple:
            """
            Logical fingerprint of the bridge operation.
            We intentionally exclude the DB row id and timestamp.
            tx hash is included separately in the replay checks.
            """
            return (
                _safe_get(event, "amount_out", "amount"),
                _safe_get(event, "recipient", "to_address", "dst_to_address"),
                _safe_get(
                    event,
                    "sender",
                    "from_address",
                    "src_from_address",
                    "depositor",
                    "withdrawer",
                ),
                _safe_get(event, "token_out", "output_token", "dst_contract_address"),
                _safe_get(event, "token_in", "input_token", "src_contract_address"),
                _safe_get(event, "src_blockchain"),
                _safe_get(event, "dst_blockchain"),
            )

        for correlation_id, events in grouped_events.items():
            source_events = [
                event
                for event in events["source"]
                if self._event_type_value(event.event_type) == self._event_type_value(flow.source)
            ]
            destination_events = [
                event
                for event in events["destination"]
                if self._event_type_value(event.event_type)
                == self._event_type_value(flow.destination)
            ]

            if not source_events or len(destination_events) <= 1:
                continue

            source_event = self.pick_first(source_events)
            if source_event is None:
                continue

            # Distinct destination transaction hashes
            dst_tx_hashes = {
                _safe_get(event, "transaction_hash", "tx_hash")
                for event in destination_events
                if _safe_get(event, "transaction_hash", "tx_hash") is not None
            }

            # Distinct logical payloads on the destination side
            dst_fingerprints = {_event_fingerprint(event) for event in destination_events}

            # Case 1:
            # same correlation_id caused multiple executions on different destination txs
            if len(dst_tx_hashes) > 1:
                for dst_event in destination_events:
                    alerts.append(
                        self.create_detection_alert(
                            signature_type=SignatureType.PROOF_REPLAY,
                            severity=AlertSeverity.MEDIUM,
                            bridge=bridge,
                            correlation_id=correlation_id,
                            correlation_type=flow.name,
                            src_event_id=source_event.id,
                            dst_event_id=dst_event.id,
                            title=f"{bridge}: Same lock/burn event caused multiple destination events on different transactions",
                            description=(
                                f"Found multiple destination events for correlation_id={correlation_id} "
                                f"spread across different transaction hashes "
                                f"{sorted([h for h in dst_tx_hashes if h is not None])}. "
                                f"This suggests the same lock/burn may have been consumed more than once."
                            ),
                            created_at_ts=dst_event.timestamp,
                            probability="TODO",
                        )
                    )

            # Case 2:
            # same correlation_id but destination payloads are inconsistent
            if len(dst_fingerprints) > 1:
                for dst_event in destination_events:
                    alerts.append(
                        self.create_detection_alert(
                            signature_type=SignatureType.PROOF_REPLAY,
                            severity=AlertSeverity.LOW,
                            bridge=bridge,
                            correlation_id=correlation_id,
                            correlation_type=flow.name,
                            src_event_id=source_event.id,
                            dst_event_id=dst_event.id,
                            title=f"{bridge}: inconsistent replay payload detected",
                            description=(
                                f"Found multiple destination events for correlation_id={correlation_id} "
                                f"with different logical payloads (amount / recipient / token / chain context differ). "
                                f"This is stronger evidence of replay, mutation, or malformed processing."
                            ),
                            created_at_ts=dst_event.timestamp,
                            probability="TODO",
                        )
                    )

            # Case 3:
            # even if payload is the same, more than one destination event is still suspicious
            # when the bridge action should be one-to-one
            if (
                len(dst_tx_hashes) <= 1
                and len(dst_fingerprints) == 1
                and len(destination_events) > 1
            ):
                for dst_event in destination_events:
                    alerts.append(
                        self.create_detection_alert(
                            signature_type=SignatureType.PROOF_REPLAY,
                            severity=AlertSeverity.LOW,
                            bridge=bridge,
                            correlation_id=correlation_id,
                            correlation_type=flow.name,
                            src_event_id=source_event.id,
                            dst_event_id=dst_event.id,
                            title=f"{bridge}: duplicate destination event for same correlation_id",
                            description=(
                                f"Found repeated destination events with identical payload for "
                                f"correlation_id={correlation_id}. This can be benign duplication, "
                                f"but may also indicate replay or duplicate ingestion."
                            ),
                            created_at_ts=dst_event.timestamp,
                            probability="TODO",
                        )
                    )

        return alerts

    def token_contract_attacks(self) -> list[DetectionAlert]:
        alerts: list[DetectionAlert] = []
        configs = TOKEN_CONTRACT_ATTACK_CONFIG.get(self.bridge, ())
        if not configs:
            return alerts

        txs_by_hash = {
            tx.transaction_hash: tx
            for tx in self.fetch_blockchain_transactions()
            if tx.transaction_hash is not None
        }

        transfers_by_tx: dict[str, list] = {}
        transfer_repository = TRANSFER_REPOSITORIES.get(self.bridge)
        if transfer_repository is not None:
            for transfer in transfer_repository.get_all():
                transfers_by_tx.setdefault(transfer.transaction_hash, []).append(transfer)

        for config in configs:
            events = NormalizedEventRepository.get_events_by_event_type(
                config.event_type,
                self.bridge,
            )
            for event in events:
                if event.token_in is None or event.amount_in is None:
                    continue

                tx = txs_by_hash.get(event.transaction_hash)
                if self._is_native_token(event, config):
                    invalid_fields = self._check_native_token_contract(event, tx, config)
                else:
                    invalid_fields = self._check_erc20_token_contract(
                        event,
                        transfers_by_tx.get(event.transaction_hash, []),
                        config,
                    )

                if not invalid_fields:
                    continue

                correlation_id = event.correlation_id or event.transaction_hash or str(event.raw_pk)
                alerts.append(
                    self.create_detection_alert(
                        signature_type=SignatureType.CONTRACT_MISMATCH,
                        severity=AlertSeverity.HIGH,
                        bridge=self.bridge,
                        correlation_id=correlation_id,
                        correlation_type=config.correlation_type,
                        src_event_id=event.id,
                        dst_event_id=None,
                        title=config.title,
                        description=(
                            f"Found {config.event_label} event with "
                            f"correlation_id={correlation_id}. "
                            f"Invalid token contract fields: {'; '.join(invalid_fields)}."
                        ),
                        created_at_ts=event.timestamp,
                        probability="TODO",
                    )
                )

        return alerts

    def _normalized_value(self, value):
        if value is None:
            return None
        return str(value).lower()

    def _is_native_token(
        self,
        event: NormalizedEvent,
        config: TokenContractAttackConfig,
    ) -> bool:
        return self._normalized_value(event.token_in) == self._normalized_value(
            config.native_token
        )

    def _expected_contract_values(self, config: TokenContractAttackConfig) -> set[str]:
        return {contract.lower() for contract in config.expected_contracts}

    def _check_expected_source_contract(
        self,
        event: NormalizedEvent,
        config: TokenContractAttackConfig,
        check_number: int,
    ) -> list[str]:
        expected_contracts = self._expected_contract_values(config)
        if not expected_contracts:
            return []

        event_contract = self._normalized_value(event.contract_address)
        if event_contract in expected_contracts:
            return []

        expected = ", ".join(sorted(expected_contracts))
        return [
            f"{check_number}) {config.event_label} contract is not an expected "
            f"{self.bridge} source contract "
            f"(contract={event.contract_address or '<missing>'}, expected={expected})"
        ]

    def _check_native_token_contract(
        self,
        event: NormalizedEvent,
        tx,
        config: TokenContractAttackConfig,
    ) -> list[str]:
        invalid_fields = []

        if tx is None or tx.value != event.amount_in:
            invalid_fields.append(
                f"1) tx.value does not match {config.amount_label} "
                f"(tx.value={getattr(tx, 'value', '<missing>')}, amount={event.amount_in})"
            )

        invalid_fields.extend(self._check_expected_source_contract(event, config, 2))

        if str(event.status) != "1":
            invalid_fields.append(
                f"3) transaction status is not success (status={event.status or '<missing>'})"
            )

        return invalid_fields

    def _check_erc20_token_contract(
        self,
        event: NormalizedEvent,
        transfers: list,
        config: TokenContractAttackConfig,
    ) -> list[str]:
        invalid_fields = []

        if str(event.status) != "1":
            invalid_fields.append(
                f"4) transaction status is not success (status={event.status or '<missing>'})"
            )

        invalid_fields.extend(self._check_expected_source_contract(event, config, 5))

        if not transfers:
            invalid_fields.append(
                f"0) no ERC20 Transfer event found in the {config.event_label} transaction"
            )
            return invalid_fields

        matching_transfers = [
            transfer
            for transfer in transfers
            if self._normalized_value(transfer.token_address)
            == self._normalized_value(event.token_in)
            and self._normalized_value(transfer.to_address)
            == self._normalized_value(event.contract_address)
            and self._normalized_value(transfer.from_address)
            == self._normalized_value(event.actor_from)
            and transfer.amount == event.amount_in
        ]
        if matching_transfers:
            return invalid_fields

        transfer_invalid_fields = []
        token_transfers = [
            transfer
            for transfer in transfers
            if self._normalized_value(transfer.token_address)
            == self._normalized_value(event.token_in)
        ]

        if not any(
            self._normalized_value(transfer.to_address)
            == self._normalized_value(event.contract_address)
            for transfer in token_transfers
        ):
            transfer_invalid_fields.append(
                f"1) no token Transfer to the {config.event_label} contract "
                f"(expected_to={event.contract_address or '<missing>'})"
            )

        if not any(
            self._normalized_value(transfer.from_address)
            == self._normalized_value(event.actor_from)
            for transfer in token_transfers
        ):
            transfer_invalid_fields.append(
                f"2) no token Transfer from the {config.actor_label} "
                f"(expected_from={event.actor_from or '<missing>'})"
            )

        if not any(transfer.amount == event.amount_in for transfer in token_transfers):
            transfer_invalid_fields.append(
                f"3) no token Transfer amount matches the {config.amount_label} "
                f"(expected_amount={event.amount_in})"
            )

        if not transfer_invalid_fields:
            transfer_invalid_fields.append(
                f"1) 2) 3) no single token Transfer matches all {config.event_label} checks"
            )

        return invalid_fields + transfer_invalid_fields
