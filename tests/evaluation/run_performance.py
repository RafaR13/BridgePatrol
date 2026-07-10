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

from evaluation.reporting import EvaluationReporter
from tests.evaluation.evaluation_utils import (
    bridge_scope,
    count_cctx_for_bridges,
    normalization_skip_reason,
    resolve_bridge_selection,
    should_run_normalization,
    summarize_alerts,
    total_count,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run performance evaluation.")
    parser.add_argument("--bridge", required=True, help="Bridge name, or 'all'.")
    parser.add_argument("--output", default="tests/evaluation/results/evaluation.jsonl")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--start-ts", type=int, default=None)
    parser.add_argument("--end-ts", type=int, default=None)
    parser.add_argument("--skip-normalization", action="store_true")
    parser.add_argument("--persist-alerts", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from db.database import Base, engine
    from normalization.runners.runner import run_normalization_for_bridge
    from signature_detection.runners.run_signature_detection import run_for_bridges

    Base.metadata.create_all(bind=engine)

    run_id = args.run_id or str(uuid4())
    reporter = EvaluationReporter(args.output, run_id=run_id)
    bridges = resolve_bridge_selection(args.bridge)

    normalization_results = []
    for bridge in bridges:
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
            reporter.write("normalization_skipped", payload)
            continue

        normalization_results.append(
            run_normalization_for_bridge(
                bridge,
                report_path=args.output,
                run_id=run_id,
            )
        )

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
        "normalization": normalization_results,
        **summarize_alerts(alerts),
    }
    if cctx_analyzed:
        summary["alerts_per_cctx"] = len(alerts) / cctx_analyzed
    reporter.write("performance_summary", summary)

    print(f"run_id={run_id}")
    print(f"output={args.output}")
    print(f"bridges={','.join(bridges)}")
    print(f"cctx_analyzed={cctx_analyzed}")
    print(f"alerts_detected={len(alerts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
