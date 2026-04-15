from db.repository.blockchain_transactions.blockchain_transactions_repository import MayanBlockchainTransactionRepository
from db.repository.cross_chain_transactions.cross_chain_transactions_repository import MayanCrossChainTransactionRepository

from .analyser import Analyser
from db.repository.detection_alert.detection_alert_model import DetectionAlert

class MayanAnalyser(Analyser):
    def __init__(self):
        super().__init__("mayan")
    
    def fetch_blockchain_transactions(self):
        return MayanBlockchainTransactionRepository.get_all()
        
    def fetch_crosschain_transactions(self):
        return MayanCrossChainTransactionRepository.get_all()