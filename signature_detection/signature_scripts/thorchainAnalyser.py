from db.repository.detection_alert.detection_alert_model import DetectionAlert

from .analyser import Analyser


class ThorchainAnalyser(Analyser):
    def __init__(self):
        super().__init__("thorchain")

    def fetch_blockchain_transactions(self):
        # TODO: fetch manually inserted Thorchain blockchain transactions.
        return []

    def analyse_bridge_specific_signatures(self) -> list[DetectionAlert]:
        # TODO: validate source vault, memo, asset and amount semantics.
        return []

    def analyse_source_trace_operations(self) -> list[DetectionAlert]:
        alerts: list[DetectionAlert] = []
        for tx in self._analysis_blockchain_transactions():
            calls = self._calls_from_trace(getattr(tx, "calls", None))
            call_frames = self._transaction_root_frames(tx)
            call_frames.extend(self._iter_trace_calls(calls))
            if call_frames:
                alerts.extend(self._check_dangerous_trace_operations(tx, call_frames))
        return alerts

    def analyse_all(
        self,
        start_ts: int | None = None,
        end_ts: int | None = None,
    ) -> list[DetectionAlert]:
        """
        Run only checks that can be evaluated from Thorchain source-side data.

        Destination events and transactions are intentionally unavailable, so
        missing pairs, cross-chain payload comparisons, destination callers,
        and replay checks must not produce alerts for this bridge.
        """
        self._set_analysis_window(start_ts=start_ts, end_ts=end_ts)
        alerts: list[DetectionAlert] = []

        # Source transaction / token consistency checks.
        alerts.extend(self.token_contract_attacks())

        # Source traces can still reveal CREATE/CREATE2/SELFDESTRUCT operations.
        alerts.extend(self.analyse_source_trace_operations())

        # This currently contains no checks, but is the extension point for
        # Thorchain source-only signatures (vault, memo, asset, etc.).
        alerts.extend(self.analyse_bridge_specific_signatures())
        return alerts
