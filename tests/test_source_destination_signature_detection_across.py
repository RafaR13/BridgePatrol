from signature_detection.runners.run_source_destination_signatures import run_for_bridge


def test_run_source_destination_signatures_across():
    alerts = run_for_bridge("across", persist=False, min_age_seconds=0)
    print(alerts)
    assert isinstance(alerts, list)