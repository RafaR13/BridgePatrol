from __future__ import annotations

from db.repository.detection_alert.detection_alert_model import DetectionAlert
from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from normalization.event_types import NormalizedEventType
from signature_detection.constants import AlertSeverity, EventPairFlow, SignatureType


class DetectReplaysMixin:
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
