from db.database import engine, Base
from db.repository.detection_alert.detection_alert_repository import DetectionAlertRepository
from signature_detection.signature_scripts.source_destination import run_source_destination_signatures
from signature_detection.types import Bridges


def run_for_bridge(bridge: str, persist: bool = False, min_age_seconds: int = 0):
    # ensure tables exist
    Base.metadata.create_all(bind=engine)

    alerts = run_source_destination_signatures(
        bridge=bridge,
        min_age_seconds=min_age_seconds,
    )

    if persist and alerts:
        repo = DetectionAlertRepository()
        repo.insert_many(alerts)

    return alerts

def run_for_bridges(bridges: list[str], persist: bool = False, min_age_seconds: int = 0):
    all_alerts = []
    for bridge in bridges:
        alerts = run_for_bridge(bridge, persist=persist, min_age_seconds=min_age_seconds)
        all_alerts.extend(alerts)
    return all_alerts

def run_for_all_bridges(persist: bool = False, min_age_seconds: int = 0):
    all_alerts = []
    for bridge in Bridges:
        all_alerts.extend(run_for_bridge(bridge=bridge, persist=persist, min_age_seconds=min_age_seconds))
    return all_alerts
    

"""if __name__ == "__main__":
    alerts = run_for_bridge("across", persist=False, min_age_seconds=0)

    print(f"Generated {len(alerts)} alerts")
    for alert in alerts:
        print(
            f"[{alert.signature_type}] correlation_id={alert.correlation_id} "
            f"title={alert.title}"
        )"""