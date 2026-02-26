# main.py
import argparse

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="collector")

    sub = parser.add_subparsers(dest="mode", required=True)

    # -------- realtime --------
    rt = sub.add_parser("realtime", help="Run realtime collection")
    rt.add_argument("--chains", default="../configs/chains.yml")
    rt.add_argument("--collectors", default="../configs/collectors.yml")

    # -------- forensic --------
    fo = sub.add_parser("forensic", help="Run forensic (bounded) collection")
    fo.add_argument("--chains", default="../configs/chains.yml")
    fo.add_argument("--collectors", default="../configs/collectors.yml")
    fo.add_argument("--from-block", type=int, default=None)
    fo.add_argument("--to-block", type=int, default=None)
    fo.add_argument("--last-n-blocks", type=int, default=100)
    fo.add_argument("--chunk-size", type=int, default=500)

    return parser

def main():

    parser = build_parser()
    args = parser.parse_args()

    if args.mode == "realtime":
        print("Real time analysis under construction ... :)")
        # TODO: initiate real time analysis here
        return

    if args.mode == "forensic":
        print("Forensic analysis under construction ... :)")
        # TODO: initiate forensic analysis here
        return

if __name__ == "__main__":
    main()