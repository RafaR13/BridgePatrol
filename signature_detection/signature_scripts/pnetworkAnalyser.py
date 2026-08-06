from db.repository.blockchain_transactions.blockchain_transactions_repository import (
    PNetworkBlockchainTransactionRepository,
)
from db.repository.detection_alert.detection_alert_model import DetectionAlert

from .analyser import Analyser


class PNetworkAnalyser(Analyser):
    def __init__(self):
        super().__init__("pnetwork")

    def fetch_blockchain_transactions(
        self, start_ts: int | None = None, end_ts: int | None = None
    ):
        return PNetworkBlockchainTransactionRepository.get_by_time_window(start_ts, end_ts)

    def fetch_latest_transaction_timestamp(self, start_ts: int | None = None):
        return PNetworkBlockchainTransactionRepository.get_latest_timestamp(start_ts)

    def analyse_bridge_specific_signatures(self) -> list[DetectionAlert]:
        return self.token_contract_attacks()

    def bridge_specific_signature_checks(self):
        return (
            ("token_contract_attacks", self.token_contract_attacks, ()),
        )
