from signature_detection.runners.run_signature_detection import run_for_bridge

from assertions import assert_valid_alerts


def test_debridge_signatures():
    alerts = run_for_bridge("debridge", persist=False)
    print(alerts)
    assert_valid_alerts(alerts, "debridge")
