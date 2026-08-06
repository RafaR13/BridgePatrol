from db.repository.blockchain_transactions.blockchain_transactions_repository import (
    ChainSwapBlockchainTransactionRepository,
)
from db.repository.cross_chain_transactions.cross_chain_transactions_repository import (
    ChainSwapCrossChainTransactionRepository,
)
from db.repository.detection_alert.detection_alert_model import DetectionAlert

from .analyser import Analyser


class ChainSwapAnalyser(Analyser):
    def __init__(self):
        super().__init__("chainswap")

    def fetch_blockchain_transactions(
        self, start_ts: int | None = None, end_ts: int | None = None
    ):
        return ChainSwapBlockchainTransactionRepository.get_by_time_window(start_ts, end_ts)

    def fetch_latest_transaction_timestamp(self, start_ts: int | None = None):
        return ChainSwapBlockchainTransactionRepository.get_latest_timestamp(start_ts)

    def fetch_cross_chain_transactions(
        self, start_ts: int | None = None, end_ts: int | None = None
    ):
        return ChainSwapCrossChainTransactionRepository.get_by_time_window(start_ts, end_ts)

    def analyse_bridge_specific_signatures(self) -> list[DetectionAlert]:
        # TODO: add ChainSwap-specific contract/function/trace checks when the
        # bridge contracts and event semantics are fully documented.
        return []

    def analyse_all(
        self,
        start_ts: int | None = None,
        end_ts: int | None = None,
    ) -> list[DetectionAlert]:
        """
        Run checks that can work without normalized events.

        The current ChainSwap attack dataset has destination-side Receive()
        transactions only. Missing-pair detection must therefore inspect the
        cross-chain transaction table directly instead of normalized event pairs.
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
            alerts.extend(
                self._run_signature_check(
                    "incomplete_cross_chain_transactions",
                    self.incomplete_cross_chain_transactions,
                    self.bridge,
                )
            )

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
