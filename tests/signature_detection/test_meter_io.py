from signature_detection.runners.run_signature_detection import run_for_bridge


def test_meter_io_signatures():
    alerts = run_for_bridge("meter.io", persist=False)
    print(alerts)
    assert isinstance(alerts, list)
