from db.repository.detection_alert.detection_alert_model import DetectionAlert

from .analyser import Analyser


class StargateAnalyser(Analyser):
    def __init__(self):
        super().__init__("stargate")

    def fetch_blockchain_transactions(
        self, start_ts: int | None = None, end_ts: int | None = None
    ):
        # TODO: implement the Stargate blockchain transaction repository.
        return []

    def analyse_bridge_specific_signatures(self) -> list[DetectionAlert]:
        # TODO: implement Stargate-specific signatures.
        return []
