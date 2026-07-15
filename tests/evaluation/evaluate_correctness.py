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

from evaluation.markdown_report import default_markdown_path, write_markdown_report_from_jsonl
from evaluation.metrics import (
    build_confusion_matrix,
    calculate_bridge_baseline_metrics,
    calculate_metrics,
    load_expected_labels,
)
from evaluation.reporting import EvaluationReporter
from tests.evaluation.evaluation_utils import (
    bridge_scope,
    count_cctx_for_bridges,
    resolve_bridge_selection,
    predicted_positive_units_by_bridge,
    summarize_alerts,
    total_count,
)


BASELINE_EXPECTED_POSITIVE_BRIDGES = {"meter.io", "pnetwork", "thorchain", "qubit"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run correctness evaluation.")
    parser.add_argument("--bridge", required=True, help="Bridge name, or 'all'.")
    parser.add_argument(
        "--labels",
        required=False,
        help=(
            "CSV with bridge,signature_type,correlation_id,expected_alert. "
            "When omitted, bridge-level baseline labels are used."
        ),
    )
    parser.add_argument("--output", default="tests/evaluation/results/evaluation.jsonl")
    parser.add_argument("--markdown-output", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--start-ts", type=int, default=None)
    parser.add_argument("--end-ts", type=int, default=None)
    parser.add_argument("--persist-alerts", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from signature_detection.runners.run_signature_detection import run_for_bridges

    run_id = args.run_id or str(uuid4())
    reporter = EvaluationReporter(args.output, run_id=run_id)
    bridges = resolve_bridge_selection(args.bridge)

    alerts = run_for_bridges(
        bridges,
        start_ts=args.start_ts,
        end_ts=args.end_ts,
        persist=args.persist_alerts,
        report_path=args.output,
        run_id=run_id,
    )

    cctx_by_bridge = count_cctx_for_bridges(
        bridges,
        start_ts=args.start_ts,
        end_ts=args.end_ts,
    )
    cctx_analyzed = total_count(cctx_by_bridge)
    summary = {
        "bridge": bridge_scope(bridges),
        "bridges": bridges,
        "start_ts": args.start_ts,
        "end_ts": args.end_ts,
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
    else:
        summary["label_count"] = 0
        summary["labels_source"] = None
        summary["metrics_mode"] = "bridge_attack_baseline"
        summary["baseline_expected_positive_bridges"] = sorted(BASELINE_EXPECTED_POSITIVE_BRIDGES)
        predicted_positive_units = predicted_positive_units_by_bridge(alerts)
        summary["predicted_positive_units_by_bridge"] = {
            bridge: len(units)
            for bridge, units in sorted(predicted_positive_units.items())
        }
        summary["metrics"] = calculate_bridge_baseline_metrics(
            predicted_positive_units_by_bridge=predicted_positive_units,
            cctx_analyzed_by_bridge=cctx_by_bridge,
            expected_positive_bridges=BASELINE_EXPECTED_POSITIVE_BRIDGES,
        )
        summary["metrics_note"] = (
            "Bridge-level baseline: meter.io, pnetwork, thorchain, and qubit CCTX "
            "are expected positives; every other bridge CCTX is an expected negative. "
            "Alerts are deduplicated to CCTX-level units when normalized event cctx_id "
            "is available."
        )

    reporter.write("correctness_summary", summary)
    markdown_output = args.markdown_output or default_markdown_path(args.output, run_id)
    write_markdown_report_from_jsonl(
        jsonl_path=args.output,
        markdown_path=markdown_output,
        run_id=run_id,
        title="Correctness Evaluation Report",
    )

    print(f"run_id={run_id}")
    print(f"output={args.output}")
    print(f"markdown_output={markdown_output}")
    print(f"bridges={','.join(bridges)}")
    print(f"cctx_analyzed={cctx_analyzed}")
    print(f"alerts_detected={len(alerts)}")
    print(f"metrics={summary['metrics']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
