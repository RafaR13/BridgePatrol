from __future__ import annotations

# ruff: noqa: E402

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
from evaluation.metrics import (
    build_confusion_matrix,
    calculate_bridge_baseline_metrics,
    calculate_metrics,
    load_expected_labels,
)
from evaluation.result_paths import build_evaluation_result_paths
from evaluation.reporting import EvaluationReporter, write_json_summary
from tests.evaluation.evaluation_utils import (
    bridge_scope,
    complete_cctx_units_by_bridge,
    count_cctx_for_bridges,
    evaluation_windows_for_bridges,
    resolve_bridge_selection,
    predicted_positive_units_by_bridge,
    summarize_alerts,
    total_count,
)


BASELINE_EXPECTED_POSITIVE_BRIDGES = {
    "chainswap",
    "meter.io",
    "pnetwork",
    "thorchain",
}
PARTIAL_EXPECTED_POSITIVE_UNITS_BY_BRIDGE = {
    "qubit": {f"cctx:qubit:cctx_{index}" for index in range(4, 20)}
}
PARTIAL_EXPECTED_POSITIVE_COUNTS_BY_BRIDGE = {
    "nomad": 382,
    "ronin": 2,
}
PARTIAL_EXPECTED_POSITIVE_WINDOWS_BY_BRIDGE = {
    "nomad": {"start_ts": 1659312000, "end_ts": 1659558228},
    "ronin": {"start_ts": 1647820871, "end_ts": 1648166400},
}
INCOMPLETE_CCTX_SIGNATURE_TYPES = {"LOCK_WITHOUT_MINT", "MINT_WITHOUT_LOCK"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run correctness evaluation.")
    parser.add_argument("--bridge", required=True, help="Bridge name, or 'all'.")
    parser.add_argument(
        "--exclude-bridge",
        action="append",
        default=[],
        help="Bridge to exclude from the selected scope. Can be passed multiple times.",
    )
    parser.add_argument(
        "--labels",
        required=False,
        help=(
            "CSV with bridge,signature_type,correlation_id,expected_alert. "
            "When omitted, bridge-level baseline labels are used."
        ),
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
        help="Optional JSON file for the final global correctness summary.",
    )
    parser.add_argument(
        "--markdown-output",
        default=None,
        help="Optional Markdown file for the final global correctness summary.",
    )
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--start-ts", type=int, default=None)
    parser.add_argument("--end-ts", type=int, default=None)
    parser.add_argument("--persist-alerts", action="store_true")
    return parser.parse_args()


def filter_records_for_bridge(records: list[dict], bridge: str) -> list[dict]:
    return [
        record
        for record in records
        if record.get("bridge") == bridge
        or bridge in (record.get("bridges") or [])
    ]


def windows_overlap(left: dict[str, int], right: dict[str, int]) -> bool:
    return left["start_ts"] <= right["end_ts"] and right["start_ts"] <= left["end_ts"]


def expected_positive_counts_for_bridges(
    bridges: list[str],
    evaluation_windows: dict[str, dict],
) -> dict[str, int]:
    return {
        bridge: PARTIAL_EXPECTED_POSITIVE_COUNTS_BY_BRIDGE[bridge]
        for bridge in bridges
        if bridge in PARTIAL_EXPECTED_POSITIVE_COUNTS_BY_BRIDGE
        and any(
            windows_overlap(window, PARTIAL_EXPECTED_POSITIVE_WINDOWS_BY_BRIDGE[bridge])
            for window in evaluation_windows[bridge]["windows"]
        )
    }


def build_correctness_summary(
    args: argparse.Namespace,
    bridges: list[str],
    alerts: list,
    evaluation_windows: dict[str, dict[str, int]],
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
        windows={
            bridge: window["windows"]
            for bridge, window in evaluation_windows.items()
            if bridge in bridges
        },
    )
    cctx_analyzed = total_count(cctx_by_bridge)
    single_bridge_window = evaluation_windows[bridges[0]] if len(bridges) == 1 else None
    summary_start_ts = (
        single_bridge_window["start_ts"]
        if single_bridge_window is not None and len(single_bridge_window["windows"]) == 1
        else args.start_ts
    )
    summary_end_ts = (
        single_bridge_window["end_ts"]
        if single_bridge_window is not None and len(single_bridge_window["windows"]) == 1
        else args.end_ts
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
        **summarize_alerts(alerts),
    }

    if args.labels:
        labels_path = Path(args.labels)
        selected_bridges = set(bridges)
        labels = {
            key: expected
            for key, expected in load_expected_labels(labels_path).items()
            if key.bridge in selected_bridges
        }
        matrix = build_confusion_matrix(alerts, labels)
        summary["label_count"] = len(labels)
        summary["metrics"] = calculate_metrics(matrix)
        summary["labels_source"] = str(labels_path)
        summary["metrics_mode"] = "labels_csv"
        return summary

    summary["label_count"] = 0
    summary["labels_source"] = None
    summary["metrics_mode"] = "bridge_attack_baseline"
    summary["baseline_expected_positive_bridges"] = sorted(BASELINE_EXPECTED_POSITIVE_BRIDGES)
    summary["partial_expected_positive_units_by_bridge"] = {
        bridge: len(units)
        for bridge, units in sorted(PARTIAL_EXPECTED_POSITIVE_UNITS_BY_BRIDGE.items())
        if bridge in bridges
    }
    expected_positive_counts = expected_positive_counts_for_bridges(
        bridges,
        evaluation_windows,
    )
    summary["partial_expected_positive_counts_by_bridge"] = expected_positive_counts
    predicted_positive_units = predicted_positive_units_by_bridge(alerts)
    predicted_incomplete_units = predicted_positive_units_by_bridge(
        alerts,
        signature_types=INCOMPLETE_CCTX_SIGNATURE_TYPES,
    )
    complete_cctx_units = complete_cctx_units_by_bridge(
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
        windows={
            bridge: window["windows"]
            for bridge, window in evaluation_windows.items()
            if bridge in bridges
        },
    )
    summary["predicted_positive_units_by_bridge"] = {
        bridge: len(units)
        for bridge, units in sorted(predicted_positive_units.items())
    }
    predicted_positive_complete_counts = {
        bridge: len(
            predicted_positive_units.get(bridge, set())
            - predicted_incomplete_units.get(bridge, set())
        )
        for bridge in bridges
    }
    summary["predicted_positive_complete_cctx_units_by_bridge"] = {
        bridge: predicted_positive_complete_counts.get(bridge, 0)
        for bridge in bridges
    }
    summary["predicted_positive_extra_units_by_bridge"] = {
        bridge: len(predicted_incomplete_units.get(bridge, set()))
        for bridge in bridges
    }
    summary["metrics"] = calculate_bridge_baseline_metrics(
        predicted_positive_units_by_bridge=predicted_positive_units,
        cctx_analyzed_by_bridge=cctx_by_bridge,
        expected_positive_bridges=BASELINE_EXPECTED_POSITIVE_BRIDGES,
        complete_cctx_units_by_bridge=complete_cctx_units,
        predicted_positive_complete_counts_by_bridge=predicted_positive_complete_counts,
        expected_positive_units_by_bridge={
            bridge: units
            for bridge, units in PARTIAL_EXPECTED_POSITIVE_UNITS_BY_BRIDGE.items()
            if bridge in bridges
        },
        expected_positive_counts_by_bridge=expected_positive_counts,
    )
    summary["metrics_note"] = (
        "Bridge-level baseline: chainswap, meter.io, pnetwork, and thorchain CCTX "
        "are expected positives; Qubit expects only cctx_4 through cctx_19 as "
        "positives; Ronin 2022 expects 2 attack units; Nomad 2022-08 expects "
        "382 attack units; every other analyzed unit is an expected negative. "
        "Alerts are deduplicated to CCTX-level units when normalized event cctx_id "
        "is available. For benign bridges, predicted positive units outside the complete "
        "CCTX table are counted as extra false positives without reducing true negatives "
        "from complete valid CCTX."
    )
    return summary


def write_correctness_artifacts(
    result_paths,
    run_id: str,
    bridge_name: str,
    summary: dict,
    records: list[dict],
    json_override: str | None = None,
    markdown_override: str | None = None,
) -> tuple[Path, Path]:
    summary_record = {"run_id": run_id, "event_type": "correctness_summary", **summary}
    json_path = Path(json_override) if json_override else result_paths.artifact_path(bridge_name, "json")
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
            "Correctness Evaluation Report"
            if bridge_name == "global"
            else f"Correctness Evaluation Report - {bridge_name}"
        ),
        raw_jsonl_path=result_paths.details_jsonl,
    )
    return json_path, markdown_path


