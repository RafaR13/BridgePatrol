# main.py
import argparse
import os
from dotenv import load_dotenv

from .config import load_yaml, build_chain_cfgs
from .rpc import rpc_web3
from .pipeline import collect_logs_and_receipts

def main():
    load_dotenv()

    ap = argparse.ArgumentParser()
    ap.add_argument("--chains", default="../configs/chains.yml")
    ap.add_argument("--collectors", default="../configs/collectors.yml")
    ap.add_argument("--out", default="out")
    ap.add_argument("--from-block", type=int, default=None)
    ap.add_argument("--to-block", type=int, default=None)
    ap.add_argument("--last-n-blocks", type=int, default=2000)
    ap.add_argument("--chunk-size", type=int, default=500)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)

    chains_doc = load_yaml(args.chains)
    collectors_doc = load_yaml(args.collectors)

    chain_cfgs = build_chain_cfgs(chains_doc)

    for collector_name, col in collectors_doc["collectors"].items():
        chain = chain_cfgs[col["chain"]]
        w3 = rpc_web3(chain.rpc_url)

        head = w3.eth.block_number
        safe_head = max(0, head - chain.confirmations)

        if args.from_block is not None and args.to_block is not None:
            from_block = args.from_block
            to_block = args.to_block
        else:
            from_block = max(0, safe_head - args.last_n_blocks)
            to_block = safe_head

        collect_logs_and_receipts(
            w3=w3,
            chain=chain,
            collector_name=collector_name,
            addresses=col["addresses"],
            topic0_list=col["topic0"],
            from_block=from_block,
            to_block=to_block,
            chunk_size=args.chunk_size,
            out_dir=args.out,
        )

if __name__ == "__main__":
    main()