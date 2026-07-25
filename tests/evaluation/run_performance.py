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
        "normalization": normalization_results,
        **summarize_alerts(alerts),
    }
    if cctx_analyzed:
        summary["alerts_per_cctx"] = len(alerts) / cctx_analyzed
    return summary


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
        if args.skip_normalization or not should_run_normalization(bridge):
            skipped_reason = (
                "requested_by_flag"
                if args.skip_normalization
                else normalization_skip_reason(bridge)
            )
            payload = {
                "bridge": bridge,
                "skipped": True,
                "reason": skipped_reason,
            }
            normalization_results.append(payload)
            bridge_normalization_results.append(payload)
            reporter.write("normalization_skipped", payload)
        else:
            normalization_result = run_normalization_for_bridge(
                bridge,
                report_path=result_paths.details_jsonl,
                run_id=run_id,
            )
            normalization_results.append(normalization_result)
            bridge_normalization_results.append(normalization_result)

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
        bridge_summary = build_performance_summary(
            args,
            [bridge],
            bridge_alerts,
            evaluation_windows,
            bridge_normalization_results,
        )
        bridge_summaries[bridge] = bridge_summary
        reporter.write("performance_bridge_summary", bridge_summary)
        records = load_run_records(result_paths.details_jsonl, run_id)
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
    print(f"alerts_detected={len(alerts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
