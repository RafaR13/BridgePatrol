from db.repository.blockchain_transactions.blockchain_transactions_repository import (
    AcrossBlockchainTransactionRepository,
)

from .analyser import Analyser
from db.repository.detection_alert.detection_alert_model import DetectionAlert


class AcrossAnalyser(Analyser):
    def __init__(self):
        super().__init__("across")

    def fetch_blockchain_transactions(self):
        return AcrossBlockchainTransactionRepository.get_all()

    def analyse_bridge_specific_signatures(self) -> list[DetectionAlert]:
        return []
