from signature_detection.runners.run_signature_detection import run_for_bridge

from assertions import assert_valid_alerts


def test_qubit_signatures():
    alerts = run_for_bridge("qubit", persist=False)
    print(alerts)
    assert_valid_alerts(alerts, "qubit")
