from db.repository.blockchain_transactions.blockchain_transactions_repository import PolygonBlockchainTransactionRepository
from db.repository.cross_chain_transactions.cross_chain_transactions_repository import PolygonCrossChainTransactionRepository

from .analyser import Analyser
from db.repository.detection_alert.detection_alert_model import DetectionAlert

class PolygonAnalyser(Analyser):
    def __init__(self):
        super().__init__("polygon")
    
    def fetch_blockchain_transactions(self):
        return PolygonBlockchainTransactionRepository.get_all()
        
    def fetch_crosschain_transactions(self):
        return PolygonCrossChainTransactionRepository.get_all()