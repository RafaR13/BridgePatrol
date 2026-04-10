from signature_detection.runners.run_signature_detection import run_for_bridge


def test_run_source_destination_signatures_across():
    alerts = run_for_bridge("across", persist=False)
    print(alerts)
    assert isinstance(alerts, list)