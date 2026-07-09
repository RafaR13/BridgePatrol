from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from db.repository.detection_alert.detection_alert_model import DetectionAlert
from evaluation.reporting import EvaluationReporter
from signature_detection.constants import (
    AlertSeverity,
    SignatureType,
)
from signature_detection.signature_scripts.checks.detect_replays import DetectReplaysMixin
from signature_detection.signature_scripts.checks.missing_event_pairs import (
    MissingEventPairsMixin,
)
from signature_detection.signature_scripts.checks.recipient_missmatch import (
    RecipientMissmatchMixin,
)
from signature_detection.signature_scripts.checks.token_checks import TokenChecksMixin
from signature_detection.signature_scripts.checks.token_contract_attacks import (
    TokenContractAttacksMixin,
)
from signature_detection.signature_scripts.checks.unauthorized_contracts import (
    UnauthorizedContractsMixin,
)

from signature_detection.signature_scripts.checks.check_event_callers import CheckEventCallersMixin
from signature_detection.signature_scripts.utils import AnalyserUtilsMixin


class Analyser(
    MissingEventPairsMixin,
    RecipientMissmatchMixin,
    TokenChecksMixin,
    UnauthorizedContractsMixin,
    DetectReplaysMixin,
    TokenContractAttacksMixin,
    CheckEventCallersMixin,
    AnalyserUtilsMixin,
    ABC,
):
    DEBUG = False
    DEBUG_TRANSACTION_HASH: str | None = None

    def __init__(self, bridge: str):
        self.bridge = bridge
        self._transaction_context: tuple[dict[str, int], dict[str, int]] | None = None
        self._analysis_start_ts: int | None = None
        self._analysis_end_ts: int | None = None
        self._analysis_has_time_filter = False
        self.evaluation_reporter: EvaluationReporter | None = None

    def _debug(self, message: str) -> None:
        if self.DEBUG:
            print(f"[signature-debug][{self.bridge}] {message}")

    @abstractmethod
    def fetch_blockchain_transactions(self):
        pass

    @abstractmethod
    def analyse_bridge_specific_signatures(self) -> List[DetectionAlert]:
        """Run checks that only apply to this bridge."""
        pass

    def bridge_specific_signature_checks(self):
        return (
            ("bridge_specific_signatures", self.analyse_bridge_specific_signatures, ()),
        )

    def analyse_all(
        self, start_ts: int | None = None, end_ts: int | None = None
    ) -> List[DetectionAlert]:
        """
        Run every configured analyser check and return a single alert list.
        """
        self._set_analysis_window(start_ts=start_ts, end_ts=end_ts)
        alerts: List[DetectionAlert] = []

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
            # Missing event pairs
            alerts.extend(self._run_signature_check("lock_without_mint", self.lock_without_mint, self.bridge))
            alerts.extend(self._run_signature_check("mint_without_lock", self.mint_without_lock, self.bridge))

            # Recipient Mismatch
            alerts.extend(self._run_signature_check("recipient_mismatch", self.recipient_mismatch, self.bridge))

            # Tokens
            alerts.extend(self._run_signature_check("amount_mismatch", self.amount_mismatch, self.bridge))
            alerts.extend(self._run_signature_check("over_mint", self.over_mint, self.bridge))
            alerts.extend(self._run_signature_check("over_release", self.over_release, self.bridge))

            # Contract authorization
            alerts.extend(self._run_signature_check("unauthorized_contracts", self.unauthorized_contracts, self.bridge))

            # Event callers
            alerts.extend(self._run_signature_check("check_event_callers", self.check_event_callers))

            # Replay / duplicate execution
            for flow_type in ("deposits", "withdrawals"):
                for flow in self._configured_flows(self.bridge, flow_type):
                    alerts.extend(
                        self._run_signature_check(
                            f"detect_replays.{flow_type}.{flow.name}",
                            self.detect_replays,
                            self.bridge,
                            flow,
                        )
                    )

            # Bridge-specific checks
            for check_name, check_fn, check_args in self.bridge_specific_signature_checks():
                alerts.extend(
                    self._run_signature_check(
                        check_name,
                        check_fn,
                        *check_args,
                    )
                )
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

    def _run_signature_check(self, check_name: str, check_fn, *args) -> List[DetectionAlert]:
        if self.evaluation_reporter is None:
            return check_fn(*args)

        with self.evaluation_reporter.timer(
            "signature_check_timer",
            {"bridge": self.bridge, "signature_check": check_name},
        ) as payload:
            alerts = check_fn(*args)
            payload["alerts_detected"] = len(alerts)
        return alerts

    def create_detection_alert(
        self,
        signature_type: SignatureType,
        severity: AlertSeverity,
        bridge: str,
        correlation_id: str,
        correlation_type: str | None,
        src_event_id: int | None,
        dst_event_id: int | None,
        title: str,
        description: str,
        created_at_ts: int | None,
        probability: str,
    ) -> DetectionAlert:
        return DetectionAlert(
            signature_type=signature_type,
            severity=severity,
            bridge=bridge,
            correlation_id=correlation_id,
            correlation_type=correlation_type,
            src_event_id=src_event_id,
            dst_event_id=dst_event_id,
            title=title,
            description=description,
            created_at_ts=created_at_ts,
            probability=probability,
        )
