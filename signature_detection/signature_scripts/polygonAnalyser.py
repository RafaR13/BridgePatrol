import json
from datetime import datetime, timedelta, timezone

from db.repository.blockchain_transactions.blockchain_transactions_repository import (
    PolygonBlockchainTransactionRepository,
)
from db.repository.normalized_event.normalized_event_repository import (
    NormalizedEventRepository,
)
from db.repository.polygon_token_mapping.polygon_token_mapping_repository import (
    PolygonTokenMappingRepository,
)
from helpers.polygon_root_chain_manager import (
    get_root_chain_manager_contract,
    get_rpc_url,
    resolve_child_token,
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

    def analyse_bridge_specific_signatures(self) -> list[DetectionAlert]:
        alerts = []
        alerts.extend(self.state_synced_contract_authorization())
        alerts.extend(self.token_mappings())
        return alerts

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

    def token_mappings(self) -> list[DetectionAlert]:
        """Checks root token and child token pairs, and checks if the mapping is correct based on polygon_token_mappings table"""
        alerts: list[DetectionAlert] = []
        mappings = PolygonTokenMappingRepository.get_all_by_root_token()
        contract = None

        stale_before = datetime.now(timezone.utc) - timedelta(days=365)

        def checked_at_dt(mapping) -> datetime | None:
            if not mapping.checked_at:
                return None
            checked_at = mapping.checked_at
            if checked_at.tzinfo:
                return checked_at.astimezone(timezone.utc)
            return checked_at.replace(tzinfo=timezone.utc)

        def severity_for(mapping) -> AlertSeverity:
            checked_at = checked_at_dt(mapping)
            if checked_at is not None and checked_at < stale_before:
                return AlertSeverity.MEDIUM
            return AlertSeverity.HIGH

        def add_alert(event, root_token, child_token):
            nonlocal contract

            if not root_token or not child_token:
                return

            normalized_root_token = str(root_token).lower()
            mapping = mappings.get(normalized_root_token)
            if mapping is None or mapping.child_token is None:
                if contract is None:
                    contract = get_root_chain_manager_contract(get_rpc_url(None))

                checked_at = datetime.now(timezone.utc)
                official_child_token = resolve_child_token(contract, normalized_root_token)
                mapping = PolygonTokenMappingRepository.upsert(
                    normalized_root_token,
                    official_child_token,
                    checked_at,
                )
                mappings[normalized_root_token] = mapping

            expected_child_token = mapping.child_token if mapping else None
            if expected_child_token and str(expected_child_token).lower() == str(child_token).lower():
                return

            checked_at = mapping.checked_at.isoformat() if mapping and mapping.checked_at else "<missing>"
            correlation_id = event.correlation_id or str(event.raw_pk)
            alerts.append(
                self.create_detection_alert(
                    signature_type=SignatureType.CONTRACT_MISMATCH,
                    severity=severity_for(mapping) if mapping else AlertSeverity.HIGH,
                    bridge=self.bridge,
                    correlation_id=correlation_id,
                    correlation_type="polygon_token_mapping",
                    src_event_id=event.id,
                    dst_event_id=None,
                    title="polygon: token mapping does not match canonical mapping",
                    description=(
                        f"Found {event.event_type} event with correlation_id={correlation_id}. "
                        f"root_token={root_token}, child_token={child_token}, "
                        f"expected_child_token={expected_child_token or '<missing>'}, "
                        f"mapping_checked_at={checked_at}."
                    ),
                    created_at_ts=event.timestamp,
                    probability="TODO",
                )
            )

        for event in NormalizedEventRepository.get_events_by_event_type(
            NormalizedEventType.TOKEN_DEPOSITED,
            self.bridge,
        ):
            add_alert(event, event.token_in, event.token_out)

        for event in NormalizedEventRepository.get_events_by_event_type(
            NormalizedEventType.CHILD_TOKEN_BURN,
            self.bridge,
        ):
            if not event.extra_data:
                continue
            try:
                extra_data = json.loads(event.extra_data)
            except (TypeError, json.JSONDecodeError):
                continue
            add_alert(event, extra_data.get("root_token"), extra_data.get("child_token") or event.token_in)

        return alerts
