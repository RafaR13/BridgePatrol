from signature_detection.runners.run_signature_detection import run_for_bridge


def test_mayan_signatures():
    alerts = run_for_bridge("mayan", persist=False)
    print(alerts)
    assert isinstance(alerts, list)
