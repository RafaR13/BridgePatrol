from db.repository.detection_alert.detection_alert_model import DetectionAlert
from db.repository.blockchain_transactions.blockchain_transactions_repository import (
    ThorchainBlockchainTransactionRepository,
)

from .analyser import Analyser


class ThorchainAnalyser(Analyser):
    def __init__(self):
        super().__init__("thorchain")

    def fetch_blockchain_transactions(
        self, start_ts: int | None = None, end_ts: int | None = None
    ):
        return ThorchainBlockchainTransactionRepository.get_by_time_window(start_ts, end_ts)

    def fetch_latest_transaction_timestamp(self, start_ts: int | None = None):
        return ThorchainBlockchainTransactionRepository.get_latest_timestamp(start_ts)

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

        total_timer = (
            self.evaluation_reporter.timer(
                "signature_detection_total_timer",
                {"bridge": self.bridge, "start_ts": start_ts, "end_ts": end_ts},
            )
            if self.evaluation_reporter is not None
            else None
        )

        from contextlib import nullcontext

        with total_timer if total_timer is not None else nullcontext({}):
            # Source transaction / token consistency checks.
            alerts.extend(
                self._run_signature_check(
                    "token_contract_attacks",
                    self.token_contract_attacks,
                )
            )

            # Source traces can still reveal CREATE/CREATE2/SELFDESTRUCT operations.
            alerts.extend(
                self._run_signature_check(
                    "source_trace_operations",
                    self.analyse_source_trace_operations,
                )
            )

            # Extension point for Thorchain source-only signatures.
            for check_name, check_fn, check_args in self.bridge_specific_signature_checks():
                alerts.extend(self._run_signature_check(check_name, check_fn, *check_args))

        if self.evaluation_reporter is not None:
            self.evaluation_reporter.write(
                "signature_detection_summary",
                {
                    "bridge": self.bridge,
                    "start_ts": start_ts,
                    "end_ts": end_ts,
                    "alerts_detected": len(alerts),
                },
            )
        return alerts
