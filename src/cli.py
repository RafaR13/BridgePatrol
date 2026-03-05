# cli.py
import argparse
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class CliArgs:
    mode: str
    bridge: str
    chains: List[str]

    # forensic only
    from_block: Optional[int] = None
    to_block: Optional[int] = None
    from_ts: Optional[int] = None
    to_ts: Optional[int] = None
    last_n_blocks: Optional[int] = None


class Cli:
    """
    Usage examples:
      collector realtime --bridge polygon-pos --chains polygon ethereum

      collector forensic --bridge polygon-pos --chains polygon ethereum --last-n-blocks 100
      collector forensic --bridge polygon-pos --chains polygon ethereum --from-block 100 --to-block 200
      collector forensic --bridge polygon-pos --chains polygon ethereum --from-ts 1700000000 --to-ts 1700003600
    """

    def __init__(self, argv: Optional[List[str]] = None) -> None:
        self.argv = argv
        self.parser = self._build_parser()

    def _build_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser()

        sub = parser.add_subparsers(dest="mode", required=True)

        # -------- realtime --------
        realtime = sub.add_parser("realtime", help="Run realtime analysis")
        self._add_common_args(realtime)


        # -------- forensic --------
        forensic = sub.add_parser("forensic", help="Run forensic (bounded) analysis")
        self._add_common_args(forensic)

        # Mutually exclusive time-range options (exactly one required)
        window = forensic.add_mutually_exclusive_group(required=True)

        # Option 1: block range (requires both)
        block = window.add_argument_group("block_range")
        block.add_argument("--from-block", type=int, default=None)
        block.add_argument("--to-block", type=int, default=None)

        # Option 2: timestamp range (requires both)
        ts = window.add_argument_group("timestamp_range")
        ts.add_argument("--from-ts", type=int, default=None, help="Unix timestamp (seconds) You can run ... to get the Unix timestamp on a given date")
        ts.add_argument("--to-ts", type=int, default=None, help="Unix timestamp (seconds). You can run ... to get the Unix timestamp on a given date")

        # Option 3: last N blocks
        window.add_argument("--last-n-blocks", type=int, default=None)

        return parser

    def _add_common_args(self, p: argparse.ArgumentParser) -> None:
        p.add_argument("--bridge", required=True, help="Bridge identifier to analyze")
        p.add_argument(
            "--chains",
            nargs="+",
            required=True,
            help='Chain names to include, e.g. --chains polygon ethereum',
        )

    def parse(self) -> CliArgs:
        ns = self.parser.parse_args(self.argv)

        # forensic validation for paired args
        if ns.mode == "forensic":
            has_block = (ns.from_block is not None) or (ns.to_block is not None)
            has_ts = (ns.from_ts is not None) or (ns.to_ts is not None)
            has_last = (ns.last_n_blocks is not None)

            # check that exactly one of the three options is selected
            selected = sum([1 if (ns.from_block is not None or ns.to_block is not None) else 0,
                            1 if (ns.from_ts is not None or ns.to_ts is not None) else 0,
                            1 if (ns.last_n_blocks is not None) else 0])
            if selected != 1:
                self.parser.error(
                    "Forensic requires exactly one window option: "
                    "(--from-block & --to-block) OR (--from-ts & --to-ts) OR (--last-n-blocks)."
                )

            if has_block:
                if ns.from_block is None or ns.to_block is None:
                    self.parser.error("--from-block and --to-block must be used together.")
                if ns.from_block < 0 or ns.to_block < 0:
                    self.parser.error("Block numbers must be non-negative.")
                if ns.from_block > ns.to_block:
                    self.parser.error("--from-block must be <= --to-block.")

            if has_ts:
                if ns.from_ts is None or ns.to_ts is None:
                    self.parser.error("--from-ts and --to-ts must be used together.")
                if ns.from_ts < 0 or ns.to_ts < 0:
                    self.parser.error("Timestamps must be non-negative Unix seconds.")
                if ns.from_ts > ns.to_ts:
                    self.parser.error("--from-ts must be <= --to-ts.")

            if has_last:
                if ns.last_n_blocks <= 0:
                    self.parser.error("--last-n-blocks must be > 0.")

        return CliArgs(
            mode=ns.mode,
            bridge=ns.bridge,
            chains=ns.chains,
            from_block=getattr(ns, "from_block", None),
            to_block=getattr(ns, "to_block", None),
            from_ts=getattr(ns, "from_ts", None),
            to_ts=getattr(ns, "to_ts", None),
            last_n_blocks=getattr(ns, "last_n_blocks", None),
        )

    def run(self) -> int:
        args = self.parse()

        if args.mode == "realtime":
            print(f"Realtime analysis under construction ... :) (bridge={args.bridge}, chains={args.chains})")
            # TODO: initiate real time analysis here
            return 0

        if args.mode == "forensic":
            print(f"Forensic analysis under construction ... :) (bridge={args.bridge}, chains={args.chains})")
            # TODO: initiate forensic analysis here
            return 0

        # argparse should prevent reaching here
        raise RuntimeError(f"Unknown mode: {args.mode}")