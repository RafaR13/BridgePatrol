from db.repository.blockchain_transactions.blockchain_transactions_repository import CCIPBlockchainTransactionRepository
from db.repository.cross_chain_transactions.cross_chain_transactions_repository import CCIPCrossChainTransactionRepository

from .analyser import Analyser
from db.repository.detection_alert.detection_alert_model import DetectionAlert

class CCIPAnalyser(Analyser):
    def __init__(self):
        super().__init__("ccip")
    
    def fetch_blockchain_transactions(self):
        return CCIPBlockchainTransactionRepository.get_all()
        
    def fetch_crosschain_transactions(self):
        return CCIPCrossChainTransactionRepository.get_all()