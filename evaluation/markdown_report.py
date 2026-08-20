from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def default_markdown_path(jsonl_path: str | Path, run_id: str) -> Path:
    path = Path(jsonl_path)
    return path.with_name(f"{path.stem}_{run_id}.md")


def write_markdown_report_from_jsonl(
    jsonl_path: str | Path,
    markdown_path: str | Path,
    run_id: str,
    title: str,
) -> Path:
    records = load_run_records(jsonl_path, run_id)
    markdown = build_markdown_report(records, title=title, raw_jsonl_path=Path(jsonl_path))

    output_path = Path(markdown_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    return output_path


def write_markdown_report_from_records(
    records: list[dict[str, Any]],
    markdown_path: str | Path,
    title: str,
    raw_jsonl_path: str | Path,
) -> Path:
    markdown = build_markdown_report(records, title=title, raw_jsonl_path=Path(raw_jsonl_path))

    output_path = Path(markdown_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    return output_path


def load_run_records(jsonl_path: str | Path, run_id: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    path = Path(jsonl_path)
    if not path.exists():
        return records

    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            if record.get("run_id") == run_id:
                records.append(record)
    return records


def build_markdown_report(
    records: list[dict[str, Any]],
    title: str,
    raw_jsonl_path: Path,
) -> str:
    latest_summary = _latest_summary(records)
    run_id = latest_summary.get("run_id") or _first_value(records, "run_id") or ""

    lines = [
        f"# {title}",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Run ID | `{_escape(run_id)}` |",
        f"| Raw JSONL | `{_escape(str(raw_jsonl_path))}` |",
        f"| Bridge scope | {_format_value(latest_summary.get('bridge'))} |",
        f"| Bridges | {_format_value(latest_summary.get('bridges'))} |",
        f"| CCTX analyzed | {_format_value(latest_summary.get('cctx_analyzed'))} |",
        f"| Alerts detected | {_format_value(latest_summary.get('alerts_detected'))} |",
        f"| Start timestamp | {_format_value(latest_summary.get('start_ts'))} |",
        f"| End timestamp | {_format_value(latest_summary.get('end_ts'))} |",
        "",
    ]

    lines.extend(_normalization_section(records, latest_summary))
    lines.extend(_performance_section(records))
    lines.extend(_alerts_section(latest_summary))
    lines.extend(_correctness_section(latest_summary))

    return "\n".join(lines).rstrip() + "\n"


def _latest_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    summary_types = {"performance_summary", "correctness_summary"}
    summaries = [record for record in records if record.get("event_type") in summary_types]
    if summaries:
        return summaries[-1]
    return records[-1] if records else {}


def _normalization_section(
    records: list[dict[str, Any]],
    latest_summary: dict[str, Any],
) -> list[str]:
    total_timers = [record for record in records if record.get("event_type") == "normalization_total"]
    table_timers = [record for record in records if record.get("event_type") == "normalization_table_timer"]
    table_summaries = [
        record for record in records if record.get("event_type") == "normalization_table_summary"
    ]
    skipped = [record for record in records if record.get("event_type") == "normalization_skipped"]

    lines = ["## Normalization", ""]
    normalization_metrics = latest_summary.get("normalization_metrics") or {}
    normalization_totals = normalization_metrics.get("total") or {}
    normalization_by_bridge = normalization_metrics.get("by_bridge") or {}

    if normalization_totals:
        lines.extend(
            _table(
                [
                    "Scope",
                    "Bridges",
                    "Jobs",
                    "Tables",
                    "Rows seen",
                    "Inserted",
                    "Skipped",
                    "Duration ms",
                    "ms / row",
                ],
                [
                    [
                        "total",
                        normalization_totals.get("bridges"),
                        normalization_totals.get("jobs"),
                        normalization_totals.get("tables"),
                        normalization_totals.get("rows_seen"),
                        normalization_totals.get("inserted"),
                        normalization_totals.get("skipped"),
                        _format_ms(normalization_totals.get("duration_ms")),
                        _format_ms(normalization_totals.get("ms_per_row_seen")),
                    ]
                ],
            )
        )
        lines.append("")

    if normalization_by_bridge:
        lines.extend(
            _table(
                [
                    "Bridge",
                    "Jobs",
                    "Tables",
                    "Rows seen",
                    "Inserted",
                    "Skipped",
                    "Duration ms",
                    "ms / row",
                ],
                [
                    [
                        bridge,
                        metrics.get("jobs"),
                        metrics.get("tables"),
                        metrics.get("rows_seen"),
                        metrics.get("inserted"),
                        metrics.get("skipped"),
                        _format_ms(metrics.get("duration_ms")),
                        _format_ms(metrics.get("ms_per_row_seen")),
                    ]
                    for bridge, metrics in sorted(normalization_by_bridge.items())
                ],
            )
        )
        lines.append("")

    if (
        not normalization_totals
        and not total_timers
        and not table_timers
        and not table_summaries
        and not skipped
    ):
        return lines + ["No normalization records for this run.", ""]

    if skipped:
        lines.extend(
            _table(
                ["Bridge", "Skipped", "Reason"],
                [
                    [
                        record.get("bridge"),
                        record.get("skipped"),
                        record.get("reason"),
                    ]
                    for record in skipped
                ],
            )
        )
        lines.append("")

    if total_timers:
        lines.extend(
            _table(
                ["Bridge", "Jobs", "Duration ms"],
                [
                    [
                        record.get("bridge"),
                        record.get("jobs"),
                        _format_ms(record.get("duration_ms")),
                    ]
                    for record in total_timers
                ],
            )
        )
        lines.append("")

    if table_timers or table_summaries:
        summaries_by_key = {
            (record.get("bridge"), record.get("raw_table")): record
            for record in table_summaries
        }
        rows = []
        for record in table_timers:
            summary = summaries_by_key.get((record.get("bridge"), record.get("raw_table")), {})
            rows.append(
                [
                    record.get("bridge"),
                    record.get("raw_table"),
                    summary.get("rows_seen"),
                    summary.get("inserted"),
                    summary.get("skipped"),
                    _format_ms(record.get("duration_ms")),
                ]
            )
        lines.extend(
            _table(
                ["Bridge", "Raw table", "Rows seen", "Inserted", "Skipped", "Duration ms"],
                rows,
            )
        )
        lines.append("")

    return lines


def _performance_section(records: list[dict[str, Any]]) -> list[str]:
    check_timers = [record for record in records if record.get("event_type") == "signature_check_timer"]
    detection_timers = [
        record for record in records if record.get("event_type") == "signature_detection_total_timer"
    ]
    bridge_summaries = [
        record for record in records if record.get("event_type") == "signature_detection_bridge_summary"
    ]

    lines = ["## Signature Detection Timings", ""]
    if detection_timers:
        lines.extend(
            _table(
                ["Bridge", "Duration ms", "Start timestamp", "End timestamp"],
                [
                    [
                        record.get("bridge"),
                        _format_ms(record.get("duration_ms")),
                        record.get("start_ts"),
                        record.get("end_ts"),
                    ]
                    for record in detection_timers
                ],
            )
        )
        lines.append("")

    if check_timers:
        lines.extend(
            _table(
                [
                    "Bridge",
                    "Signature check",
                    "Unit",
                    "CCTX",
                    "Event groups",
                    "Events/logs",
                    "Transactions",
                    "Duration ms",
                    "ms/CCTX",
                    "ms/event",
                    "ms/tx",
                ],
                [
                    [
                        record.get("bridge"),
                        record.get("signature_check"),
                        record.get("unit_type"),
                        record.get("cctx_analyzed"),
                        record.get("event_groups_analyzed"),
                        record.get("events_analyzed"),
                        record.get("transactions_analyzed"),
                        _format_ms(record.get("duration_ms")),
                        _format_ms(record.get("ms_per_cctx")),
                        _format_ms(record.get("ms_per_event")),
                        _format_ms(record.get("ms_per_transaction")),
                    ]
                    for record in check_timers
                ],
            )
        )
        lines.append("")

    if bridge_summaries:
        lines.extend(
            _table(
                ["Bridge", "Normalized events analyzed", "Alerts detected"],
                [
                    [
                        record.get("bridge"),
                        record.get("normalized_events_analyzed"),
                        record.get("alerts_detected"),
                    ]
                    for record in bridge_summaries
                ],
            )
        )
        lines.append("")

    if not detection_timers and not check_timers and not bridge_summaries:
        lines.append("No signature detection timing records for this run.")
        lines.append("")

    return lines


def _alerts_section(summary: dict[str, Any]) -> list[str]:
    lines = ["## Alert Summary", ""]

    by_bridge = summary.get("alerts_by_bridge") or {}
    by_signature = summary.get("alerts_by_signature_type") or {}
    by_cctx = summary.get("alerts_by_cctx") or {}

    if by_bridge:
        lines.extend(_table(["Bridge", "Alerts"], sorted(by_bridge.items())))
        lines.append("")

    if by_cctx:
        rows = []
        for bridge, cctxs in sorted(by_cctx.items()):
            for cctx_id, cctx_summary in sorted(cctxs.items()):
                rows.append(
                    [
                        bridge,
                        cctx_id,
                        cctx_summary.get("alert_count"),
                        _format_signature_counts(cctx_summary.get("signature_types") or {}),
                    ]
                )
        lines.extend(_table(["Bridge", "CCTX", "Alerts", "Signature types"], rows))
        lines.append("")

    if by_signature:
        lines.extend(_table(["Signature type", "Alerts"], sorted(by_signature.items())))
        lines.append("")

    if not by_bridge and not by_signature and not by_cctx:
        lines.append("No alerts detected.")
        lines.append("")

    cctx_by_bridge = summary.get("cctx_analyzed_by_bridge") or {}
    if cctx_by_bridge:
        rows = []
        for bridge, cctx_count in sorted(cctx_by_bridge.items()):
            alerts = by_bridge.get(bridge, 0)
            alerts_per_cctx = None if cctx_count in (None, 0) else alerts / cctx_count
            rows.append([bridge, cctx_count, alerts, _format_float(alerts_per_cctx)])
        lines.extend(_table(["Bridge", "CCTX analyzed", "Alerts", "Alerts / CCTX"], rows))
        lines.append("")

    return lines


def _format_signature_counts(counts: dict[str, Any]) -> str:
    parts = []
    for signature_type, count in sorted(counts.items()):
        parts.append(str(signature_type) if count == 1 else f"{signature_type} ({count})")
    return ", ".join(parts)


def _correctness_section(summary: dict[str, Any]) -> list[str]:
    metrics = summary.get("metrics")
    lines = ["## Correctness Metrics", ""]

    if summary.get("metrics_mode") is not None:
        lines.append(f"Metrics mode: `{_escape(str(summary.get('metrics_mode')))}`")
    if summary.get("labels_source") is not None:
        lines.append(f"Labels source: `{_escape(str(summary.get('labels_source')))}`")
    if summary.get("baseline_expected_positive_bridges") is not None:
        lines.append(
            "Baseline expected positive bridges: "
            f"{_format_value(summary.get('baseline_expected_positive_bridges'))}"
        )
    if summary.get("metrics_mode") is not None or summary.get("labels_source") is not None:
        lines.append("")

    expected_by_signature = summary.get("expected_positive_signature_counts_by_bridge") or {}
    if expected_by_signature:
        lines.extend(
            _table(
                ["Bridge", "Signature type", "Expected alerts"],
                [
                    [bridge, signature_type, count]
                    for bridge, counts_by_signature in sorted(expected_by_signature.items())
                    for signature_type, count in sorted(counts_by_signature.items())
                ],
            )
        )
        lines.append("")

    predicted_by_signature = summary.get("predicted_positive_units_by_bridge_signature") or {}
    if predicted_by_signature:
        lines.extend(
            _table(
                ["Bridge", "Signature type", "Predicted positive units"],
                [
                    [bridge, signature_type, count]
                    for bridge, counts_by_signature in sorted(predicted_by_signature.items())
                    for signature_type, count in sorted(counts_by_signature.items())
                ],
            )
        )
        lines.append("")

    predicted_units = summary.get("predicted_positive_units_by_bridge") or {}
    if predicted_units:
        complete_predicted_units = (
            summary.get("predicted_positive_complete_cctx_units_by_bridge") or {}
        )
        extra_predicted_units = summary.get("predicted_positive_extra_units_by_bridge") or {}
        lines.extend(
            _table(
                [
                    "Bridge",
                    "Predicted positive units",
                    "On complete CCTX",
                    "Extra/incomplete units",
                ],
                [
                    [
                        bridge,
                        count,
                        complete_predicted_units.get(bridge),
                        extra_predicted_units.get(bridge),
                    ]
                    for bridge, count in sorted(predicted_units.items())
                ],
            )
        )
        lines.append("")

    if not metrics:
        note = summary.get("metrics_note") or "No correctness labels were provided for this run."
        return lines + [str(note), ""]

    confusion_rows = [
        ["True positives", metrics.get("true_positives")],
        ["False positives", metrics.get("false_positives")],
        ["True negatives", metrics.get("true_negatives")],
        ["False negatives", metrics.get("false_negatives")],
    ]
    lines.extend(_table(["Class", "Count"], confusion_rows))
    lines.append("")

    metric_rows = [
        ["Accuracy", _format_float(metrics.get("accuracy"))],
        ["Precision", _format_float(metrics.get("precision"))],
        ["Recall", _format_float(metrics.get("recall"))],
        ["False positive rate", _format_float(metrics.get("false_positive_rate"))],
    ]
    lines.extend(_table(["Metric", "Value"], metric_rows))
    lines.append("")

    if summary.get("label_count") is not None:
        lines.append(f"Labels used: {_format_value(summary.get('label_count'))}")
        lines.append("")

    if summary.get("metrics_note"):
        lines.append(str(summary.get("metrics_note")))
        lines.append("")

    return lines


def _table(headers: list[str], rows: list[list[Any]] | list[tuple[Any, ...]]) -> list[str]:
    lines = [
        "| " + " | ".join(_escape(header) for header in headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_format_value(value) for value in row) + " |")
    return lines


def _format_value(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return _format_float(value)
    if isinstance(value, (list, tuple, set)):
        return ", ".join(_escape(str(item)) for item in value) if value else "-"
    if isinstance(value, dict):
        return _escape(json.dumps(value, default=str, sort_keys=True))
    return _escape(str(value))


def _format_ms(value: Any) -> str:
    if value is None:
        return "-"
    return f"{float(value):.3f}"


def _format_float(value: Any) -> str:
    if value is None:
        return "-"
    return f"{float(value):.6f}"


def _escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _first_value(records: list[dict[str, Any]], key: str) -> Any:
    for record in records:
        if key in record:
            return record[key]
    return None
