from signature_detection.runners.run_signature_detection import run_for_bridge

from assertions import assert_valid_alerts


def test_stargate_signatures():
    alerts = run_for_bridge("stargate", persist=False)
    print(alerts)
    assert_valid_alerts(alerts, "stargate")
