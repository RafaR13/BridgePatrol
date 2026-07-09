from db.repository.detection_alert.detection_alert_model import DetectionAlert
from db.repository.blockchain_transactions.blockchain_transactions_repository import (
    QubitBlockchainTransactionRepository,
)

from .analyser import Analyser


class QubitAnalyser(Analyser):
    def __init__(self):
        super().__init__("qubit")

    def fetch_blockchain_transactions(self):
        return QubitBlockchainTransactionRepository.get_all()

    def analyse_bridge_specific_signatures(self) -> list[DetectionAlert]:
        # TODO: implement Qubit-specific signatures.
        return []
