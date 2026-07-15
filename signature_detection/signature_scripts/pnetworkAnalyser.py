from db.repository.blockchain_transactions.blockchain_transactions_repository import (
    PNetworkBlockchainTransactionRepository,
)
from db.repository.detection_alert.detection_alert_model import DetectionAlert

from .analyser import Analyser


class PNetworkAnalyser(Analyser):
    def __init__(self):
        super().__init__("pnetwork")

    def fetch_blockchain_transactions(self):
        return PNetworkBlockchainTransactionRepository.get_all()

    def analyse_bridge_specific_signatures(self) -> list[DetectionAlert]:
        return self.token_contract_attacks()

    def bridge_specific_signature_checks(self):
        return (
            ("token_contract_attacks", self.token_contract_attacks, ()),
        )
