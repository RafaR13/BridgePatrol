from db.repository.cross_chain_transactions.cross_chain_transactions_repository import RoninCrossChainTransactionRepository
from db.repository.detection_alert.detection_alert_model import DetectionAlert

def _fetch_cctxs(bridge: str):
    if bridge == "ronin":
        return RoninCrossChainTransactionRepository.get_all()
    else:
        raise ValueError(f"Bridge not supported: {bridge}")


def check_cctxs(bridge: str) -> list[DetectionAlert]:
    alerts = []
    return alerts