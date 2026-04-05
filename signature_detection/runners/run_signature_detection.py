from db.database import engine, Base
from db.repository.detection_alert.detection_alert_repository import DetectionAlertRepository
from signature_detection.signature_scripts.source_destination import check_all_signatures
from signature_detection.signature_scripts.cctx_analysis import check_cctxs
from config.constants import Bridges


def run_for_bridge(bridge: str, persist: bool = False):
    # ensure tables exist
    Base.metadata.create_all(bind=engine)


    alerts = check_all_signatures(bridge)
    alerts.extend(check_cctxs(bridge))

    if persist and alerts:
        repo = DetectionAlertRepository()
        repo.insert_many(alerts)

    return alerts

def run_for_bridges(bridges: list[str], persist: bool = False):
    all_alerts = []
    for bridge in bridges:
        alerts = run_for_bridge(bridge, persist=persist)
        all_alerts.extend(alerts)
    return all_alerts

def run_for_all_bridges(persist: bool = False):
    all_alerts = []
    for bridge in Bridges:
        all_alerts.extend(run_for_bridge(bridge=bridge, persist=persist))
    return all_alerts
