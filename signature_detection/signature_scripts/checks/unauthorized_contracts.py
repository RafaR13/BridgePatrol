from __future__ import annotations

from db.repository.detection_alert.detection_alert_model import DetectionAlert
from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from signature_detection.constants import (
    VERIFIED_CONTRACTS,
    AlertSeverity,
    EventPairFlow,
    SignatureType,
)


class UnauthorizedContractsMixin:
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
        print("starting analysis for unauthorized_contracts")
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
                                    created_at_ts=self._created_at_ts_for_event(event),
                                    probability="TODO",
                                )
                            )

        print(f"cought {len(alerts)} alerts")
        return alerts
