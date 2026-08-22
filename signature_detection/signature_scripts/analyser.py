from __future__ import annotations

from abc import ABC, abstractmethod
import time
from typing import List

from db.repository.detection_alert.detection_alert_model import DetectionAlert
from evaluation.reporting import EvaluationReporter
from normalization.event_types import NormalizedEventType
from signature_detection.constants import (
    AlertSeverity,
    SignatureType,
    TOKEN_CONTRACT_ATTACK_CONFIG,
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
    CCTX_GROUP_CHECKS = {
        "lock_without_mint",
        "mint_without_lock",
        "recipient_mismatch",
        "amount_mismatch",
        "contract_discrepancies",
    }
    EVENT_CHECKS = {
        "unauthorized_contracts",
        "token_contract_attacks",
        "state_synced_contract_authorization",
        "token_mappings",
    }
    TRANSACTION_CHECKS = {
        "check_event_callers",
        "incomplete_cross_chain_transactions",
        "source_trace_operations",
        "ronin_proofs",
    }

    def __init__(self, bridge: str):
        self.bridge = bridge
        self._transaction_context: tuple[dict[str, int], dict[str, int]] | None = None
        self._analysis_blockchain_transactions_cache: list | None = None
        self._analysis_blockchain_transactions_by_hash_cache: dict | None = None
        self._latest_block_numbers_by_blockchain: dict[str, int] | None = None
        self._latest_block_number: int | None = None
        self._cross_chain_transactions_cache: list | None = None
        self._transfers_by_transaction_hash_cache = {}
        self._analysis_start_ts: int | None = None
        self._analysis_end_ts: int | None = None
        self._analysis_has_time_filter = False
        self._events_cache = {}
        self._event_pairs_cache = {}
        self.evaluation_reporter: EvaluationReporter | None = None

    def _debug(self, message: str) -> None:
        if self.DEBUG:
            print(f"[signature-debug][{self.bridge}] {message}")

    @abstractmethod
    def fetch_blockchain_transactions(
        self, start_ts: int | None = None, end_ts: int | None = None
    ):
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

        start_ns = time.perf_counter_ns()
        alerts = check_fn(*args)
        end_ns = time.perf_counter_ns()

        duration_ns = end_ns - start_ns
        duration_ms = duration_ns / 1_000_000
        payload = {
            "bridge": self.bridge,
            "signature_check": check_name,
            "alerts_detected": len(alerts),
            "duration_ns": duration_ns,
            "duration_ms": duration_ms,
        }
        payload.update(self._signature_check_unit_stats(check_name, args, duration_ms))
        self.evaluation_reporter.write("signature_check_timer", payload)
        return alerts

    def _signature_check_unit_stats(
        self,
        check_name: str,
        args: tuple,
        duration_ms: float,
    ) -> dict:
        if check_name.startswith("detect_replays."):
            return self._event_pair_unit_stats(
                unit_type="cctx_group",
                duration_ms=duration_ms,
                flows=[args[1]] if len(args) > 1 else [],
            )

        if check_name in self.CCTX_GROUP_CHECKS:
            return self._event_pair_unit_stats(
                unit_type="cctx_group",
                duration_ms=duration_ms,
                flows=self._flows_for_cctx_group_check(check_name),
            )

        if check_name in self.EVENT_CHECKS:
            return self._event_unit_stats(check_name, duration_ms)

        if check_name in self.TRANSACTION_CHECKS:
            return self._transaction_unit_stats(check_name, duration_ms)

        return {
            "unit_type": "unknown",
            "cctx_analyzed": None,
            "event_groups_analyzed": None,
            "events_analyzed": None,
            "transactions_analyzed": None,
            "ms_per_cctx": None,
            "ms_per_event_group": None,
            "ms_per_event": None,
            "ms_per_transaction": None,
        }

    def _flows_for_cctx_group_check(self, check_name: str):
        if check_name in {"lock_without_mint", "mint_without_lock"}:
            flow_types = ("deposits",)
        else:
            flow_types = ("deposits", "withdrawals")

        flows = []
        for flow_type in flow_types:
            flows.extend(self._configured_flows(self.bridge, flow_type))
        return flows

    def _event_pair_unit_stats(
        self,
        unit_type: str,
        duration_ms: float,
        flows,
    ) -> dict:
        event_groups_analyzed = 0
        events_analyzed = 0
        cctx_ids: set[str] = set()

        for flow in flows:
            grouped_events = self.fetch_event_pairs(self.bridge, flow)
            event_groups_analyzed += len(grouped_events)
            for events in grouped_events.values():
                for side in ("source", "destination"):
                    events_analyzed += len(events[side])
                    for event in events[side]:
                        if getattr(event, "cctx_id", None):
                            cctx_ids.add(str(event.cctx_id))

        cctx_analyzed = len(cctx_ids) if cctx_ids else event_groups_analyzed
        return self._unit_stats_payload(
            unit_type=unit_type,
            duration_ms=duration_ms,
            cctx_analyzed=cctx_analyzed,
            event_groups_analyzed=event_groups_analyzed,
            events_analyzed=events_analyzed,
            transactions_analyzed=None,
        )

    def _event_unit_stats(self, check_name: str, duration_ms: float) -> dict:
        events = []
        event_groups_analyzed = None

        if check_name == "token_contract_attacks":
            for config in TOKEN_CONTRACT_ATTACK_CONFIG.get(self.bridge, ()):
                events.extend(self._events_by_event_type(config.event_type, self.bridge))
        elif check_name == "state_synced_contract_authorization":
            events.extend(
                self._events_by_event_type(NormalizedEventType.STATE_SYNCED, self.bridge)
            )
        elif check_name == "token_mappings":
            events.extend(
                self._events_by_event_type(NormalizedEventType.TOKEN_DEPOSITED, self.bridge)
            )
            events.extend(
                self._events_by_event_type(NormalizedEventType.CHILD_TOKEN_BURN, self.bridge)
            )
        elif check_name == "unauthorized_contracts":
            event_groups_analyzed = 0
            seen_event_ids: set[int] = set()
            for flow_type in ("deposits", "withdrawals"):
                for flow in self._configured_flows(self.bridge, flow_type):
                    grouped_events = self.fetch_event_pairs(self.bridge, flow)
                    event_groups_analyzed += len(grouped_events)
                    for grouped in grouped_events.values():
                        for side in ("source", "destination"):
                            for event in grouped[side]:
                                if event.id in seen_event_ids:
                                    continue
                                seen_event_ids.add(event.id)
                                events.append(event)

        cctx_ids = {
            str(event.cctx_id)
            for event in events
            if getattr(event, "cctx_id", None)
        }
        return self._unit_stats_payload(
            unit_type="event",
            duration_ms=duration_ms,
            cctx_analyzed=len(cctx_ids) if cctx_ids else None,
            event_groups_analyzed=event_groups_analyzed,
            events_analyzed=len(events),
            transactions_analyzed=None,
        )

    def _transaction_unit_stats(self, check_name: str, duration_ms: float) -> dict:
        if check_name == "ronin_proofs" and hasattr(
            self, "fetch_blockchain_transactions_with_receipts_with_signatures"
        ):
            transactions = self.fetch_blockchain_transactions_with_receipts_with_signatures()
        else:
            transactions = self._analysis_blockchain_transactions()

        return self._unit_stats_payload(
            unit_type="transaction",
            duration_ms=duration_ms,
            cctx_analyzed=None,
            event_groups_analyzed=None,
            events_analyzed=None,
            transactions_analyzed=len(transactions),
        )

    def _unit_stats_payload(
        self,
        unit_type: str,
        duration_ms: float,
        cctx_analyzed: int | None,
        event_groups_analyzed: int | None,
        events_analyzed: int | None,
        transactions_analyzed: int | None,
    ) -> dict:
        return {
            "unit_type": unit_type,
            "cctx_analyzed": cctx_analyzed,
            "event_groups_analyzed": event_groups_analyzed,
            "events_analyzed": events_analyzed,
            "transactions_analyzed": transactions_analyzed,
            "ms_per_cctx": self._duration_per_unit(duration_ms, cctx_analyzed),
            "ms_per_event_group": self._duration_per_unit(duration_ms, event_groups_analyzed),
            "ms_per_event": self._duration_per_unit(duration_ms, events_analyzed),
            "ms_per_transaction": self._duration_per_unit(duration_ms, transactions_analyzed),
        }

    def _duration_per_unit(self, duration_ms: float, unit_count: int | None) -> float | None:
        if unit_count is None or unit_count <= 0:
            return None
        return duration_ms / unit_count

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
