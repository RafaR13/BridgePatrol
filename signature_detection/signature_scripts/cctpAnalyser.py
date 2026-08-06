from db.repository.blockchain_transactions.blockchain_transactions_repository import (
    CCTPBlockchainTransactionRepository,
)
from db.repository.normalized_event.normalized_event_repository import (
    NormalizedEventRepository,
)
from db.repository.transfer_events.transfer_events_repository import (
    CCTPTransferRepository,
)
from normalization.event_types import NormalizedEventType
from signature_detection.constants import (
    AlertSeverity,
    SignatureType,
    VERIFIED_CONTRACTS,
)

from .analyser import Analyser
from db.repository.detection_alert.detection_alert_model import DetectionAlert


class CCTPAnalyser(Analyser):
    CCTP_NATIVE_TOKEN = "TODO"

    def __init__(self):
        super().__init__("cctp")

    def fetch_blockchain_transactions(
        self, start_ts: int | None = None, end_ts: int | None = None
    ):
        return CCTPBlockchainTransactionRepository.get_by_time_window(start_ts, end_ts)

    def fetch_latest_transaction_timestamp(self, start_ts: int | None = None):
        return CCTPBlockchainTransactionRepository.get_latest_timestamp(start_ts)

    def analyse_bridge_specific_signatures(self) -> list[DetectionAlert]:
        return self.token_contract_attacks()

    def bridge_specific_signature_checks(self):
        return (("token_contract_attacks", self.token_contract_attacks, ()),)

    def _normalized_value(self, value):
        if value is None:
            return None
        return str(value).lower()

    def _expected_source_contracts(self) -> tuple[str, ...]:
        return VERIFIED_CONTRACTS["cctp"]["burn_message"][
            NormalizedEventType.DEPOSIT_FOR_BURN
        ]

    def _check_deposit_for_burn_native_token(self, event, tx) -> list[str]:
        invalid_fields = []

        if str(event.status) != "1":
            invalid_fields.append(
                f"1) transaction status is not success (status={event.status or '<missing>'})"
            )

        expected_contracts = self._expected_source_contracts()
        event_contract = self._normalized_value(event.contract_address)
        if event_contract not in {contract.lower() for contract in expected_contracts}:
            invalid_fields.append(
                "2) DepositForBurn contract is not an expected CCTP source contract "
                f"(contract={event.contract_address or '<missing>'})"
            )

        if tx is None or tx.value != event.amount_in:
            invalid_fields.append(
                "3) tx.value does not match DepositForBurn amount "
                f"(tx.value={getattr(tx, 'value', '<missing>')}, amount={event.amount_in})"
            )

        return invalid_fields

    def _check_deposit_for_burn_erc20_token(self, event, transfers) -> list[str]:
        invalid_fields = []

        if str(event.status) != "1":
            invalid_fields.append(
                f"1) transaction status is not success (status={event.status or '<missing>'})"
            )

        expected_contracts = self._expected_source_contracts()
        event_contract = self._normalized_value(event.contract_address)
        if event_contract not in {contract.lower() for contract in expected_contracts}:
            invalid_fields.append(
                "2) DepositForBurn contract is not an expected CCTP source contract "
                f"(contract={event.contract_address or '<missing>'})"
            )

        if not transfers:
            invalid_fields.append("3) no ERC20 Transfer event found in the DepositForBurn transaction")
            return invalid_fields

        matching_transfers = [
            transfer
            for transfer in transfers
            if self._normalized_value(transfer.token_address)
            == self._normalized_value(event.token_in)
            and self._normalized_value(transfer.from_address)
            == self._normalized_value(event.actor_from)
            and self._normalized_value(transfer.to_address)
            == self._normalized_value(event.contract_address)
            and transfer.amount == event.amount_in
        ]
        if matching_transfers:
            return invalid_fields

        token_transfers = [
            transfer
            for transfer in transfers
            if self._normalized_value(transfer.token_address)
            == self._normalized_value(event.token_in)
        ]

        if not any(
            self._normalized_value(transfer.from_address)
            == self._normalized_value(event.actor_from)
            for transfer in token_transfers
        ):
            invalid_fields.append(
                "4) no token Transfer from the depositor "
                f"(expected_from={event.actor_from or '<missing>'})"
            )

        if not any(
            self._normalized_value(transfer.to_address)
            == self._normalized_value(event.contract_address)
            for transfer in token_transfers
        ):
            invalid_fields.append(
                "5) no token Transfer to the DepositForBurn contract "
                f"(expected_to={event.contract_address or '<missing>'})"
            )

        if not any(transfer.amount == event.amount_in for transfer in token_transfers):
            invalid_fields.append(
                "6) no token Transfer amount matches the DepositForBurn amount "
                f"(expected_amount={event.amount_in})"
            )

        if not invalid_fields:
            invalid_fields.append(
                "4) 5) 6) no single token Transfer matches all DepositForBurn checks"
            )

        return invalid_fields

    '''
    def token_contract_attacks(self) -> list[DetectionAlert]:
        alerts: list[DetectionAlert] = []

        events = NormalizedEventRepository.get_events_by_event_type(
            NormalizedEventType.DEPOSIT_FOR_BURN,
            self.bridge,
        )
        txs_by_hash = {
            tx.transaction_hash: tx
            for tx in CCTPBlockchainTransactionRepository.get_all()
            if tx.transaction_hash is not None
        }
        transfers_by_tx: dict[str, list] = {}
        for transfer in CCTPTransferRepository.get_all():
            transfers_by_tx.setdefault(transfer.transaction_hash, []).append(transfer)

        for event in events:
            if str(event.token_in).lower() == self.CCTP_NATIVE_TOKEN.lower():
                invalid_fields = self._check_deposit_for_burn_native_token(
                    event,
                    txs_by_hash.get(event.transaction_hash),
                )
            else:
                invalid_fields = self._check_deposit_for_burn_erc20_token(
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
                    correlation_type="cctp_token_contract_attack",
                    src_event_id=event.id,
                    dst_event_id=None,
                    title="cctp: DepositForBurn failed token contract checks",
                    description=(
                        f"Found DepositForBurn event with correlation_id={correlation_id}. "
                        f"Invalid token contract fields: {'; '.join(invalid_fields)}."
                    ),
                    created_at_ts=event.timestamp,
                    probability="TODO",
                )
            )

        return alerts
    '''
