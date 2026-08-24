from db.database import engine, Base
from db.database import get_session
from db.repository.normalized_event.normalized_event_model import get_normalized_event_model
from db.repository.detection_alert.detection_alert_repository import DetectionAlertRepository
from signature_detection.constants import Bridges
from db.repository.detection_alert.detection_alert_model import DetectionAlert
from evaluation.reporting import build_reporter

from signature_detection.signature_scripts.acrossAnalyser import AcrossAnalyser
from signature_detection.signature_scripts.ccipAnalyser import CCIPAnalyser
from signature_detection.signature_scripts.cctpAnalyser import CCTPAnalyser
from signature_detection.signature_scripts.debridgeAnalyser import DeBridgeAnalyser
from signature_detection.signature_scripts.mayanAnalyser import MayanAnalyser
from signature_detection.signature_scripts.nomadAnalyser import NomadAnalyser
from signature_detection.signature_scripts.omnibridgeAnalyser import OmnibridgeAnalyser
from signature_detection.signature_scripts.roninAnalyser import RoninAnalyser
from signature_detection.signature_scripts.polygonAnalyser import PolygonAnalyser
from signature_detection.signature_scripts.stargateAnalyser import StargateAnalyser
from signature_detection.signature_scripts.thorchainAnalyser import ThorchainAnalyser
from signature_detection.signature_scripts.meterIoAnalyser import MeterIoAnalyser
from signature_detection.signature_scripts.pnetworkAnalyser import PNetworkAnalyser
from signature_detection.signature_scripts.qubitAnalyser import QubitAnalyser
from signature_detection.signature_scripts.chainswapAnalyser import ChainSwapAnalyser

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
    Bridges.NOMAD.value: NomadAnalyser,
    Bridges.THORCHAIN.value: ThorchainAnalyser,
    Bridges.METER_IO.value: MeterIoAnalyser,
    Bridges.PNETWORK.value: PNetworkAnalyser,
    Bridges.QUBIT.value: QubitAnalyser,
    Bridges.CHAINSWAP.value: ChainSwapAnalyser,
}


def run_for_bridge(
    bridge: str,
    start_ts: int | None = None,
    end_ts: int | None = None,
    persist: bool = False,
    report_path: str | None = None,
    run_id: str | None = None,
) -> list[DetectionAlert]:
    bridge_name = bridge.value if isinstance(bridge, Bridges) else bridge
    known_bridges = {supported_bridge.value for supported_bridge in Bridges}
    if bridge_name not in known_bridges:
        raise ValueError(f"Bridge {bridge} is not recognized")

    analyser_cls = ANALYSER_BY_BRIDGE.get(bridge_name)
    if analyser_cls is None:
        reporter = build_reporter(report_path, run_id=run_id)
        if reporter is not None:
            reporter.write(
                "signature_detection_bridge_summary",
                {
                    "bridge": bridge_name,
                    "normalized_events_analyzed": None,
                    "alerts_detected": 0,
                    "skipped": True,
                    "reason": "no_signature_analyser",
                },
            )
        return []

    # Ensure tables exist only after resolving a runnable analyser.
    Base.metadata.create_all(bind=engine)
    analyser = analyser_cls()
    analyser.evaluation_reporter = build_reporter(report_path, run_id=run_id)

    alerts = analyser.analyse_all(start_ts=start_ts, end_ts=end_ts)

    if persist and alerts:
        repo = DetectionAlertRepository()
        repo.insert_many(alerts)

    if analyser.evaluation_reporter is not None:
        try:
            model = get_normalized_event_model(bridge_name)
            normalized_events_analyzed = _count_normalized_events(
                model=model,
                start_ts=start_ts,
                end_ts=end_ts,
            )
        except ValueError:
            normalized_events_analyzed = None
        analyser.evaluation_reporter.write(
            "signature_detection_bridge_summary",
            {
                "bridge": bridge_name,
                "normalized_events_analyzed": normalized_events_analyzed,
                "alerts_detected": len(alerts),
            },
        )

    return alerts


def run_for_bridges(
    bridges: list[str],
    start_ts: int | None = None,
    end_ts: int | None = None,
    persist: bool = False,
    report_path: str | None = None,
    run_id: str | None = None,
) -> list[DetectionAlert]:
    all_alerts = []
    for bridge in bridges:
        alerts = run_for_bridge(
            bridge,
            start_ts=start_ts,
            end_ts=end_ts,
            persist=persist,
            report_path=report_path,
            run_id=run_id,
        )
        all_alerts.extend(alerts)
    return all_alerts


def run_for_all_bridges(
    start_ts: int | None = None,
    end_ts: int | None = None,
    persist: bool = False,
    report_path: str | None = None,
    run_id: str | None = None,
) -> list[DetectionAlert]:
    all_alerts = []
    for bridge in Bridges:
        all_alerts.extend(
            run_for_bridge(
                bridge=bridge,
                start_ts=start_ts,
                end_ts=end_ts,
                persist=persist,
                report_path=report_path,
                run_id=run_id,
            )
        )
    return all_alerts


def _count_normalized_events(model, start_ts: int | None, end_ts: int | None) -> int:
    session = get_session()
    try:
        query = session.query(model)
        if start_ts is not None:
            query = query.filter(model.timestamp >= start_ts)
        if end_ts is not None:
            query = query.filter(model.timestamp <= end_ts)
        return query.count()
    finally:
        session.close()
