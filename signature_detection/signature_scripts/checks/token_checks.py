from __future__ import annotations

from dataclasses import dataclass

from db.repository.detection_alert.detection_alert_model import DetectionAlert
from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from signature_detection.constants import AlertSeverity, SignatureType


@dataclass(frozen=True)
class CctxAmountFields:
    source: tuple[str, ...]
    destination: tuple[str, ...]


CCTX_AMOUNT_FIELDS_BY_BRIDGE = {
    "across": CctxAmountFields(("input_amount",), ("output_amount",)),
    "debridge": CctxAmountFields(("input_amount",), ("output_amount",)),
    "mayan": CctxAmountFields(("input_amount",), ("output_amount",)),
    "meter.io": CctxAmountFields(("amount_in", "src_value"), ("amount_out",)),
    "pnetwork": CctxAmountFields(("amount_in", "src_value"), ("amount_out",)),
    "qubit": CctxAmountFields(("amount_in", "src_value"), ("amount_out",)),
    "thorchain": CctxAmountFields(("amount_in", "src_value"), ("amount_out",)),
}


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
        used_cctxs, alerts = self._cctx_amount_mismatch_alerts(bridge)
        if used_cctxs:
            print(f"cought {len(alerts)} alerts")
            return alerts

        alerts = self._event_amount_mismatch_alerts(bridge)
        print(f"cought {len(alerts)} alerts")
        return alerts

    def _event_amount_mismatch_alerts(self, bridge: str) -> list[DetectionAlert]:
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

        return alerts

    def _cctx_amount_mismatch_alerts(self, bridge: str) -> tuple[bool, list[DetectionAlert]]:
        amount_fields = CCTX_AMOUNT_FIELDS_BY_BRIDGE.get(bridge)
        if amount_fields is None:
            return False, []

        alerts = []
        found_comparable_cctx = False
        for cctx in self._analysis_cross_chain_transactions():
            source_amount = self._first_cctx_value(cctx, amount_fields.source)
            destination_amount = self._first_cctx_value(cctx, amount_fields.destination)
            if source_amount is None or destination_amount is None:
                continue

            found_comparable_cctx = True
            if source_amount == destination_amount:
                continue

            correlation_id = self._cctx_alert_correlation_id(bridge, cctx)
            source_token = getattr(cctx, "token_in", None)
            destination_token = getattr(cctx, "token_out", None)
            token_note = ""
            if (
                source_token is not None
                and destination_token is not None
                and str(source_token).lower() != str(destination_token).lower()
            ):
                token_note = f" Source token={source_token}; destination token={destination_token}."

            alerts.append(
                self.create_detection_alert(
                    signature_type=SignatureType.AMOUNT_MISMATCH,
                    severity=AlertSeverity.MEDIUM,
                    bridge=bridge,
                    correlation_id=correlation_id,
                    correlation_type="cross_chain_transaction",
                    src_event_id=None,
                    dst_event_id=None,
                    title=f"{bridge}: token amount mismatch detected",
                    description=(
                        f"Found CCTX {correlation_id} with source amount {source_amount} "
                        f"and destination amount {destination_amount}.{token_note}"
                    ),
                    created_at_ts=(
                        getattr(cctx, "dst_timestamp", None) or getattr(cctx, "src_timestamp", None)
                    ),
                    probability="TODO",
                )
            )

        return found_comparable_cctx, alerts

    def _first_cctx_value(self, cctx, fields: tuple[str, ...]):
        for field in fields:
            value = getattr(cctx, field, None)
            if value is not None:
                return value
        return None

    def _cctx_alert_correlation_id(self, bridge: str, cctx) -> str:
        for field in ("cctx_id", "intent_id", "correlation_id", "deposit_id", "id"):
            value = getattr(cctx, field, None)
            if value is not None:
                return str(value)
        return f"{bridge}:unknown_cctx"
