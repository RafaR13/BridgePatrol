import json
from datetime import datetime, timedelta, timezone

from db.repository.blockchain_transactions.blockchain_transactions_repository import (
    PolygonBlockchainTransactionRepository,
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
    POLYGON_NATIVE_ROOT_TOKEN = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
    POLYGON_NATIVE_BRIDGE_CONTRACT = "0x8484ef722627bf18ca5ae6bcf031c23e6e922b30"

    def __init__(self):
        super().__init__("polygon")

    def fetch_blockchain_transactions(self, start_ts: int | None = None, end_ts: int | None = None):
        return PolygonBlockchainTransactionRepository.get_by_time_window(start_ts, end_ts)

    def fetch_latest_transaction_timestamp(self, start_ts: int | None = None):
        return PolygonBlockchainTransactionRepository.get_latest_timestamp(start_ts)

    def analyse_bridge_specific_signatures(self) -> list[DetectionAlert]:
        alerts = []
        alerts.extend(self.state_synced_contract_authorization())
        alerts.extend(self.token_mappings())
        alerts.extend(self.token_contract_attacks())
        return alerts

    def bridge_specific_signature_checks(self):
        return (
            (
                "state_synced_contract_authorization",
                self.state_synced_contract_authorization,
                (),
            ),
            ("token_mappings", self.token_mappings, ()),
            ("token_contract_attacks", self.token_contract_attacks, ()),
        )

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
        print("starting analysis for state_synced_contract_authorization")
        alerts: list[DetectionAlert] = []
        state_sender = POLYGON_POS_CORE["state_sender"]
        child_chain_manager_proxy = POLYGON_POS_CORE["child_chain_manager_proxy"]

        events = self._events_by_event_type(
            NormalizedEventType.STATE_SYNCED,
            self.bridge,
        )
        skipped_missing_address: set[str] = set()
        locked_token_tx_hashes = {
            event.transaction_hash
            for event in self._events_by_event_type(
                NormalizedEventType.LOCKED_TOKEN,
                self.bridge,
            )
            if event.transaction_hash
        }
        pos_deposit_txs_with_child_manager_state_sync = {
            event.transaction_hash
            for event in events
            if event.transaction_hash in locked_token_tx_hashes
            and self._is_expected_address(
                self._state_synced_payload_contract_address(event),
                child_chain_manager_proxy,
            )
        }
        alerted_pos_deposit_txs: set[str] = set()

        for event in events:
            event_address = event.contract_address
            payload_contract_address = self._state_synced_payload_contract_address(event)
            is_pos_deposit_state_sync = event.transaction_hash in locked_token_tx_hashes
            invalid_fields = []

            if self._normalized_value(event_address) is None:
                skipped_missing_address.add(self._event_analysis_key(event))
                self._debug(
                    "state_synced_contract_authorization: skip event missing "
                    f"contract_address id={event.id} tx={event.transaction_hash} "
                    f"cctx_id={event.cctx_id} correlation_id={event.correlation_id} "
                    f"payload_contract={payload_contract_address or '<missing>'}"
                )
                continue

            if not self._is_expected_address(event_address, state_sender):
                invalid_fields.append(
                    "address="
                    f"{event_address or '<missing>'}; expected one of: "
                    f"{', '.join(state_sender)}"
                )

            # StateSynced is a generic Polygon state-sync event. The emitter must be
            # StateSender, but the payload contract is the child-chain receiver and
            # can legitimately vary. A PoS deposit tx can emit multiple StateSynced
            # events; the invariant is that at least one of them targets
            # ChildChainManagerProxy, not that every StateSynced in that tx does.
            if (
                is_pos_deposit_state_sync
                and event.transaction_hash
                and event.transaction_hash not in pos_deposit_txs_with_child_manager_state_sync
                and event.transaction_hash not in alerted_pos_deposit_txs
            ):
                alerted_pos_deposit_txs.add(event.transaction_hash)
                invalid_fields.append(
                    "contract_address="
                    "no StateSynced event in this PoS deposit transaction targets "
                    f"one of: {', '.join(child_chain_manager_proxy)}"
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
                    created_at_ts=self._created_at_ts_for_event(event),
                    probability="TODO",
                )
            )
            print(
                "[state_synced_contract_authorization] "
                f"bridge={self.bridge} correlation_id={correlation_id} "
                f"event_id={event.id} tx_hash={event.transaction_hash} "
                f"event_type={event.event_type} "
                f"event_contract={event_address or '<missing>'} "
                f"payload_contract={payload_contract_address or '<missing>'} "
                f"is_pos_deposit_state_sync={is_pos_deposit_state_sync} "
                f"invalid_fields={'; '.join(invalid_fields)}"
            )

        if skipped_missing_address:
            print(
                "[state_synced_contract_authorization] "
                f"{len(skipped_missing_address)} cctx could not be analyzed for this "
                "check because the normalized event contract address is missing."
            )
        print(f"cought {len(alerts)} alerts")
        return alerts

    def token_mappings(self) -> list[DetectionAlert]:
        """Checks root token and child token pairs, and checks if the mapping is correct based on polygon_token_mappings table"""
        print("starting analysis for token_mappings")
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
            if (
                expected_child_token
                and str(expected_child_token).lower() == str(child_token).lower()
            ):
                return

            checked_at = (
                mapping.checked_at.isoformat() if mapping and mapping.checked_at else "<missing>"
            )
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
                    created_at_ts=self._created_at_ts_for_event(event),
                    probability="TODO",
                )
            )
            print(
                "[token_mappings] "
                f"bridge={self.bridge} correlation_id={correlation_id} "
                f"event_id={event.id} tx_hash={event.transaction_hash} "
                f"event_type={event.event_type} "
                f"root_token={root_token or '<missing>'} "
                f"child_token={child_token or '<missing>'} "
                f"expected_child_token={expected_child_token or '<missing>'} "
                f"mapping_checked_at={checked_at}"
            )

        for event in self._events_by_event_type(
            NormalizedEventType.TOKEN_DEPOSITED,
            self.bridge,
        ):
            add_alert(event, event.token_in, event.token_out)

        for event in self._events_by_event_type(
            NormalizedEventType.CHILD_TOKEN_BURN,
            self.bridge,
        ):
            if not event.extra_data:
                continue
            try:
                extra_data = json.loads(event.extra_data)
            except (TypeError, json.JSONDecodeError):
                continue
            add_alert(
                event, extra_data.get("root_token"), extra_data.get("child_token") or event.token_in
            )

        print(f"cought {len(alerts)} alerts")
        return alerts
