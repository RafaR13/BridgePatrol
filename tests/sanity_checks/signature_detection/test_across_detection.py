from signature_detection.runners.run_signature_detection import run_for_bridge

from assertions import assert_valid_alerts


def test_run_source_destination_signatures_across():
    alerts = run_for_bridge("across", persist=False)
    print(alerts)
    assert_valid_alerts(alerts, "across")
