from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from db.repository.detection_alert.detection_alert_model import DetectionAlert
from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from db.repository.normalized_event.normalized_event_repository import NormalizedEventRepository
from normalization.event_types import NormalizedEventType
from signature_detection.constants import BRIDGE_EVENT_MAP, TIME_THRESHOLDS, BlockConfirmationThresholds, AlertSeverity, SignatureType


class Analyser(ABC):
    def __init__(self, bridge: str):
        self.bridge = bridge
    
    def pick_first(self, events: list[NormalizedEvent]) -> NormalizedEvent | None:
        """Helper function to pick the first event from a list, or return None if the list is empty."""
        return events[0] if events else None

    def fetch_event_pairs(self, bridge: str, source: NormalizedEventType, destination: NormalizedEventType) -> dict[str, dict[str, list[NormalizedEvent]]]:
        """
        Fetches and groups normalized events for the given source and destination event types by correlation_id.
        ex: lock-mint, burn-release
        """
        # 2: query the normalized events for the source and destination events
        source_events = NormalizedEventRepository.get_events_by_event_type(source, bridge)
        destination_events = NormalizedEventRepository.get_events_by_event_type(destination, bridge)
        
        # 3: group the events by correlation_id
        grouped_events = {}
        for event in source_events:
            if not event.correlation_id:
                continue # TODO: handle events without correlation_id (i think it never happens tho)
            if event.correlation_id not in grouped_events:
                grouped_events[event.correlation_id] = {"source": [], "destination": []}
            grouped_events[event.correlation_id]["source"].append(event)
        for event in destination_events:
            if not event.correlation_id:
                continue # TODO: handle events without correlation_id (i think it never happens tho)
            if event.correlation_id not in grouped_events:
                grouped_events[event.correlation_id] = {"source": [], "destination": []}
            grouped_events[event.correlation_id]["destination"].append(event)

        return grouped_events

    @abstractmethod
    def fetch_blockchain_transactions(self):
        pass

    @abstractmethod
    def fetch_crosschain_transactions(self):
        pass

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
            probability: str
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
            probability=probability
        )
    
    def analyse_source_destination(self, start_ts: int, end_ts: int) -> List[DetectionAlert]:
        """Run source/destination event correlation checks."""
        alerts: List[DetectionAlert] = []

        alerts.extend(self.lock_without_mint(self.bridge, start_ts, end_ts))
        alerts.extend(self.mint_without_lock(self.bridge, start_ts, end_ts))
        alerts.extend(self.over_mint(self.bridge))
        alerts.extend(self.over_release(self.bridge))
        return alerts

    @abstractmethod
    def analyse_crosschain_transactions(self) -> List[DetectionAlert]:
        """Run cross-chain transaction checks."""
        raise NotImplementedError

    @abstractmethod
    def analyse_proofs(self) -> List[DetectionAlert]:
        """Run proof-related checks."""
        raise NotImplementedError

    def analyse_all(self, start_ts: int, end_ts: int) -> List[DetectionAlert]:
        """
        Run every analyser stage and return a single alert list.
        """
        alerts: List[DetectionAlert] = []
        alerts.extend(self.analyse_source_destination(start_ts, end_ts))
        alerts.extend(self.analyse_crosschain_transactions())
        alerts.extend(self.analyse_proofs())
        return alerts
    
    def lock_without_mint(self, bridge: str, start_ts: int, end_ts: int) -> list[DetectionAlert]:
        """lock event without a corresponding mint event"""
        # TODO: check if proof was sent but no mint occured
        grouped_events = self.fetch_event_pairs(bridge, BRIDGE_EVENT_MAP[bridge].lock, BRIDGE_EVENT_MAP[bridge].mint)
        alerts = []

        time_threshold = TIME_THRESHOLDS.get(bridge, 3600)
        number_of_blocks_to_confirm = BlockConfirmationThresholds.get(bridge, 12)
        latest_block_number = 67 # TODO: call XChainDataGen to get latest block number for the chain
        
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
        
        for correlation_id, events in grouped_events.items():
            if events["source"] and not events["destination"]:
                lock_event = self.pick_first(events["source"])
                
                # no lock event too, so keep going
                if lock_event is None:
                    continue

                event_timestamp = tx_timestamps.get(lock_event.transaction_hash, lock_event.timestamp)
                event_block_number = tx_block_numbers.get(lock_event.transaction_hash, lock_event.block_number)
                event_age = end_ts - event_timestamp if event_timestamp is not None else None

                # block is recent if it is close enough to the latest block (depending on each chain's threshold)
                is_recent_block = (
                    latest_block_number is not None
                    and event_block_number is not None
                    and latest_block_number - event_block_number <= number_of_blocks_to_confirm
                )
                event_is_within_time_threshold = event_age is not None and event_age < time_threshold

                severity = AlertSeverity.MEDIUM
                description_suffix = "No matching mint event was observed."
                if is_recent_block or event_is_within_time_threshold:
                    severity = AlertSeverity.LOW
                    description_suffix = (
                        "No matching mint event was observed yet, but the lock is still within the expected processing window."
                    )

                alerts.append(self.create_detection_alert(
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
                            f"{description_suffix}"
                        ),
                    created_at_ts=event_timestamp if event_timestamp is not None else lock_event.timestamp,
                    probability="TODO"
                ))
        return alerts

    def mint_without_lock(self, bridge: str, start_ts: int, end_ts: int) -> list[DetectionAlert]:
        grouped_events = self.fetch_event_pairs(bridge, BRIDGE_EVENT_MAP[bridge].mint, BRIDGE_EVENT_MAP[bridge].lock)
        alerts = []
        time_threshold = TIME_THRESHOLDS.get(bridge, 3600)
        number_of_blocks_to_confirm = BlockConfirmationThresholds.get(bridge, 12)
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
        latest_block_number = 67 # TODO: call XChainDataGen to get latest block number for the chain

        for correlation_id, events in grouped_events.items():
            if events["source"] and not events["destination"]:
                mint_event = self.pick_first(events["source"])

                if mint_event is None:
                    continue

                event_timestamp = tx_timestamps.get(mint_event.transaction_hash, mint_event.timestamp)
                event_block_number = tx_block_numbers.get(mint_event.transaction_hash, mint_event.block_number)
                event_age = end_ts - event_timestamp if event_timestamp is not None else None

                is_recent_block = (
                    latest_block_number is not None
                    and event_block_number is not None
                    and latest_block_number - event_block_number <= number_of_blocks_to_confirm
                )
                event_is_within_time_threshold = event_age is not None and event_age < time_threshold

                severity = AlertSeverity.HIGH
                description_suffix = "No matching lock event was observed."
                if is_recent_block or event_is_within_time_threshold:
                    severity = AlertSeverity.MEDIUM
                    description_suffix = (
                        "No matching lock event was observed yet, but the mint is still within the expected processing window."
                    )

                alerts.append(self.create_detection_alert(
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
                        f"{description_suffix}"
                    ),
                    created_at_ts=event_timestamp if event_timestamp is not None else mint_event.timestamp,
                    probability="TODO"
                ))
        return alerts

    def over_mint(self, bridge: str) -> list[DetectionAlert]:
        grouped_events = self.fetch_event_pairs(bridge, BRIDGE_EVENT_MAP[bridge].lock, BRIDGE_EVENT_MAP[bridge].mint)
        alerts = []
        for correlation_id, events in grouped_events.items():
            if not events["destination"] or not events["source"]:
                continue
            mint_event = events["destination"][0]
            lock_event = events["source"][0]
            if mint_event.amount_out is not None and lock_event.amount_out is not None and mint_event.amount_out > lock_event.amount_out:
                alerts.append(self.create_detection_alert(
                    signature_type=SignatureType.OVER_MINT,
                    severity=AlertSeverity.LOW,
                    bridge=bridge,
                    correlation_id=correlation_id,
                    correlation_type=None,
                    src_event_id=lock_event.id,
                    dst_event_id=mint_event.id,
                    title=f"{bridge}: over-mint detected",
                    description=(
                        f"Found mint event {mint_event.event_type} with amount {mint_event.amount_out} "
                        f"which is greater than the corresponding lock event {lock_event.event_type} "
                        f"with amount {lock_event.amount_out} for correlation_id={correlation_id}."
                    ),
                    created_at_ts=mint_event.timestamp,
                    probability="TODO"
                ))
        return alerts

    def over_release(self, bridge: str) -> list[DetectionAlert]:
        grouped_events = self.fetch_event_pairs(bridge, BRIDGE_EVENT_MAP[bridge].burn, BRIDGE_EVENT_MAP[bridge].release)
        alerts = []
        for correlation_id, events in grouped_events.items():
            if not events["destination"] or not events["source"]:
                continue
            release_event = events["destination"][0]
            burn_event = events["source"][0]
            if release_event.amount_out is not None and burn_event.amount_out is not None and release_event.amount_out > burn_event.amount_out:
                alerts.append(self.create_detection_alert(
                    signature_type=SignatureType.OVER_RELEASE,
                    severity=AlertSeverity.LOW,
                    bridge=bridge,
                    correlation_id=correlation_id,
                    correlation_type=None,
                    src_event_id=burn_event.id,
                    dst_event_id=release_event.id,
                    title=f"{bridge}: over-release detected",
                    description=(
                        f"Found release event {release_event.event_type} with amount {release_event.amount_out} "
                        f"which is greater than the corresponding burn event {burn_event.event_type} "
                        f"with amount {burn_event.amount_out} for correlation_id={correlation_id}."
                    ),
                    created_at_ts=release_event.timestamp,
                    probability="TODO"
                ))
        return alerts

    def detect_replays(self, bridge: str, source: NormalizedEventType, destination: NormalizedEventType) -> list[DetectionAlert]:
        grouped_events = self.fetch_event_pairs(bridge, source, destination)
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
                _safe_get(event, "sender", "from_address", "src_from_address", "depositor", "withdrawer"),
                _safe_get(event, "token_out", "output_token", "dst_contract_address"),
                _safe_get(event, "token_in", "input_token", "src_contract_address"),
                _safe_get(event, "src_blockchain"),
                _safe_get(event, "dst_blockchain"),
            )

        for correlation_id, events in grouped_events.items():
            source_events = events["source"]
            destination_events = events["destination"]

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
                    alerts.append(self.create_detection_alert(
                        signature_type=SignatureType.PROOF_REPLAY,
                        severity=AlertSeverity.MEDIUM,
                        bridge=bridge,
                        correlation_id=correlation_id,
                        correlation_type=None,
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
                        probability="TODO"
                        )
                    )

            # Case 2:
            # same correlation_id but destination payloads are inconsistent
            if len(dst_fingerprints) > 1:
                for dst_event in destination_events:
                    alerts.append(self.create_detection_alert(
                            signature_type=SignatureType.PROOF_REPLAY,
                            severity=AlertSeverity.LOW,
                            bridge=bridge,
                            correlation_id=correlation_id,
                            correlation_type=None,
                            src_event_id=source_event.id,
                            dst_event_id=dst_event.id,
                            title=f"{bridge}: inconsistent replay payload detected",
                            description=(
                                f"Found multiple destination events for correlation_id={correlation_id} "
                                f"with different logical payloads (amount / recipient / token / chain context differ). "
                                f"This is stronger evidence of replay, mutation, or malformed processing."
                            ),
                            created_at_ts=dst_event.timestamp,
                            probability="TODO"
                        )
                    )

            # Case 3:
            # even if payload is the same, more than one destination event is still suspicious
            # when the bridge action should be one-to-one
            if len(dst_tx_hashes) <= 1 and len(dst_fingerprints) == 1 and len(destination_events) > 1:
                for dst_event in destination_events:
                    alerts.append(self.create_detection_alert(
                        signature_type=SignatureType.PROOF_REPLAY,
                        severity=AlertSeverity.LOW,
                        bridge=bridge,
                        correlation_id=correlation_id,
                        correlation_type=None,
                        src_event_id=source_event.id,
                        dst_event_id=dst_event.id,
                        title=f"{bridge}: duplicate destination event for same correlation_id",
                        description=(
                            f"Found repeated destination events with identical payload for "
                            f"correlation_id={correlation_id}. This can be benign duplication, "
                            f"but may also indicate replay or duplicate ingestion."
                        ),
                        created_at_ts=dst_event.timestamp,
                        probability="TODO"
                    )
                    )

        return alerts
