import pytest

from signature_detection.runners.run_signature_detection import run_for_bridge
from signature_detection.signature_scripts.thorchainAnalyser import ThorchainAnalyser


def test_thorchain_signatures():
    alerts = run_for_bridge("thorchain", persist=False)
    print(alerts)
    assert isinstance(alerts, list)


def test_thorchain_analyse_all_only_runs_source_side_checks(monkeypatch):
    analyser = ThorchainAnalyser()
    calls = []

    monkeypatch.setattr(analyser, "_set_analysis_window", lambda **kwargs: calls.append("window"))
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
        "over_mint",
        "over_release",
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
