from db.repository.blockchain_transactions.blockchain_transactions_repository import (
    NomadBlockchainTransactionRepository,
)
from db.repository.detection_alert.detection_alert_model import DetectionAlert

from .analyser import Analyser


class NomadAnalyser(Analyser):
    def __init__(self):
        super().__init__("nomad")

    def fetch_blockchain_transactions(
        self, start_ts: int | None = None, end_ts: int | None = None
    ):
        return NomadBlockchainTransactionRepository.get_by_time_window(start_ts, end_ts)

    def fetch_latest_transaction_timestamp(self, start_ts: int | None = None):
        return NomadBlockchainTransactionRepository.get_latest_timestamp(start_ts)

    def analyse_bridge_specific_signatures(self) -> list[DetectionAlert]:
        return []
