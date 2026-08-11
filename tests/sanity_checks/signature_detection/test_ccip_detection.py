from signature_detection.runners.run_signature_detection import run_for_bridge

from assertions import assert_valid_alerts


def test_ccip_signatures():
    alerts = run_for_bridge("ccip", persist=False)
    print(alerts)
    assert_valid_alerts(alerts, "ccip")
