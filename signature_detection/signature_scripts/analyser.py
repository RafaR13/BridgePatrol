from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from db.repository.detection_alert.detection_alert_model import DetectionAlert
from normalization.event_types import NormalizedEventType
from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from db.repository.normalized_event.normalized_event_repository import NormalizedEventRepository
from db.repository.detection_alert.detection_alert_model import DetectionAlert
from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from db.repository.normalized_event.normalized_event_repository import NormalizedEventRepository
from normalization.event_types import NormalizedEventType
from signature_detection.constants import BRIDGE_EVENT_MAP, AlertSeverity, SignatureType


class Analyser(ABC):
    def __init__(self, bridge: str):
        self.bridge = bridge
    
    def pick_first(events: list[NormalizedEvent]) -> NormalizedEvent | None:
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

    def create_detection_alert(
            self, 
            signature_type: SignatureType, 
            severity: AlertSeverity, 
            bridge: str, 
            correlation_id: str, 
            correlation_type: str, 
            src_event_id: int | None, 
            dst_event_id: int | None, 
            title: str, 
            description: str, 
            created_at_ts: int
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
        )

    @abstractmethod
    def fetch_blockchain_transactions(self):
        pass

    @abstractmethod
    def fetch_crosschain_transactions(self):
        pass

    def analyse_source_destination(self) -> List[DetectionAlert]:
        """Run source/destination event correlation checks."""
        alerts = []

        alerts.extend(self.lock_without_mint(self.bridge))
        alerts.extend(self.mint_without_lock(self.bridge))
        alerts.extend(self.over_mint(self.bridge))
        alerts.extend(self.over_release(self.bridge))
        alerts.extend(self.proof_replay(self.bridge, BRIDGE_EVENT_MAP[self.bridge].lock, BRIDGE_EVENT_MAP[self.bridge].mint))
        alerts.extend(self.proof_replay(self.bridge, BRIDGE_EVENT_MAP[self.bridge].burn, BRIDGE_EVENT_MAP[self.bridge].release))
        return alerts

    def analyse_cctxs(self) -> List[DetectionAlert]:
        """Run cross-chain transaction checks."""
        raise NotImplementedError

    @abstractmethod
    def analyse_proofs(self) -> List[DetectionAlert]:
        """Run proof-related checks."""
        raise NotImplementedError

    def analyse_all(self) -> List[DetectionAlert]:
        """
        Run every analyser stage and return a single alert list.
        """
        alerts: List[DetectionAlert] = []
        alerts.extend(self.analyse_source_destination())
        alerts.extend(self.analyse_cctxs())
        alerts.extend(self.analyse_proofs())
        return alerts
    
    def lock_without_mint(self,bridge: str) -> list[DetectionAlert]:
        grouped_events = self.fetch_event_pairs(bridge, BRIDGE_EVENT_MAP[bridge].lock, BRIDGE_EVENT_MAP[bridge].mint)
        # 4: detect lock events without corresponding mint events
        alerts = []
        for correlation_id, events in grouped_events.items():
            if events["source"] and not events["destination"]:
                for event in events["source"]:
                    lock_event = self.pick_first(events["source"])
                    alerts.append(self.create_detection_alert(
                        signature_type=SignatureType.LOCK_WITHOUT_MINT,
                        severity=AlertSeverity.LOW,
                        bridge=bridge,
                        correlation_id=correlation_id,
                        correlation_type=lock_event.correlation_type,
                        src_event_id=lock_event.id,
                        dst_event_id=None,
                        title=f"{bridge}: lock event without corresponding mint event",
                        description=(
                            f"Found lock event {lock_event.event_type} with "
                            f"correlation_id={correlation_id}, but no matching mint event."
                        ),
                        created_at_ts=lock_event.timestamp,
                    ))
        return alerts

    def mint_without_lock(self, bridge: str) -> list[DetectionAlert]:
        grouped_events = self.fetch_event_pairs(bridge, BRIDGE_EVENT_MAP[bridge].mint, BRIDGE_EVENT_MAP[bridge].lock)
        # 4: detect mint events without corresponding lock events
        alerts = []
        for correlation_id, events in grouped_events.items():
            if events["source"] and not events["destination"]:
                for event in events["source"]:
                    mint_event = self.pick_first(events["source"])
                    alerts.append(self.create_detection_alert(
                        signature_type=SignatureType.MINT_WITHOUT_LOCK,
                        severity=AlertSeverity.LOW,
                        bridge=bridge,
                        correlation_id=correlation_id,
                        correlation_type=mint_event.correlation_type,
                        src_event_id=None,
                        dst_event_id=mint_event.id,
                        title=f"{bridge}: mint event without corresponding lock event",
                        description=(
                            f"Found mint event {mint_event.event_type} with "
                            f"correlation_id={correlation_id}, but no matching lock event."
                        ),
                        created_at_ts=mint_event.timestamp,
                    ))
        return alerts

    def over_mint(self, bridge: str) -> list[DetectionAlert]:
        grouped_events = self.fetch_event_pairs(bridge, BRIDGE_EVENT_MAP[bridge].lock, BRIDGE_EVENT_MAP[bridge].mint)
        alerts = []
        for correlation_id, events in grouped_events.items():
            if not events["destination"] or not events["source"]:
                continue
            for mint_event in events["destination"]:
                for lock_event in events["source"]:
                    if mint_event.amount_out is not None and lock_event.amount_out is not None and mint_event.amount_out > lock_event.amount_out:
                        alerts.append(self.create_detection_alert(
                            signature_type=SignatureType.OVER_MINT,
                            severity=AlertSeverity.LOW,
                            bridge=bridge,
                            correlation_id=correlation_id,
                            correlation_type=lock_event.correlation_type,
                            src_event_id=lock_event.id,
                            dst_event_id=mint_event.id,
                            title=f"{bridge}: over-mint detected",
                            description=(
                                f"Found mint event {mint_event.event_type} with amount {mint_event.amount_out} "
                                f"which is greater than the corresponding lock event {lock_event.event_type} "
                                f"with amount {lock_event.amount_out} for correlation_id={correlation_id}."
                            ),
                            created_at_ts=mint_event.timestamp,
                        ))
        return alerts

    def over_release(self, bridge: str) -> list[DetectionAlert]:
        grouped_events = self.fetch_event_pairs(bridge, BRIDGE_EVENT_MAP[bridge].burn, BRIDGE_EVENT_MAP[bridge].release)
        alerts = []
        for correlation_id, events in grouped_events.items():
            if not events["destination"] or not events["source"]:
                continue
            for release_event in events["destination"]:
                for burn_event in events["source"]:
                    if release_event.amount_out is not None and burn_event.amount_out is not None and release_event.amount_out > burn_event.amount_out:
                        alerts.append(self.create_detection_alert(
                            signature_type=SignatureType.OVER_RELEASE,
                            severity=AlertSeverity.LOW,
                            bridge=bridge,
                            correlation_id=correlation_id,
                            correlation_type=burn_event.correlation_type,
                            src_event_id=burn_event.id,
                            dst_event_id=release_event.id,
                            title=f"{bridge}: over-release detected",
                            description=(
                                f"Found release event {release_event.event_type} with amount {release_event.amount_out} "
                                f"which is greater than the corresponding burn event {burn_event.event_type} "
                                f"with amount {burn_event.amount_out} for correlation_id={correlation_id}."
                            ),
                            created_at_ts=release_event.timestamp,
                        ))
        return alerts

    def proof_replay(self, bridge: str, source: NormalizedEventType, destination: NormalizedEventType) -> list[DetectionAlert]:
        grouped_events = self.fetch_event_pairs(bridge, source, destination)
        # check if the same lock event is used for multiple mint events (potential proof replay attack)
        alerts = []
        for correlation_id, events in grouped_events.items():
            if len(events["source"]) == 1 and len(events["destination"]) > 1:

                # #######################################################################################
                # TODO: check if it's possible to have multiple locks and multiple mints for the same id,
                # and still be in normal behaviour
                # #######################################################################################
                
                lock_event = self.pick_first(events["source"])
                mint_events = events["destination"]
                for mint_event in mint_events:
                    alerts.append(self.create_detection_alert(
                        signature_type=SignatureType.PROOF_REPLAY,
                        severity=AlertSeverity.LOW,
                        bridge=bridge,
                        correlation_id=correlation_id,
                        correlation_type=lock_event.correlation_type,
                        src_event_id=lock_event.id,
                        dst_event_id=mint_event.id,
                        title=f"{bridge}: potential proof replay attack detected",
                        description=(
                            f"Found multiple mint / release events corresponding to the same lock / burn event {lock_event.event_type} "
                            f"with correlation_id={correlation_id}, which may indicate a proof replay attack."
                        ),
                        created_at_ts=mint_event.timestamp,
                    ))
        return alerts

    def check_replays(self, bridge: str, source: NormalizedEventType, destination: NormalizedEventType) -> list[DetectionAlert]:
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
                _safe_get(event, "correlation_type"),
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
                        correlation_type=source_event.correlation_type,
                        src_event_id=source_event.id,
                        dst_event_id=dst_event.id,
                        title=f"{bridge}: replay-like repeated execution across multiple destination transactions",
                        description=(
                            f"Found multiple destination events for correlation_id={correlation_id} "
                            f"spread across different transaction hashes "
                            f"{sorted([h for h in dst_tx_hashes if h is not None])}. "
                            f"This suggests the same lock/burn may have been consumed more than once."
                        ),
                        created_at_ts=dst_event.timestamp,
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
                            correlation_type=source_event.correlation_type,
                            src_event_id=source_event.id,
                            dst_event_id=dst_event.id,
                            title=f"{bridge}: inconsistent replay payload detected",
                            description=(
                                f"Found multiple destination events for correlation_id={correlation_id} "
                                f"with different logical payloads (amount / recipient / token / chain context differ). "
                                f"This is stronger evidence of replay, mutation, or malformed processing."
                            ),
                            created_at_ts=dst_event.timestamp,
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
                        correlation_type=source_event.correlation_type,
                        src_event_id=source_event.id,
                        dst_event_id=dst_event.id,
                        title=f"{bridge}: duplicate destination event for same correlation_id",
                        description=(
                            f"Found repeated destination events with identical payload for "
                            f"correlation_id={correlation_id}. This can be benign duplication, "
                            f"but may also indicate replay or duplicate ingestion."
                        ),
                        created_at_ts=dst_event.timestamp,
                    )
                    )

        return alerts

