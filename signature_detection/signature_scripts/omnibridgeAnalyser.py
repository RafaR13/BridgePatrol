from db.repository.blockchain_transactions.blockchain_transactions_repository import OmnibridgeBlockchainTransactionRepository
from db.repository.cross_chain_transactions.cross_chain_transactions_repository import OmnibridgeCrossChainTransactionRepository

from .analyser import Analyser
from db.repository.detection_alert.detection_alert_model import DetectionAlert

class OmnibridgeAnalyser(Analyser):
    def __init__(self):
        super().__init__("omnibridge")
    
    def fetch_blockchain_transactions(self):
        return OmnibridgeBlockchainTransactionRepository.get_all()
        
    def fetch_crosschain_transactions(self):
        return OmnibridgeCrossChainTransactionRepository.get_all()