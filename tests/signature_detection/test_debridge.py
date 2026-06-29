from signature_detection.runners.run_signature_detection import run_for_bridge


def test_debridge_signatures():
    alerts = run_for_bridge("debridge", persist=False)
    print(alerts)
    assert isinstance(alerts, list)
