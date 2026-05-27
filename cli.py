# cli.py
import argparse
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from signature_detection.runners.run_signature_detection import run_for_bridge
from normalization.runners.runner import run_normalization_for_bridge


@dataclass(frozen=True)
class CliArgs:
    bridge: str
    blockchains: List[str]
    start_ts: int | None
    end_ts: int | None
    need_extraction: bool
    need_normalization: bool
    store_alerts: bool


class Cli:
    """
    Usage example:
      collector --bridge polygon-pos --blockchains polygon ethereum --start-ts 1700000000 --end-ts 1700000000 --need-extraction --need-normalization --store-alerts
    """

    def __init__(self, argv: Optional[List[str]] = None) -> None:
        self.argv = argv
        self.parser = self._build_parser()

    def _build_parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser()
        Cli._add_common_args(parser)
        return parser

    def _add_common_args(p: argparse.ArgumentParser) -> None:
        p.add_argument("--bridge", required=True, help="Bridge identifier to analyze")
        p.add_argument(
            "--blockchains",
            nargs="+",
            required=True,
            help="Chain names to include, e.g. --blockchains polygon ethereum",
        )
        p.add_argument(
            "--start-ts",
            type=int,
            required=False,
            help=(
                "Optional Unix timestamp (seconds). Required only with --need-extraction. "
                "You can run "
                '"python3 src/helpers/getUnixTimestamp.py [yyyy-mm-dd] --time [hh:mm:ss]" '
                "to get the Unix timestamp on a given date."
            ),
        )
        p.add_argument(
            "--end-ts",
            type=int,
            required=False,
            help=(
                "Optional Unix timestamp (seconds). Required only with --need-extraction. "
                "You can run "
                '"python3 src/helpers/getUnixTimestamp.py [yyyy-mm-dd] --time [hh:mm:ss]" '
                "to get the Unix timestamp on a given date."
            ),
        )
        p.add_argument("--need-extraction", help="Whether to run the extraction phase (default: False)", action="store_true")
        p.add_argument("--need-normalization", help="Whether to run the normalization phase (default: False)", action="store_true")
        p.add_argument("--store-alerts", help="Whether to store generated alerts in the database (default: False)", action="store_true")

    def parse(argv: Optional[List[str]] = None) -> CliArgs:
        parser = Cli._build_parser()
        ns = parser.parse_args(argv)

        if ns.start_ts is not None and ns.start_ts < 0:
            parser.error("--start-ts must be a non-negative Unix timestamp.")

        if ns.end_ts is not None and ns.end_ts < 0:
            parser.error("--end-ts must be a non-negative Unix timestamp.")

        if ns.need_extraction and (ns.start_ts is None or ns.end_ts is None):
            parser.error("--start-ts and --end-ts are required when --need-extraction is used.")

        return CliArgs(
            bridge=ns.bridge,
            blockchains=ns.blockchains,
            start_ts=ns.start_ts,
            end_ts=ns.end_ts,
            need_extraction=ns.need_extraction if hasattr(ns, "need_extraction") else False,
            need_normalization=ns.need_normalization if hasattr(ns, "need_normalization") else False,
            store_alerts=ns.store_alerts if hasattr(ns, "store_alerts") else False
        )

    def run() -> int:
        args = Cli.parse()
        analysis_start_ts = args.start_ts if args.start_ts is not None else 0
        analysis_end_ts = args.end_ts if args.end_ts is not None else int(time.time())
        print(
            "Analysis under construction ... :) "
            f"(bridge={args.bridge}, blockchains={args.blockchains}, start_ts={args.start_ts}, end_ts={args.end_ts}, need_extraction={args.need_extraction}, need_normalization={args.need_normalization}, store_alerts={args.store_alerts})"
        )

        # if extraction is needed, call XChainDataGen
        if args.need_extraction:
            print("Running extraction phase...\n")
            xchain_root = Path(__file__).resolve().parents[1] / "XChainDataGen"
            xchain_entrypoint = xchain_root / "__init__.py"

            if not xchain_entrypoint.exists():
                raise FileNotFoundError(f"XChainDataGen entrypoint not found at {xchain_entrypoint}")

            extract_cmd = [
                sys.executable,
                str(xchain_entrypoint),
                "extract",
                "--bridge",
                args.bridge,
                "--start_ts",
                str(args.start_ts),
                "--end_ts",
                str(args.end_ts),
                "--blockchains",
                *args.blockchains,
            ]
            generate_cmd = [
                sys.executable,
                str(xchain_entrypoint),
                "generate",
                "--bridge",
                args.bridge,
            ]

            subprocess.run(extract_cmd, cwd=xchain_root, check=True)
            subprocess.run(generate_cmd, cwd=xchain_root, check=True)
            print("Extraction phase completed.\n")
        
        # normalize logs and receipts
        if args.need_normalization:
            print("Running normalization phase...\n")
            run_normalization_for_bridge(args.bridge)
            print("Normalization phase completed.\n")

        # run signature detection
        alerts = []
        print("Running signature detection phase...\n")
        alerts = run_for_bridge(
            args.bridge,
            start_ts=analysis_start_ts,
            end_ts=analysis_end_ts,
            persist=args.store_alerts,
        )
        for alert in alerts:
            print(alert + "\n")
        print("Signature detection phase completed.\n")
        print(f"Total alerts detected: {len(alerts)}")
        return 0
