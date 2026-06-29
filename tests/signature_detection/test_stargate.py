from signature_detection.runners.run_signature_detection import run_for_bridge


def test_stargate_signatures():
    alerts = run_for_bridge("stargate", persist=False)
    print(alerts)
    assert isinstance(alerts, list)
