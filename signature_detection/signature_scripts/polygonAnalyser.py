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
from db.repository.transfer_events.transfer_events_repository import (
    PolygonTransferRepository,
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

    def fetch_blockchain_transactions(self):
        return PolygonBlockchainTransactionRepository.get_all()

    def analyse_bridge_specific_signatures(self) -> list[DetectionAlert]:
        alerts = []
        alerts.extend(self.state_synced_contract_authorization())
        alerts.extend(self.token_mappings())
        alerts.extend(self.token_contract_attacks())
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
            add_alert(
                event, extra_data.get("root_token"), extra_data.get("child_token") or event.token_in
            )

        return alerts

    # token contract attacks:
    def _check_locked_token_native(self, event, tx) -> list[str]:
        """token contract checks regarding native tokens"""
        invalid_fields = []

        # 1) verificar se o "value" da transação é o mesmo do receipt.quantity
        if tx is None or tx.value != event.amount_in:
            invalid_fields.append(
                "1) tx.value does not match locked amount "
                f"(tx.value={getattr(tx, 'value', '<missing>')}, amount={event.amount_in})"
            )

        # 2) verificar se o receipt.mainchain.tokenAddr é o contract oficial da bridge
        if str(event.address).lower() != self.POLYGON_NATIVE_BRIDGE_CONTRACT:
            invalid_fields.append(
                "2) LockedToken contract is not the official native bridge "
                f"(contract={event.contract_address or '<missing>'}, "
                f"expected={self.POLYGON_NATIVE_BRIDGE_CONTRACT})"
            )

        # 3) verificar se o status é success
        if str(event.status) != "1":
            invalid_fields.append(
                f"3) transaction status is not success (status={event.status or '<missing>'})"
            )

        return invalid_fields

    def _check_locked_token_erc20(self, event, transfers) -> list[str]:
        """token contract checks regarding ERC20 tokens"""
        invalid_fields = []

        # 0) Verificar se houve transfer event nesta transação
        if not transfers:
            return ["0) no ERC20 Transfer event found in the LockedToken transaction"]

        matching_transfers = [
            transfer
            for transfer in transfers
            if str(transfer.token_address).lower() == str(event.token_in).lower()
            and str(transfer.to_address).lower() == str(event.contract_address).lower()
            and str(transfer.from_address).lower() == str(event.actor_from).lower()
            and transfer.amount == event.amount_in
        ]
        if matching_transfers:
            return invalid_fields

        token_transfers = [
            transfer
            for transfer in transfers
            if str(transfer.token_address).lower() == str(event.token_in).lower()
        ]

        # 1) verificar se o transfer.to é o address do token
        if not any(
            str(transfer.to_address).lower() == str(event.contract_address).lower()
            for transfer in token_transfers
        ):
            invalid_fields.append(
                "1) no token Transfer to the LockedToken contract "
                f"(expected_to={event.contract_address or '<missing>'})"
            )

        # 2) verificar se o transfer.from é quem fez o lockedERC20
        if not any(
            str(transfer.from_address).lower() == str(event.actor_from).lower()
            for transfer in token_transfers
        ):
            invalid_fields.append(
                "2) no token Transfer from the LockedToken depositor "
                f"(expected_from={event.actor_from or '<missing>'})"
            )

        # 3) verificar se transfer.value é igual ao receipt.info.quantity
        if not any(transfer.amount == event.amount_in for transfer in token_transfers):
            invalid_fields.append(
                "3) no token Transfer amount matches the LockedToken amount "
                f"(expected_amount={event.amount_in})"
            )

        if not invalid_fields:
            invalid_fields.append(
                "1) 2) 3) no single token Transfer matches all LockedToken checks"
            )

        return invalid_fields

    '''
    def token_contract_attacks(self) -> list[DetectionAlert]:
        """
        For lock/burn events
        1)
            a) se for native token,
                1) verificar se o "value" da transação é o mesmo do receipt.quantity (event amount provavelmente)
                2) verificar se o receipt.mainchain.tokenAddr (campo "address" da row deste evento) é o contract oficial da bridge (0x8484Ef722627bf18ca5Ae6BcF031c23E6e922B30)
                3) verificar se o status é success (?)
            b) se for token ERC20
                0) Verificar se houve transfer event nesta transação, senão alert
                1) verificar se o transfer.to é o address do token ([DepositRequested].receipt.mainchain.tokenAddr, ou seja, campo "address" da row do evento lockedERC20)
                2) verificar se o transfer.from é o [DepositRequested].receipt.mainchain.addr, ou seja, quem fez o lockedERC20 (column depositor no evento lockederc20)
                3) verificar se transfer.value é igual ao [DepositRequested].receipt.info.quantity (coluna amount do evento lockedERC20)

                [importante] no caso de haver mais que um transfer event, é possivel que tenha havido chained transfers, por isso temos que seguir o caminho e verificar se tudo bate certo (mais que um transfer pode não significar que houve ataque, pode ter havido A->B->C->lock/burn)

        """

        alerts: list[DetectionAlert] = []

        # 1 - fetch lock/burn events - lockedToken only for now, and corresponding transaction
        # TODO: add the remaining lock/burn event types after LockedToken checks are covered.
        locked_events = NormalizedEventRepository.get_events_by_event_type(
            NormalizedEventType.LOCKED_TOKEN,
            self.bridge,
        )
        txs_by_hash = {
            tx.transaction_hash: tx
            for tx in PolygonBlockchainTransactionRepository.get_all()
            if tx.transaction_hash is not None
        }
        transfers_by_tx: dict[str, list] = {}
        for transfer in PolygonTransferRepository.get_all():
            transfers_by_tx.setdefault(transfer.transaction_hash, []).append(transfer)

        # 2 - for each event, check if it's native or ERC20 token (root token is 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2)
        for event in locked_events:
            tx = txs_by_hash.get(event.transaction_hash)
            if str(event.token_in).lower() == self.POLYGON_NATIVE_ROOT_TOKEN:
                invalid_fields = self._check_locked_token_native(event, tx)
            else:
                invalid_fields = self._check_locked_token_erc20(
                    event,
                    transfers_by_tx.get(event.transaction_hash, []),
                )

            if not invalid_fields:
                continue

            correlation_id = event.correlation_id or event.transaction_hash or str(event.raw_pk)
            alerts.append(
                self.create_detection_alert(
                    signature_type=SignatureType.CONTRACT_MISMATCH,
                    severity=AlertSeverity.HIGH,
                    bridge=self.bridge,
                    correlation_id=correlation_id,
                    correlation_type="locked_token_contract_attack",
                    src_event_id=event.id,
                    dst_event_id=None,
                    title="polygon: LockedToken failed token contract checks",
                    description=(
                        f"Found LockedToken event with correlation_id={correlation_id}. "
                        f"Invalid token contract fields: {'; '.join(invalid_fields)}."
                    ),
                    created_at_ts=event.timestamp,
                    probability="TODO",
                )
            )

        return alerts
    '''
