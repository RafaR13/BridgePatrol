from types import SimpleNamespace

import pytest

from signature_detection.constants import SignatureType
from signature_detection.runners.run_signature_detection import run_for_bridge
from signature_detection.signature_scripts.thorchainAnalyser import ThorchainAnalyser

from assertions import assert_valid_alerts


def test_thorchain_signatures():
    alerts = run_for_bridge("thorchain", persist=False)
    print(alerts)
    assert_valid_alerts(alerts, "thorchain")


def test_thorchain_analyse_all_only_runs_source_side_checks(monkeypatch):
    analyser = ThorchainAnalyser()
    calls = []

    monkeypatch.setattr(analyser, "_set_analysis_window", lambda **kwargs: calls.append("window"))
    monkeypatch.setattr(
        analyser,
        "incomplete_cross_chain_transactions",
        lambda bridge: calls.append("incomplete_cross_chain_transactions") or [],
    )
    monkeypatch.setattr(
        analyser,
        "token_contract_attacks",
        lambda: calls.append("token_contract_attacks") or [],
    )
    monkeypatch.setattr(
        analyser,
        "analyse_source_trace_operations",
        lambda: calls.append("source_trace_operations") or [],
    )
    monkeypatch.setattr(
        analyser,
        "analyse_bridge_specific_signatures",
        lambda: calls.append("bridge_specific") or [],
    )

    destination_or_pair_checks = (
        "lock_without_mint",
        "mint_without_lock",
        "recipient_mismatch",
        "amount_mismatch",
        "unauthorized_contracts",
        "check_event_callers",
        "detect_replays",
    )
    for method_name in destination_or_pair_checks:
        monkeypatch.setattr(
            analyser,
            method_name,
            lambda *args, name=method_name, **kwargs: pytest.fail(
                f"{name} must not run for source-only Thorchain data"
            ),
        )

    assert analyser.analyse_all() == []
    assert calls == [
        "window",
        "token_contract_attacks",
        "source_trace_operations",
        "bridge_specific",
    ]


def test_thorchain_src_only_cctx_alerts_as_lock_without_mint(monkeypatch):
    analyser = ThorchainAnalyser()
    analyser._set_analysis_window(start_ts=None, end_ts=2_000)
    monkeypatch.setattr(analyser, "_event_is_recent", lambda *args: False)

    alerts = analyser.incomplete_cross_chain_transactions(
        "thorchain",
        [
            SimpleNamespace(
                cctx_id="thorchain:0xsrc",
                src_transaction_hash="0xsrc",
                src_timestamp=1_000,
                src_blockchain="ethereum",
                dst_transaction_hash=None,
                dst_timestamp=None,
            )
        ],
    )

    assert len(alerts) == 1
    assert alerts[0].signature_type == SignatureType.LOCK_WITHOUT_MINT
    assert alerts[0].correlation_id == "thorchain:0xsrc"
