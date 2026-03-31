from db.repository.detection_alert.detection_alert_model import DetectionAlert
from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from db.repository.normalized_event.normalized_event_repository import NormalizedEventRepository
from normalization.event_types import NormalizedEventType
from signature_detection.constants import BRIDGE_EVENT_MAP, AlertSeverity, SignatureType


def _pick_first(events):
    return events[0] if events else None

def _fetch_event_pairs(bridge: str, source: NormalizedEventType, destination: NormalizedEventType) -> dict[str, dict[str, list[NormalizedEvent]]]:
    """
    Fetches and groups normalized events for the given source and destination event types by correlation_id.
    ex: lock-mint, burn-release
    """
    # 2: query the normalized events for the source and destination events
    source_events = NormalizedEventRepository.get_events_by_event_type(source, bridge)
    destination_events = NormalizedEventRepository.get_events_by_event_type(destination, bridge)
    
    # 3: group the events by correlation_id
    grouped_events = {}
    for event in source_events:
        if not event.correlation_id:
            continue # TODO: handle events without correlation_id (i think it never happens tho)
        if event.correlation_id not in grouped_events:
            grouped_events[event.correlation_id] = {"source": [], "destination": []}
        grouped_events[event.correlation_id]["source"].append(event)
    for event in destination_events:
        if not event.correlation_id:
            continue # TODO: handle events without correlation_id (i think it never happens tho)
        if event.correlation_id not in grouped_events:
            grouped_events[event.correlation_id] = {"source": [], "destination": []}
        grouped_events[event.correlation_id]["destination"].append(event)

    return grouped_events

def lock_without_mint(bridge: str) -> list[DetectionAlert]:
    grouped_events = _fetch_event_pairs(bridge, BRIDGE_EVENT_MAP[bridge].lock, BRIDGE_EVENT_MAP[bridge].mint)
    # 4: detect lock events without corresponding mint events
    alerts = []
    for correlation_id, events in grouped_events.items():
        if events["source"] and not events["destination"]:
            for event in events["source"]:
                lock_event = _pick_first(events["source"])
                alerts.append(DetectionAlert(
                    signature_type=SignatureType.LOCK_WITHOUT_MINT,
                    severity=AlertSeverity.LOW,
                    bridge=bridge,
                    correlation_id=correlation_id,
                    correlation_type=lock_event.correlation_type,
                    src_event_id=lock_event.id,
                    dst_event_id=None,
                    title=f"{bridge}: lock event without corresponding mint event",
                    description=(
                        f"Found lock event {lock_event.event_type} with "
                        f"correlation_id={correlation_id}, but no matching mint event."
                    ),
                    created_at_ts=lock_event.timestamp,
                ))
    return alerts

def mint_without_lock(bridge: str) -> list[DetectionAlert]:
    grouped_events = _fetch_event_pairs(bridge, BRIDGE_EVENT_MAP[bridge].mint, BRIDGE_EVENT_MAP[bridge].lock)
    # 4: detect mint events without corresponding lock events
    alerts = []
    for correlation_id, events in grouped_events.items():
        if events["source"] and not events["destination"]:
            for event in events["source"]:
                mint_event = _pick_first(events["source"])
                alerts.append(DetectionAlert(
                    signature_type=SignatureType.MINT_WITHOUT_LOCK,
                    severity=AlertSeverity.LOW,
                    bridge=bridge,
                    correlation_id=correlation_id,
                    correlation_type=mint_event.correlation_type,
                    src_event_id=None,
                    dst_event_id=mint_event.id,
                    title=f"{bridge}: mint event without corresponding lock event",
                    description=(
                        f"Found mint event {mint_event.event_type} with "
                        f"correlation_id={correlation_id}, but no matching lock event."
                    ),
                    created_at_ts=mint_event.timestamp,
                ))
    return alerts

