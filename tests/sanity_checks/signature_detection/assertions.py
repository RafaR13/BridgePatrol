from db.repository.detection_alert.detection_alert_model import DetectionAlert


def assert_valid_alerts(alerts, bridge: str | None = None):
    assert isinstance(alerts, list)

    for alert in alerts:
        assert isinstance(alert, DetectionAlert)
        if bridge is not None:
            assert alert.bridge == bridge
        assert alert.signature_type is not None
        assert alert.severity is not None
        assert alert.title
        assert alert.description
        assert alert.probability is not None
