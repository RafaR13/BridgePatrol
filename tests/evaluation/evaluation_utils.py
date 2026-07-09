from __future__ import annotations

from collections import Counter
from typing import Any

from signature_detection.constants import Bridges


ALL_BRIDGE = "all"
MANUAL_NORMALIZATION_BRIDGES = {"meter.io", "qubit", "thorchain", "wormhole"}
NO_NORMALIZATION_JOB_BRIDGES = {"stargate"}
EXTRA_EVALUATION_BRIDGES = {"wormhole"}


def supported_evaluation_bridges() -> list[str]:
    bridge_names = {bridge.value for bridge in Bridges} | EXTRA_EVALUATION_BRIDGES
    return sorted(bridge_names)


def resolve_bridge_selection(bridge: str) -> list[str]:
    bridge = bridge.strip().lower()
    if bridge == ALL_BRIDGE:
        return supported_evaluation_bridges()
    if bridge not in supported_evaluation_bridges():
        supported = ", ".join([ALL_BRIDGE, *supported_evaluation_bridges()])
        raise ValueError(f"Unsupported bridge {bridge!r}. Supported values: {supported}")
    return [bridge]


def should_run_normalization(bridge: str) -> bool:
    return normalization_skip_reason(bridge) is None


def normalization_skip_reason(bridge: str) -> str | None:
    if bridge in MANUAL_NORMALIZATION_BRIDGES:
        return "manual_normalized_events_dataset"
    if bridge in NO_NORMALIZATION_JOB_BRIDGES:
        return "no_normalization_jobs"
    return None


def bridge_scope(bridges: list[str]) -> str:
    return ALL_BRIDGE if len(bridges) != 1 else bridges[0]


def count_cctx(
    bridge: str,
    start_ts: int | None = None,
    end_ts: int | None = None,
) -> int | None:
    from sqlalchemy import or_

    from db.database import get_session
    from normalization.runners.runner import CCTX_MODELS

    if bridge not in CCTX_MODELS:
        return None

    model, _ = CCTX_MODELS[bridge]
    session = get_session()
    try:
        query = session.query(model)
        if start_ts is not None or end_ts is not None:
            filters = []
            for field in ("src_timestamp", "dst_timestamp", "refund_timestamp"):
                if not hasattr(model, field):
                    continue
                column = getattr(model, field)
                field_filters = []
                if start_ts is not None:
                    field_filters.append(column >= start_ts)
                if end_ts is not None:
                    field_filters.append(column <= end_ts)
                if field_filters:
                    query_for_field = field_filters[0]
                    for extra_filter in field_filters[1:]:
                        query_for_field = query_for_field & extra_filter
                    filters.append(query_for_field)
            if filters:
                query = query.filter(or_(*filters))
        return query.count()
    finally:
        session.close()


def count_cctx_for_bridges(
    bridges: list[str],
    start_ts: int | None = None,
    end_ts: int | None = None,
) -> dict[str, int | None]:
    return {
        bridge: count_cctx(bridge, start_ts=start_ts, end_ts=end_ts)
        for bridge in bridges
    }


def total_count(values: dict[str, int | None]) -> int | None:
    known_values = [value for value in values.values() if value is not None]
    if not known_values:
        return None
    return sum(known_values)


def summarize_alerts(alerts) -> dict[str, Any]:
    by_signature = Counter(
        str(getattr(alert.signature_type, "value", alert.signature_type))
        for alert in alerts
    )
    by_bridge = Counter(str(alert.bridge) for alert in alerts)
    return {
        "alerts_detected": len(alerts),
        "alerts_by_signature_type": dict(sorted(by_signature.items())),
        "alerts_by_bridge": dict(sorted(by_bridge.items())),
    }
