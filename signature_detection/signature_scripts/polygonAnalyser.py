import json

from db.repository.blockchain_transactions.blockchain_transactions_repository import PolygonBlockchainTransactionRepository
from db.repository.cross_chain_transactions.cross_chain_transactions_repository import PolygonCrossChainTransactionRepository
from db.repository.normalized_event.normalized_event_repository import (
    NormalizedEventRepository,
)
from normalization.event_types import NormalizedEventType
from signature_detection.constants import (
    POLYGON_POS_CORE,
    AlertSeverity,
    SignatureType,
)

from .analyser import Analyser
from db.repository.detection_alert.detection_alert_model import DetectionAlert


class PolygonAnalyser(Analyser):
    def __init__(self):
        super().__init__("polygon")

    def fetch_blockchain_transactions(self):
        return PolygonBlockchainTransactionRepository.get_all()

    def fetch_crosschain_transactions(self):
        return PolygonCrossChainTransactionRepository.get_all()

    def analyse_bridge_specific_signatures(self) -> list[DetectionAlert]:
        return self.state_synced_contract_authorization()

    def _state_synced_payload_contract_address(self, event):
        if event.actor_to:
            return event.actor_to
        if not event.extra_data:
            return None
        try:
            extra_data = json.loads(event.extra_data)
        except (TypeError, json.JSONDecodeError):
            return None
        return extra_data.get("contract_address")

    def _is_expected_address(self, actual, expected: tuple[str, ...]) -> bool:
        if not actual:
            return False
        return str(actual).lower() in {address.lower() for address in expected}

    def state_synced_contract_authorization(self) -> list[DetectionAlert]:
        alerts: list[DetectionAlert] = []
        state_sender = POLYGON_POS_CORE["state_sender"]
        child_chain_manager_proxy = POLYGON_POS_CORE["child_chain_manager_proxy"]

        events = NormalizedEventRepository.get_events_by_event_type(
            NormalizedEventType.STATE_SYNCED,
            self.bridge,
        )

        for event in events:
            event_address = event.contract_address
            payload_contract_address = self._state_synced_payload_contract_address(event)
            invalid_fields = []

            if not self._is_expected_address(event_address, state_sender):
                invalid_fields.append(
                    "address="
                    f"{event_address or '<missing>'}; expected one of: "
                    f"{', '.join(state_sender)}"
                )

            if not self._is_expected_address(
                payload_contract_address,
                child_chain_manager_proxy,
            ):
                invalid_fields.append(
                    "contract_address="
                    f"{payload_contract_address or '<missing>'}; expected one of: "
                    f"{', '.join(child_chain_manager_proxy)}"
                )

            if not invalid_fields:
                continue

            correlation_id = event.correlation_id or str(event.raw_pk)
            alerts.append(
                self.create_detection_alert(
                    signature_type=SignatureType.UNAUTHORIZED_CONTRACT,
                    severity=AlertSeverity.HIGH,
                    bridge=self.bridge,
                    correlation_id=correlation_id,
                    correlation_type="state_synced_core_contracts",
                    src_event_id=event.id,
                    dst_event_id=None,
                    title="polygon: StateSynced emitted by unauthorized core contract",
                    description=(
                        f"Found StateSynced event with correlation_id={correlation_id}. "
                        f"Invalid Polygon core contract fields: {'; '.join(invalid_fields)}."
                    ),
                    created_at_ts=event.timestamp,
                    probability="TODO",
                )
            )

        return alerts
