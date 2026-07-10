from db.repository.blockchain_transactions.blockchain_transactions_repository import (
    NomadBlockchainTransactionRepository,
)
from db.repository.detection_alert.detection_alert_model import DetectionAlert

from .analyser import Analyser


class NomadAnalyser(Analyser):
    def __init__(self):
        super().__init__("nomad")

    def fetch_blockchain_transactions(self):
        return NomadBlockchainTransactionRepository.get_all()

    def analyse_bridge_specific_signatures(self) -> list[DetectionAlert]:
        return []
