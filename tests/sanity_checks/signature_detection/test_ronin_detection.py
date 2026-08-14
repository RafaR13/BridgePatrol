from types import SimpleNamespace

from signature_detection.constants import SignatureType
from signature_detection.runners.run_signature_detection import run_for_bridge
from signature_detection.signature_scripts.roninAnalyser import RoninAnalyser

from assertions import assert_valid_alerts


def test_ronin_signatures():
    alerts = run_for_bridge("ronin", persist=False)
    print(alerts)
    assert_valid_alerts(alerts, "ronin")


def test_ronin_dst_only_cctx_alerts_as_mint_without_lock(monkeypatch):
    analyser = RoninAnalyser()
    analyser._set_analysis_window(start_ts=None, end_ts=2_000)
    monkeypatch.setattr(analyser, "_event_is_recent", lambda *args: False)

    alerts = analyser.incomplete_cross_chain_transactions(
        "ronin",
        [
            SimpleNamespace(
                id=35,
                deposit_id=2_000_000,
                src_transaction_hash=None,
                src_timestamp=None,
                dst_transaction_hash="0xdst",
                dst_timestamp=1_000,
            )
        ],
    )

    assert len(alerts) == 1
    assert alerts[0].signature_type == SignatureType.MINT_WITHOUT_LOCK
    assert alerts[0].correlation_id == "ronin:deposit_id:2000000"
