from db.repository.blockchain_transactions.blockchain_transactions_repository import CCTPBlockchainTransactionRepository
from db.repository.cross_chain_transactions.cross_chain_transactions_repository import CCTPCrossChainTransactionRepository

from .analyser import Analyser
from db.repository.detection_alert.detection_alert_model import DetectionAlert

class CCTPAnalyser(Analyser):
    def __init__(self):
        super().__init__("cctp")
    
    def fetch_blockchain_transactions(self):
        return CCTPBlockchainTransactionRepository.get_all()
        
    def fetch_crosschain_transactions(self):
        return CCTPCrossChainTransactionRepository.get_all()