from db.repository.detection_alert.detection_alert_model import DetectionAlert

from .analyser import Analyser


class MeterIoAnalyser(Analyser):
    def __init__(self):
        super().__init__("meter.io")

    def fetch_blockchain_transactions(self):
        # TODO: fetch manually inserted Meter.io blockchain transactions.
        return []

    def analyse_bridge_specific_signatures(self) -> list[DetectionAlert]:
        # TODO: implement Meter.io-specific signatures.
        return []