def over_mint(bridge: str) -> list[DetectionAlert]:
    grouped_events = _fetch_event_pairs(bridge, BRIDGE_EVENT_MAP[bridge].lock, BRIDGE_EVENT_MAP[bridge].mint)
    alerts = []
    for correlation_id, events in grouped_events.items():
        if not events["destination"] or not events["source"]:
            continue
        for mint_event in events["destination"]:
            for lock_event in events["source"]:
                if mint_event.amount_out is not None and lock_event.amount_out is not None and mint_event.amount_out > lock_event.amount_out:
                    alerts.append(DetectionAlert(
                        signature_type=SignatureType.OVER_MINT,
                        severity=AlertSeverity.LOW,
                        bridge=bridge,
                        correlation_id=correlation_id,
                        correlation_type=lock_event.correlation_type,
                        src_event_id=lock_event.id,
                        dst_event_id=mint_event.id,
                        title=f"{bridge}: over-mint detected",
                        description=(
                            f"Found mint event {mint_event.event_type} with amount {mint_event.amount_out} "
                            f"which is greater than the corresponding lock event {lock_event.event_type} "
                            f"with amount {lock_event.amount_out} for correlation_id={correlation_id}."
                        ),
                        created_at_ts=mint_event.timestamp,
                    ))
    return alerts

def over_release(bridge: str) -> list[DetectionAlert]:
    grouped_events = _fetch_event_pairs(bridge, BRIDGE_EVENT_MAP[bridge].burn, BRIDGE_EVENT_MAP[bridge].release)
    alerts = []
    for correlation_id, events in grouped_events.items():
        if not events["destination"] or not events["source"]:
            continue
        for release_event in events["destination"]:
            for burn_event in events["source"]:
                if release_event.amount_out is not None and burn_event.amount_out is not None and release_event.amount_out > burn_event.amount_out:
                    alerts.append(DetectionAlert(
                        signature_type=SignatureType.OVER_RELEASE,
                        severity=AlertSeverity.LOW,
                        bridge=bridge,
                        correlation_id=correlation_id,
                        correlation_type=burn_event.correlation_type,
                        src_event_id=burn_event.id,
                        dst_event_id=release_event.id,
                        title=f"{bridge}: over-release detected",
                        description=(
                            f"Found release event {release_event.event_type} with amount {release_event.amount_out} "
                            f"which is greater than the corresponding burn event {burn_event.event_type} "
                            f"with amount {burn_event.amount_out} for correlation_id={correlation_id}."
                        ),
                        created_at_ts=release_event.timestamp,
                    ))
    return alerts

def proof_replay(bridge: str, source: NormalizedEventType, destination: NormalizedEventType) -> list[DetectionAlert]:
    grouped_events = _fetch_event_pairs(bridge, source, destination)
    # check if the same lock event is used for multiple mint events (potential proof replay attack)
    alerts = []
    for correlation_id, events in grouped_events.items():
        if len(events["source"]) == 1 and len(events["destination"]) > 1:

            # #######################################################################################
            # TODO: check if it's possible to have multiple locks and multiple mints for the same id,
            # and still be in normal behaviour
            # #######################################################################################
            
            lock_event = _pick_first(events["source"])
            mint_events = events["destination"]
            for mint_event in mint_events:
                alerts.append(DetectionAlert(
                    signature_type=SignatureType.PROOF_REPLAY,
                    severity=AlertSeverity.LOW,
                    bridge=bridge,
                    correlation_id=correlation_id,
                    correlation_type=lock_event.correlation_type,
                    src_event_id=lock_event.id,
                    dst_event_id=mint_event.id,
                    title=f"{bridge}: potential proof replay attack detected",
                    description=(
                        f"Found multiple mint / release events corresponding to the same lock / burn event {lock_event.event_type} "
                        f"with correlation_id={correlation_id}, which may indicate a proof replay attack."
                    ),
                    created_at_ts=mint_event.timestamp,
                ))
    return alerts


def check_all_signatures(bridge: str):
    alerts = []
    
    alerts.extend(lock_without_mint(bridge))
    alerts.extend(mint_without_lock(bridge))
    alerts.extend(over_mint(bridge))
    alerts.extend(over_release(bridge))
    alerts.extend(proof_replay(bridge, BRIDGE_EVENT_MAP[bridge].lock, BRIDGE_EVENT_MAP[bridge].mint))
    alerts.extend(proof_replay(bridge, BRIDGE_EVENT_MAP[bridge].burn, BRIDGE_EVENT_MAP[bridge].release))

    return alerts


"""
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
"""