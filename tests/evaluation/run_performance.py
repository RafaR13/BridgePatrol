from __future__ import annotations

import argparse
import sys
from pathlib import Path
from uuid import uuid4

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from config.env import load_env_file

load_env_file(REPO_ROOT / ".env")

from evaluation.markdown_report import (
    load_run_records,
    write_markdown_report_from_records,
)
from evaluation.result_paths import build_evaluation_result_paths
from evaluation.reporting import EvaluationReporter, write_json_summary
from tests.evaluation.evaluation_utils import (
    bridge_scope,
    count_cctx_for_bridges,
    evaluation_windows_for_bridges,
    normalization_skip_reason,
    resolve_bridge_selection,
    should_run_normalization,
    summarize_alerts,
    total_count,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run performance evaluation.")
    parser.add_argument("--bridge", required=True, help="Bridge name, or 'all'.")
    parser.add_argument(
        "--phase",
        choices=("all", "normalization", "signature-detection"),
        default="all",
        help="Evaluation phase to run. Defaults to all.",
    )
    parser.add_argument(
        "--exclude-bridge",
        action="append",
        default=[],
        help="Bridge to exclude from the selected scope. Can be passed multiple times.",
    )
    parser.add_argument(
        "--results-dir",
        default=None,
        help=(
            "Directory for this evaluation run. When omitted, a timestamped "
            "evaluation_results_* directory is created."
        ),
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional detailed JSONL output path. Defaults inside the run results directory.",
    )
    parser.add_argument(
        "--summary-output",
        default=None,
        help="Optional JSON file for the final global performance summary.",
    )
    parser.add_argument(
        "--markdown-output",
        default=None,
        help="Optional Markdown file for the final global performance summary.",
    )
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--start-ts", type=int, default=None)
    parser.add_argument("--end-ts", type=int, default=None)
    parser.add_argument("--skip-normalization", action="store_true")
    parser.add_argument("--persist-alerts", action="store_true")
    return parser.parse_args()


def filter_records_for_bridge(records: list[dict], bridge: str) -> list[dict]:
    return [
        record
        for record in records
        if record.get("bridge") == bridge
        or bridge in (record.get("bridges") or [])
    ]


def build_performance_summary(
    args: argparse.Namespace,
    bridges: list[str],
    alerts: list,
    evaluation_windows: dict[str, dict[str, int]],
    normalization_results: list[dict],
    normalization_metrics: dict,
) -> dict:
    cctx_by_bridge = count_cctx_for_bridges(
        bridges,
        start_ts={
            bridge: window["start_ts"]
            for bridge, window in evaluation_windows.items()
            if bridge in bridges
        },
        end_ts={
            bridge: window["end_ts"]
            for bridge, window in evaluation_windows.items()
            if bridge in bridges
        },
    )
    cctx_analyzed = total_count(cctx_by_bridge)
    summary_start_ts = (
        evaluation_windows[bridges[0]]["start_ts"] if len(bridges) == 1 else args.start_ts
    )
    summary_end_ts = (
        evaluation_windows[bridges[0]]["end_ts"] if len(bridges) == 1 else args.end_ts
    )
    summary = {
        "bridge": bridge_scope(bridges),
        "bridges": bridges,
        "start_ts": summary_start_ts,
        "end_ts": summary_end_ts,
        "evaluation_windows_by_bridge": {
            bridge: evaluation_windows[bridge] for bridge in bridges
        },
        "cctx_analyzed": cctx_analyzed,
        "cctx_analyzed_by_bridge": cctx_by_bridge,
        "phase": args.phase,
        "normalization": normalization_results,
        "normalization_metrics": normalization_metrics,
        **summarize_alerts(alerts),
    }
    if cctx_analyzed:
        summary["alerts_per_cctx"] = len(alerts) / cctx_analyzed
    return summary


def summarize_normalization_metrics(records: list[dict]) -> dict:
    by_bridge: dict[str, dict] = {}

    for record in records:
        bridge = record.get("bridge")
        if not bridge:
            continue
        metrics = by_bridge.setdefault(
            bridge,
            {
                "jobs": 0,
                "duration_ms": 0.0,
                "tables": 0,
                "rows_seen": 0,
                "inserted": 0,
                "skipped": 0,
            },
        )

        if record.get("event_type") == "normalization_total":
            metrics["jobs"] += int(record.get("jobs") or 0)
            metrics["duration_ms"] += float(record.get("duration_ms") or 0)
        elif record.get("event_type") == "normalization_table_summary":
            metrics["tables"] += 1
            metrics["rows_seen"] += int(record.get("rows_seen") or 0)
            metrics["inserted"] += int(record.get("inserted") or 0)
            metrics["skipped"] += int(record.get("skipped") or 0)

    totals = {
        "bridges": len(by_bridge),
        "jobs": sum(metrics["jobs"] for metrics in by_bridge.values()),
        "duration_ms": sum(metrics["duration_ms"] for metrics in by_bridge.values()),
        "tables": sum(metrics["tables"] for metrics in by_bridge.values()),
        "rows_seen": sum(metrics["rows_seen"] for metrics in by_bridge.values()),
        "inserted": sum(metrics["inserted"] for metrics in by_bridge.values()),
        "skipped": sum(metrics["skipped"] for metrics in by_bridge.values()),
    }
    totals["ms_per_row_seen"] = (
        None
        if totals["rows_seen"] == 0
        else totals["duration_ms"] / totals["rows_seen"]
    )
    totals["normalized_events_seen"] = totals["rows_seen"]
    totals["normalized_events_inserted"] = totals["inserted"]
    totals["normalized_events_skipped"] = totals["skipped"]

    for metrics in by_bridge.values():
        metrics["ms_per_row_seen"] = (
            None
            if metrics["rows_seen"] == 0
            else metrics["duration_ms"] / metrics["rows_seen"]
        )
        metrics["normalized_events_seen"] = metrics["rows_seen"]
        metrics["normalized_events_inserted"] = metrics["inserted"]
        metrics["normalized_events_skipped"] = metrics["skipped"]

    return {
        "total": totals,
        "by_bridge": dict(sorted(by_bridge.items())),
    }


def should_run_normalization_phase(args: argparse.Namespace, bridge: str) -> bool:
    return (
        args.phase in ("all", "normalization")
        and not args.skip_normalization
        and should_run_normalization(bridge)
    )


def normalization_skip_payload(args: argparse.Namespace, bridge: str) -> dict | None:
    if args.phase == "signature-detection":
        return None
    if args.skip_normalization:
        reason = "requested_by_flag"
    else:
        reason = normalization_skip_reason(bridge)
    if reason is None:
        return None
    return {
        "bridge": bridge,
        "skipped": True,
        "reason": reason,
    }


def write_performance_artifacts(
    result_paths,
    run_id: str,
    bridge_name: str,
    summary: dict,
    records: list[dict],
    json_override: str | None = None,
    markdown_override: str | None = None,
) -> tuple[Path, Path]:
    summary_record = {"run_id": run_id, "event_type": "performance_summary", **summary}
    json_path = (
        Path(json_override)
        if json_override
        else result_paths.artifact_path(bridge_name, "json")
    )
    markdown_path = (
        Path(markdown_override)
        if markdown_override
        else result_paths.artifact_path(bridge_name, "md")
    )
    write_json_summary(json_path, summary_record)
    write_markdown_report_from_records(
        [*records, summary_record],
        markdown_path=markdown_path,
        title=(
            "Performance Evaluation Report"
            if bridge_name == "global"
            else f"Performance Evaluation Report - {bridge_name}"
        ),
        raw_jsonl_path=result_paths.details_jsonl,
    )
    return json_path, markdown_path


def main() -> int:
    args = parse_args()
    from db.database import Base, engine
    from normalization.runners.runner import run_normalization_for_bridge
    from signature_detection.runners.run_signature_detection import run_for_bridges

    Base.metadata.create_all(bind=engine)

    run_id = args.run_id or str(uuid4())
    result_paths = build_evaluation_result_paths(
        results_dir=args.results_dir,
        details_output=args.output,
        evaluation_type="performance",
    )
    reporter = EvaluationReporter(result_paths.details_jsonl, run_id=run_id)
    bridges = resolve_bridge_selection(args.bridge)
    excluded_bridges = {bridge.strip().lower() for bridge in args.exclude_bridge}
    bridges = [bridge for bridge in bridges if bridge not in excluded_bridges]
    if not bridges:
        raise ValueError("No bridges left to evaluate after applying --exclude-bridge.")
    evaluation_windows = evaluation_windows_for_bridges(
        bridges,
        start_ts=args.start_ts,
        end_ts=args.end_ts,
    )

    normalization_results = []
    alerts = []
    bridge_summaries = {}
    for bridge in bridges:
        bridge_normalization_results = []
        skipped_payload = normalization_skip_payload(args, bridge)
        if skipped_payload is not None:
            payload = skipped_payload
            normalization_results.append(payload)
            bridge_normalization_results.append(payload)
            reporter.write("normalization_skipped", payload)
        elif should_run_normalization_phase(args, bridge):
            normalization_result = run_normalization_for_bridge(
                bridge,
                report_path=result_paths.details_jsonl,
                run_id=run_id,
            )
            normalization_results.append(normalization_result)
            bridge_normalization_results.append(normalization_result)

        bridge_alerts = []
        if args.phase in ("all", "signature-detection"):
            bridge_window = evaluation_windows[bridge]
            bridge_alerts = run_for_bridges(
                [bridge],
                start_ts=bridge_window["start_ts"],
                end_ts=bridge_window["end_ts"],
                persist=args.persist_alerts,
                report_path=result_paths.details_jsonl,
                run_id=run_id,
            )
        alerts.extend(bridge_alerts)
        records = load_run_records(result_paths.details_jsonl, run_id)
        bridge_summary = build_performance_summary(
            args,
            [bridge],
            bridge_alerts,
            evaluation_windows,
            bridge_normalization_results,
            summarize_normalization_metrics(filter_records_for_bridge(records, bridge)),
        )
        bridge_summaries[bridge] = bridge_summary
        reporter.write("performance_bridge_summary", bridge_summary)
        write_performance_artifacts(
            result_paths,
            run_id,
            bridge,
            bridge_summary,
            filter_records_for_bridge(records, bridge),
        )

    summary = build_performance_summary(
        args,
        bridges,
        alerts,
        evaluation_windows,
        normalization_results,
        summarize_normalization_metrics(load_run_records(result_paths.details_jsonl, run_id)),
    )
    summary["bridge_summaries"] = bridge_summaries
    reporter.write("performance_summary", summary)
    global_json, global_markdown = write_performance_artifacts(
        result_paths,
        run_id,
        "global",
        summary,
        load_run_records(result_paths.details_jsonl, run_id),
        json_override=args.summary_output,
        markdown_override=args.markdown_output,
    )

    print(f"run_id={run_id}")
    print(f"results_dir={result_paths.directory}")
    print(f"output={result_paths.details_jsonl}")
    print(f"summary_output={global_json}")
    print(f"markdown_output={global_markdown}")
    print(f"bridges={','.join(bridges)}")
    print(f"cctx_analyzed={summary['cctx_analyzed']}")
    print(f"normalization_metrics={summary['normalization_metrics']['total']}")
    print(f"alerts_detected={len(alerts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
