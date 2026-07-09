from signature_detection.runners.run_signature_detection import run_for_bridge

def test_ronin_signatures():
    alerts = run_for_bridge("ronin", persist=False)
    print(alerts)
    assert isinstance(alerts, list)