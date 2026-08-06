from db.repository.detection_alert.detection_alert_model import DetectionAlert
from db.repository.blockchain_transactions.blockchain_transactions_repository import (
    MeterIoBlockchainTransactionRepository,
)

from .analyser import Analyser


class MeterIoAnalyser(Analyser):
    def __init__(self):
        super().__init__("meter.io")

    def fetch_blockchain_transactions(
        self, start_ts: int | None = None, end_ts: int | None = None
    ):
        return MeterIoBlockchainTransactionRepository.get_by_time_window(start_ts, end_ts)

    def fetch_latest_transaction_timestamp(self, start_ts: int | None = None):
        return MeterIoBlockchainTransactionRepository.get_latest_timestamp(start_ts)

    def analyse_bridge_specific_signatures(self) -> list[DetectionAlert]:
        # TODO: implement Meter.io-specific signatures.
        return []
