from __future__ import annotations

from db.repository.detection_alert.detection_alert_model import DetectionAlert
from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from signature_detection.constants import AlertSeverity, SignatureType


class TokenChecksMixin:
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
        print("starting analysis for amount_mismatch")
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
                            created_at_ts=(
                                self._created_at_ts_for_event(destination_event)
                                or self._created_at_ts_for_event(source_event)
                            ),
                            probability="TODO",
                        )
                    )

        print(f"cought {len(alerts)} alerts")
        return alerts

    def over_mint(self, bridge: str) -> list[DetectionAlert]:
        print("starting analysis for over_mint")
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
                            created_at_ts=self._created_at_ts_for_event(mint_event),
                            probability="TODO",
                        )
                    )
        print(f"cought {len(alerts)} alerts")
        return alerts

    def over_release(self, bridge: str) -> list[DetectionAlert]:
        print("starting analysis for over_release")
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
                            created_at_ts=self._created_at_ts_for_event(release_event),
                            probability="TODO",
                        )
                    )
        print(f"cought {len(alerts)} alerts")
        return alerts
