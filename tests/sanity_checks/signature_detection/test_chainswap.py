from types import SimpleNamespace

import pytest
from sqlalchemy.exc import OperationalError

from signature_detection.constants import SignatureType
from signature_detection.runners.run_signature_detection import run_for_bridge
from signature_detection.signature_scripts.chainswapAnalyser import ChainSwapAnalyser


def test_chainswap_signatures():
    try:
        alerts = run_for_bridge("chainswap", persist=False)
    except OperationalError as exc:
        pytest.skip(f"database unavailable for ChainSwap integration test: {exc}")

    print(alerts)
    assert isinstance(alerts, list)


def test_chainswap_dst_only_cctx_alerts_as_mint_without_lock(monkeypatch):
    analyser = ChainSwapAnalyser()
    analyser._set_analysis_window(start_ts=None, end_ts=2_000)
    monkeypatch.setattr(analyser, "_event_is_recent", lambda *args: False)

    alerts = analyser.incomplete_cross_chain_transactions(
        "chainswap",
        [
            SimpleNamespace(
                cctx_id="chainswap:0xdst",
                src_transaction_hash=None,
                src_timestamp=None,
                dst_transaction_hash="0xdst",
                dst_timestamp=1_000,
            )
        ],
    )

    assert len(alerts) == 1
    assert alerts[0].signature_type == SignatureType.MINT_WITHOUT_LOCK
    assert alerts[0].correlation_id == "chainswap:0xdst"
