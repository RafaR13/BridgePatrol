def lock_without_mint(bridge: str) -> list[DetectionAlert]:
    grouped_events = _fetch_event_pairs(bridge, BRIDGE_EVENT_MAP[bridge].lock, BRIDGE_EVENT_MAP[bridge].mint)
    alerts = []
    for correlation_id, events in grouped_events.items():
        if events["source"] and not events["destination"]:
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