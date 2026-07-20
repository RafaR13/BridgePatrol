from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from signature_detection.constants import Bridges


ALL_BRIDGE = "all"
MANUAL_NORMALIZATION_BRIDGES = {"meter.io", "pnetwork", "qubit", "thorchain", "wormhole"}
MANUAL_TRANSACTION_ONLY_BRIDGES = {"chainswap"}
NO_NORMALIZATION_JOB_BRIDGES = {"stargate"}
EXTRA_EVALUATION_BRIDGES = {"wormhole"}
EVALUATION_START_TS = 1735689600  # 2025-01-01 00:00:00 UTC
EVALUATION_END_TS = 1735776000  # 2025-01-02 00:00:00 UTC
EVALUATION_WINDOWS_BY_BRIDGE = {
    "across": (1764547200, 1764550800),  # 2025-12-01 00:00:00..01:00:00 UTC
    "ccip": (1735689600, 1735732800),  # 2025-01-01 00:00:00..12:00:00 UTC
    "cctp": (1735689600, 1735776000),  # 2025-01-01 00:00:00..2025-01-02 00:00:00 UTC
    "debridge": (1733011200, 1733014800),  # 2024-12-01 00:00:00..01:00:00 UTC
    "mayan": (1741219200, 1741262400),  # 2025-03-06 00:00:00..12:00:00 UTC
    "nomad": (1654041600, 1654128000),  # 2022-06-01 00:00:00..2022-06-02 00:00:00 UTC
    "omnibridge": (1735689600, 1735776000),  # 2025-01-01 00:00:00..2025-01-02 00:00:00 UTC
    "polygon": (1735689600, 1735776000),  # 2025-01-01 00:00:00..2025-01-02 00:00:00 UTC
    "ronin": (1735689600, 1735776000),  # 2025-01-01 00:00:00..2025-01-02 00:00:00 UTC
    "chainswap": (1625944500, 1625946900),  # 2021-07-10 19:15:00..19:55:00 UTC
}


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
    if bridge in MANUAL_TRANSACTION_ONLY_BRIDGES:
        return "manual_transaction_only_dataset"
    if bridge in NO_NORMALIZATION_JOB_BRIDGES:
        return "no_normalization_jobs"
    return None


def bridge_scope(bridges: list[str]) -> str:
    return ALL_BRIDGE if len(bridges) != 1 else bridges[0]


def evaluation_window_for_bridge(
    bridge: str,
    start_ts: int | None = None,
    end_ts: int | None = None,
) -> tuple[int, int]:
    default_start_ts, default_end_ts = EVALUATION_WINDOWS_BY_BRIDGE.get(
        bridge,
        (EVALUATION_START_TS, EVALUATION_END_TS),
    )
    return (
        start_ts if start_ts is not None else default_start_ts,
        end_ts if end_ts is not None else default_end_ts,
    )


def evaluation_windows_for_bridges(
    bridges: list[str],
    start_ts: int | None = None,
    end_ts: int | None = None,
) -> dict[str, dict[str, int]]:
    return {
        bridge: {
            "start_ts": bridge_start_ts,
            "end_ts": bridge_end_ts,
        }
        for bridge in bridges
        for bridge_start_ts, bridge_end_ts in [
            evaluation_window_for_bridge(bridge, start_ts=start_ts, end_ts=end_ts)
        ]
    }


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
    start_ts: int | dict[str, int] | None = None,
    end_ts: int | dict[str, int] | None = None,
) -> dict[str, int | None]:
    return {
        bridge: count_cctx(
            bridge,
            start_ts=start_ts.get(bridge) if isinstance(start_ts, dict) else start_ts,
            end_ts=end_ts.get(bridge) if isinstance(end_ts, dict) else end_ts,
        )
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


def predicted_positive_units_by_bridge(alerts) -> dict[str, set[str]]:
    """Resolve alert predictions to CCTX-level units where possible."""
    event_ids_by_bridge: dict[str, set[int]] = defaultdict(set)
    for alert in alerts:
        bridge = str(alert.bridge)
        for field in ("src_event_id", "dst_event_id"):
            event_id = getattr(alert, field, None)
            if event_id is not None:
                event_ids_by_bridge[bridge].add(event_id)

    cctx_by_bridge_event_id = _load_cctx_ids_for_event_ids(event_ids_by_bridge)

    units_by_bridge: dict[str, set[str]] = defaultdict(set)
    for alert in alerts:
        bridge = str(alert.bridge)
        unit = None
        event_cctx_ids = cctx_by_bridge_event_id.get(bridge, {})
        for field in ("src_event_id", "dst_event_id"):
            event_id = getattr(alert, field, None)
            if event_id is not None and event_cctx_ids.get(event_id):
                unit = f"cctx:{event_cctx_ids[event_id]}"
                break

        if unit is None and getattr(alert, "correlation_id", None):
            unit = f"correlation:{alert.correlation_id}"
        if unit is None:
            signature_type = getattr(alert.signature_type, "value", alert.signature_type)
            unit = (
                f"alert:{signature_type}:"
                f"{getattr(alert, 'src_event_id', None)}:"
                f"{getattr(alert, 'dst_event_id', None)}"
            )

        units_by_bridge[bridge].add(unit)

    return dict(units_by_bridge)


def _load_cctx_ids_for_event_ids(
    event_ids_by_bridge: dict[str, set[int]],
) -> dict[str, dict[int, str | None]]:
    if not event_ids_by_bridge:
        return {}

    from db.database import get_session
    from db.repository.normalized_event.normalized_event_model import get_normalized_event_model

    cctx_by_bridge_event_id: dict[str, dict[int, str | None]] = {}
    session = get_session()
    try:
        for bridge, event_ids in event_ids_by_bridge.items():
            if not event_ids:
                continue
            try:
                model = get_normalized_event_model(bridge)
            except ValueError:
                continue
            rows = (
                session.query(model.id, model.cctx_id)
                .filter(model.id.in_(event_ids))
                .all()
            )
            cctx_by_bridge_event_id[bridge] = {
                event_id: str(cctx_id) if cctx_id is not None else None
                for event_id, cctx_id in rows
            }
    finally:
        session.close()

    return cctx_by_bridge_event_id
