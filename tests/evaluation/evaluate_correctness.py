from __future__ import annotations

import argparse
import sys
from pathlib import Path
from uuid import uuid4

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from evaluation.metrics import build_confusion_matrix, calculate_metrics, load_expected_labels
from evaluation.reporting import EvaluationReporter
from tests.evaluation.evaluation_utils import (
    bridge_scope,
    count_cctx_for_bridges,
    resolve_bridge_selection,
    summarize_alerts,
    total_count,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run correctness evaluation.")
    parser.add_argument("--bridge", required=True, help="Bridge name, or 'all'.")
    parser.add_argument("--labels", required=False, help="CSV with bridge,signature_type,correlation_id,expected_alert")
    parser.add_argument("--output", default="tests/evaluation/results/evaluation.jsonl")
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
        selected_bridges = set(bridges)
        labels = {
            key: expected
            for key, expected in load_expected_labels(args.labels).items()
            if key.bridge in selected_bridges
        }
        matrix = build_confusion_matrix(alerts, labels)
        summary["label_count"] = len(labels)
        summary["metrics"] = calculate_metrics(matrix)
    else:
        summary["metrics"] = None
        summary["metrics_note"] = "Pass --labels to calculate accuracy, precision, recall, and false_positive_rate."

    reporter.write("correctness_summary", summary)

    print(f"run_id={run_id}")
    print(f"output={args.output}")
    print(f"bridges={','.join(bridges)}")
    print(f"cctx_analyzed={cctx_analyzed}")
    print(f"alerts_detected={len(alerts)}")
    print(f"metrics={summary['metrics']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
