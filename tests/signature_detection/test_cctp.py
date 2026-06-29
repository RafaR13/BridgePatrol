from signature_detection.runners.run_signature_detection import run_for_bridge


def test_cctp_signatures():
    alerts = run_for_bridge("cctp", persist=False)
    print(alerts)
    assert isinstance(alerts, list)
