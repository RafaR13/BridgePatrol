from db.repository.blockchain_transactions.blockchain_transactions_repository import (
    MayanBlockchainTransactionRepository,
)

from .analyser import Analyser
from db.repository.detection_alert.detection_alert_model import DetectionAlert


class MayanAnalyser(Analyser):
    def __init__(self):
        super().__init__("mayan")

    def fetch_blockchain_transactions(
        self, start_ts: int | None = None, end_ts: int | None = None
    ):
        return MayanBlockchainTransactionRepository.get_by_time_window(start_ts, end_ts)

    def fetch_latest_transaction_timestamp(self, start_ts: int | None = None):
        return MayanBlockchainTransactionRepository.get_latest_timestamp(start_ts)

    def analyse_bridge_specific_signatures(self) -> list[DetectionAlert]:
        return []
