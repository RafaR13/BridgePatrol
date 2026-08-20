from signature_detection.runners.run_signature_detection import run_for_all_bridges

from assertions import assert_valid_alerts


def test_all_bridges_signatures():
    alerts = run_for_all_bridges(persist=False)
    print(alerts)
    assert_valid_alerts(alerts)
