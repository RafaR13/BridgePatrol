from db.repository.detection_alert.detection_alert_model import DetectionAlert
from db.repository.blockchain_transactions.blockchain_transactions_repository import (
    QubitBlockchainTransactionRepository,
)
from db.repository.cross_chain_transactions.cross_chain_transactions_repository import (
    QubitCrossChainTransactionRepository,
)

from .analyser import Analyser


class QubitAnalyser(Analyser):
    def __init__(self):
        super().__init__("qubit")

    def fetch_blockchain_transactions(
        self, start_ts: int | None = None, end_ts: int | None = None
    ):
        return QubitBlockchainTransactionRepository.get_by_time_window(start_ts, end_ts)

    def fetch_latest_transaction_timestamp(self, start_ts: int | None = None):
        return QubitBlockchainTransactionRepository.get_latest_timestamp(start_ts)

    def fetch_cross_chain_transactions(
        self, start_ts: int | None = None, end_ts: int | None = None
    ):
        return QubitCrossChainTransactionRepository.get_by_time_window(start_ts, end_ts)

    def analyse_bridge_specific_signatures(self) -> list[DetectionAlert]:
        return self.token_contract_attacks()

    def bridge_specific_signature_checks(self):
        return (("token_contract_attacks", self.token_contract_attacks, ()),)
