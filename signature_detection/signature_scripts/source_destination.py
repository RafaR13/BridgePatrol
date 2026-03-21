from db.repository.detection_alert.detection_alert_model import DetectionAlert
from db.repository.normalized_event.normalized_event_repository import NormalizedEventRepository
from signature_detection.correlation import group_events_by_correlation
from signature_detection.types import AlertSeverity, AlertStatus, SignatureType


def _pick_first(events):
    return events[0] if events else None


def detect_fill_without_source(bridge: str, correlation_id: str, sources: list, destinations: list) -> DetectionAlert:

    if not sources and destinations:
        dst = _pick_first(destinations)

        return DetectionAlert(
            signature_type=SignatureType.FILL_WITHOUT_SOURCE,
            severity=AlertSeverity.HIGH,
            status=AlertStatus.OPEN,
            bridge=bridge,
                correlation_id=correlation_id,
                correlation_type=dst.correlation_type,
                src_event_id=None,
                dst_event_id=dst.id,
                title=f"{bridge}: destination event without source",
                description=(
                    f"Found destination-side event {dst.event_type} with "
                    f"correlation_id={correlation_id}, but no matching source event."
                ),
                created_at_ts=dst.timestamp,
            )


def detect_source_without_fill(bridge: str, correlation_id: str, max_seen_ts: int, sources: list, destinations: list, min_age_seconds: int = 0) -> DetectionAlert:

    if sources and not destinations:
        src = _pick_first(sources)

        if min_age_seconds > 0 and src.timestamp is not None:
            if max_seen_ts - src.timestamp < min_age_seconds:
                return

        return DetectionAlert(
            signature_type=SignatureType.SOURCE_WITHOUT_FILL,
            severity=AlertSeverity.MEDIUM,
            status=AlertStatus.OPEN,
                bridge=bridge,
                correlation_id=correlation_id,
                correlation_type=src.correlation_type,
                src_event_id=src.id,
                dst_event_id=None,
                title=f"{bridge}: source event without destination",
                description=(
                    f"Found source-side event {src.event_type} with "
                    f"correlation_id={correlation_id}, but no matching destination event."
                ),
                created_at_ts=src.timestamp,
            )


def detect_amount_mismatch(bridge: str, correlation_id: str, sources: list, destinations: list) -> DetectionAlert:
  
    if not sources or not destinations:
        return None

    src = _pick_first(sources)
    dst = _pick_first(destinations)

    src_amount = src.amount_out if src.amount_out is not None else src.amount_in
    dst_amount = dst.amount_out if dst.amount_out is not None else dst.amount_in

    if src_amount is None or dst_amount is None:
        return None

    if src_amount != dst_amount:
        return DetectionAlert(
            signature_type=SignatureType.AMOUNT_MISMATCH,
            severity=AlertSeverity.HIGH,
            status=AlertStatus.OPEN,
            bridge=bridge,
            correlation_id=correlation_id,
            correlation_type=src.correlation_type or dst.correlation_type,
            src_event_id=src.id,
            dst_event_id=dst.id,
            title=f"{bridge}: amount mismatch between source and destination",
            description=(
                f"Source event {src.event_type} and destination event {dst.event_type} "
                f"share correlation_id={correlation_id}, but amounts differ "
                f"(source={src_amount}, destination={dst_amount})."
            ),
            created_at_ts=dst.timestamp or src.timestamp,
        )


def run_source_destination_signatures(bridge: str, min_age_seconds: int = 0) -> list[DetectionAlert]:
    events = NormalizedEventRepository.get_events_by_bridge(bridge)
    grouped = group_events_by_correlation(events)
    max_seen_ts = max((e.timestamp or 0 for e in events), default=0)

    alerts = []

    for key, bucket in grouped.items():
        if key[1] is not None and key[2] is not None:
            sources = bucket["sources"]
            destinations = bucket["destinations"]

            alerts.append(detect_fill_without_source(bridge, key[-1], sources, destinations))
            alerts.append(detect_source_without_fill(bridge, key[-1], max_seen_ts, sources, destinations, min_age_seconds=min_age_seconds))
            alerts.append(detect_amount_mismatch(bridge, key[-1], sources, destinations))

    return alerts