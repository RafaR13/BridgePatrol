from signature_detection.runners.run_signature_detection import run_for_bridge

from assertions import assert_valid_alerts


def test_nomad_signatures():
    alerts = run_for_bridge("nomad", persist=False)
    print(alerts)
    assert_valid_alerts(alerts, "nomad")
