from signature_detection.runners.run_signature_detection import run_for_bridge

from assertions import assert_valid_alerts


def test_meter_io_signatures():
    alerts = run_for_bridge("meter.io", persist=False)
    print(alerts)
    assert_valid_alerts(alerts, "meter.io")
