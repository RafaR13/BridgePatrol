from db.database import engine, Base
from db.repository.detection_alert.detection_alert_repository import DetectionAlertRepository
from signature_detection.constants import Bridges
from db.repository.detection_alert.detection_alert_model import DetectionAlert

from signature_detection.signature_scripts.acrossAnalyser import AcrossAnalyser
from signature_detection.signature_scripts.ccipAnalyser import CCIPAnalyser
from signature_detection.signature_scripts.cctpAnalyser import CCTPAnalyser
from signature_detection.signature_scripts.debridgeAnalyser import DeBridgeAnalyser
from signature_detection.signature_scripts.mayanAnalyser import MayanAnalyser
from signature_detection.signature_scripts.omnibridgeAnalyser import OmnibridgeAnalyser
from signature_detection.signature_scripts.roninAnalyser import RoninAnalyser
from signature_detection.signature_scripts.polygonAnalyser import PolygonAnalyser
from signature_detection.signature_scripts.stargateAnalyser import StargateAnalyser
from signature_detection.signature_scripts.thorchainAnalyser import ThorchainAnalyser
from signature_detection.signature_scripts.meterIoAnalyser import MeterIoAnalyser
from signature_detection.signature_scripts.qubitAnalyser import QubitAnalyser

ANALYSER_BY_BRIDGE = {
    Bridges.STARGATE.value: StargateAnalyser,
    Bridges.CCTP.value: CCTPAnalyser,
    Bridges.CCIP.value: CCIPAnalyser,
    Bridges.ACROSS.value: AcrossAnalyser,
    Bridges.RONIN.value: RoninAnalyser,
    Bridges.POLYGON.value: PolygonAnalyser,
    Bridges.OMNIBRIDGE.value: OmnibridgeAnalyser,
    Bridges.DEBRIDGE.value: DeBridgeAnalyser,
    Bridges.MAYAN.value: MayanAnalyser,
    Bridges.THORCHAIN.value: ThorchainAnalyser,
    Bridges.METER_IO.value: MeterIoAnalyser,
    Bridges.QUBIT.value: QubitAnalyser,
}


def run_for_bridge(
    bridge: str,
    start_ts: int | None = None,
    end_ts: int | None = None,
    persist: bool = False,
) -> list[DetectionAlert]:
    # ensure tables exist
    Base.metadata.create_all(bind=engine)
    bridge_name = bridge.value if isinstance(bridge, Bridges) else bridge
    if bridge_name not in Bridges:
        raise ValueError(f"Bridge {bridge} is not recognized")

    analyser_cls = ANALYSER_BY_BRIDGE.get(bridge_name)
    if analyser_cls is None:
        return []
    analyser = analyser_cls()

    alerts = analyser.analyse_all(start_ts=start_ts, end_ts=end_ts)

    if persist and alerts:
        repo = DetectionAlertRepository()
        repo.insert_many(alerts)

    return alerts


def run_for_bridges(
    bridges: list[str],
    start_ts: int | None = None,
    end_ts: int | None = None,
    persist: bool = False,
) -> list[DetectionAlert]:
    all_alerts = []
    for bridge in bridges:
        alerts = run_for_bridge(bridge, start_ts=start_ts, end_ts=end_ts, persist=persist)
        all_alerts.extend(alerts)
    return all_alerts


def run_for_all_bridges(
    start_ts: int | None = None,
    end_ts: int | None = None,
    persist: bool = False,
) -> list[DetectionAlert]:
    all_alerts = []
    for bridge in Bridges:
        all_alerts.extend(
            run_for_bridge(bridge=bridge, start_ts=start_ts, end_ts=end_ts, persist=persist)
        )
    return all_alerts
