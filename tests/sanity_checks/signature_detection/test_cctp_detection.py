from signature_detection.runners.run_signature_detection import run_for_bridge

from assertions import assert_valid_alerts


def test_cctp_signatures():
    alerts = run_for_bridge("cctp", persist=False)
    print(alerts)
    assert_valid_alerts(alerts, "cctp")
