from signature_detection.runners.run_signature_detection import run_for_all_bridges

def test_all_bridges_signatures():
    alerts = run_for_all_bridges(persist=False)
    print(alerts)
    assert isinstance(alerts, list)