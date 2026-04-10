from db.database import engine, Base
from db.repository.detection_alert.detection_alert_repository import DetectionAlertRepository
from signature_detection.signature_scripts.roninAnalyser import RoninAnalyser
from config.constants import Bridges
from db.repository.detection_alert.detection_alert_model import DetectionAlert


def run_for_bridge(bridge: str, persist: bool = False) -> list[DetectionAlert]:
    # ensure tables exist
    Base.metadata.create_all(bind=engine)
    analyser = None

    if bridge not in Bridges:
        raise ValueError(f"Bridge {bridge} is not recognized. Valid bridges are: {Bridges}")
    if bridge == "ronin":
        analyser = RoninAnalyser()
    else:
        return []
    
    alerts = analyser.analyse_all()

    if persist and alerts:
        repo = DetectionAlertRepository()
        repo.insert_many(alerts)

    return alerts

def run_for_bridges(bridges: list[str], persist: bool = False) -> list[DetectionAlert]:
    all_alerts = []
    for bridge in bridges:
        alerts = run_for_bridge(bridge, persist=persist)
        all_alerts.extend(alerts)
    return all_alerts

def run_for_all_bridges(persist: bool = False) -> list[DetectionAlert]:
    all_alerts = []
    for bridge in Bridges:
        all_alerts.extend(run_for_bridge(bridge=bridge, persist=persist))
    return all_alerts
