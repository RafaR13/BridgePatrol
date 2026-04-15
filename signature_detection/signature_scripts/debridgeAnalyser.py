from db.repository.blockchain_transactions.blockchain_transactions_repository import DeBridgeBlockchainTransactionRepository
from db.repository.cross_chain_transactions.cross_chain_transactions_repository import DeBridgeCrossChainTransactionRepository

from .analyser import Analyser
from db.repository.detection_alert.detection_alert_model import DetectionAlert

class DeBridgeAnalyser(Analyser):
    def __init__(self):
        super().__init__("DeBridge")
    
    def fetch_blockchain_transactions(self):
        return DeBridgeBlockchainTransactionRepository.get_all()
        
    def fetch_crosschain_transactions(self):
        return DeBridgeCrossChainTransactionRepository.get_all()