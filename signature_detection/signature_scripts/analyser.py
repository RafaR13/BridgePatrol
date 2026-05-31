from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from db.repository.detection_alert.detection_alert_model import DetectionAlert
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
from signature_detection.signature_scripts.utils import AnalyserUtilsMixin


class Analyser(
    MissingEventPairsMixin,
    RecipientMissmatchMixin,
    TokenChecksMixin,
    UnauthorizedContractsMixin,
    DetectReplaysMixin,
    TokenContractAttacksMixin,
    AnalyserUtilsMixin,
    ABC,
):
    DEBUG = True
    DEBUG_TRANSACTION_HASH: str | None = None

    def __init__(self, bridge: str):
        self.bridge = bridge
        self._transaction_context: tuple[dict[str, int], dict[str, int]] | None = None

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

    def analyse_all(self, start_ts: int, end_ts: int) -> List[DetectionAlert]:
        """
        Run every configured analyser check and return a single alert list.
        """
        alerts: List[DetectionAlert] = []

        # Missing event pairs
        alerts.extend(self.lock_without_mint(self.bridge, start_ts, end_ts))
        alerts.extend(self.mint_without_lock(self.bridge, start_ts, end_ts))

        # Recipient Mismatch
        alerts.extend(self.recipient_mismatch(self.bridge))

        # Tokens
        alerts.extend(self.amount_mismatch(self.bridge))
        alerts.extend(self.over_mint(self.bridge))
        alerts.extend(self.over_release(self.bridge))

        # Contract authorization
        alerts.extend(self.unauthorized_contracts(self.bridge))

        # Replay / duplicate execution
        for flow_type in ("deposits", "withdrawals"):
            for flow in self._configured_flows(self.bridge, flow_type):
                alerts.extend(self.detect_replays(self.bridge, flow))

        # Bridge-specific checks
        alerts.extend(self.analyse_bridge_specific_signatures())
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
        created_at_ts: int,
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