def main() -> int:
    args = parse_args()
    from signature_detection.runners.run_signature_detection import run_for_bridges

    run_id = args.run_id or str(uuid4())
    result_paths = build_evaluation_result_paths(
        results_dir=args.results_dir,
        details_output=args.output,
        evaluation_type="correctness",
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

    alerts = []
    bridge_summaries = {}
    for bridge in bridges:
        bridge_window = evaluation_windows[bridge]
        bridge_alerts = []
        for window in bridge_window["windows"]:
            bridge_alerts.extend(
                run_for_bridges(
                    [bridge],
                    start_ts=window["start_ts"],
                    end_ts=window["end_ts"],
                    persist=args.persist_alerts,
                    report_path=result_paths.details_jsonl,
                    run_id=run_id,
                )
            )
        alerts.extend(bridge_alerts)
        bridge_summary = build_correctness_summary(
            args,
            [bridge],
            bridge_alerts,
            evaluation_windows,
        )
        bridge_summaries[bridge] = bridge_summary
        reporter.write("correctness_bridge_summary", bridge_summary)
        records = load_run_records(result_paths.details_jsonl, run_id)
        write_correctness_artifacts(
            result_paths,
            run_id,
            bridge,
            bridge_summary,
            filter_records_for_bridge(records, bridge),
        )

    summary = build_correctness_summary(args, bridges, alerts, evaluation_windows)
    summary["bridge_summaries"] = bridge_summaries

    reporter.write("correctness_summary", summary)
    global_json, global_markdown = write_correctness_artifacts(
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
    print(f"metrics={summary['metrics']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
