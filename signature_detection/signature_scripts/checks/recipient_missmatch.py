from __future__ import annotations

from db.repository.detection_alert.detection_alert_model import DetectionAlert
from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from signature_detection.constants import AlertSeverity, SignatureType


class RecipientMissmatchMixin:
    def _pick_recipient_event(self, events: list[NormalizedEvent]) -> NormalizedEvent | None:
        for event in events:
            if event.actor_to is not None and (
                event.amount_out is not None or event.amount_in is not None
            ):
                return event
        return None

    def recipient_mismatch(self, bridge: str) -> list[DetectionAlert]:
        print("starting analysis for recipient_mismatch")
        alerts = []

        for flow_type in ("deposits", "withdrawals"):
            for flow in self._configured_flows(bridge, flow_type):
                grouped_events = self.fetch_event_pairs(bridge, flow)
                for correlation_id, events in grouped_events.items():
                    if not events["destination"] or not events["source"]:
                        continue

                    source_event = self._pick_recipient_event(events["source"])
                    destination_event = self._pick_recipient_event(events["destination"])
                    if source_event is None or destination_event is None:
                        continue

                    source_recipient = self._normalized_value(source_event.actor_to)
                    destination_recipient = self._normalized_value(destination_event.actor_to)
                    if (
                        source_recipient is None
                        or destination_recipient is None
                        or source_recipient == destination_recipient
                    ):
                        continue

                    alerts.append(
                        self.create_detection_alert(
                            signature_type=SignatureType.RECIPIENT_MISMATCH,
                            severity=AlertSeverity.HIGH,
                            bridge=bridge,
                            correlation_id=correlation_id,
                            correlation_type=flow.name,
                            src_event_id=source_event.id,
                            dst_event_id=destination_event.id,
                            title=f"{bridge}: recipient mismatch detected",
                            description=(
                                f"Found source event {source_event.event_type} with recipient "
                                f"{source_event.actor_to} and destination event "
                                f"{destination_event.event_type} with recipient "
                                f"{destination_event.actor_to} for correlation_id={correlation_id}. "
                                f"Flow={flow.name}."
                            ),
                            created_at_ts=(
                                self._created_at_ts_for_event(destination_event)
                                or self._created_at_ts_for_event(source_event)
                            ),
                            probability="TODO",
                        )
                    )

        print(f"cought {len(alerts)} alerts")
        return alerts
