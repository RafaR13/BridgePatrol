import argparse
import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml
from dotenv import load_dotenv
from web3 import Web3


@dataclass
class ChainCfg:
    name: str
    chain_id: int
    rpc_url: str
    confirmations: int


def load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_out_dir(out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)


def rpc_web3(rpc_url: str) -> Web3:
    w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 30}))
    if not w3.is_connected():
        raise RuntimeError(f"Failed to connect to RPC: {rpc_url}")
    return w3


def chunk_range(start: int, end: int, step: int) -> List[Tuple[int, int]]:
    # inclusive start/end
    if end < start:
        return []
    chunks = []
    cur = start
    while cur <= end:
        nxt = min(cur + step - 1, end)
        chunks.append((cur, nxt))
        cur = nxt + 1
    return chunks


def safe_call(fn, retries: int = 5, base_sleep: float = 0.8):
    last_err = None
    for i in range(retries):
        try:
            return fn()
        except Exception as e:
            last_err = e
            time.sleep(base_sleep * (2 ** i))
    raise last_err


def collect_logs_and_receipts(
    w3: Web3,
    chain: ChainCfg,
    collector_name: str,
    addresses: List[str],
    topic0_list: List[str],
    from_block: int,
    to_block: int,
    chunk_size: int,
    out_dir: str,
) -> Tuple[int, int]:
    logs_path = os.path.join(out_dir, f"{collector_name}__{chain.name}__logs.jsonl")
    receipts_path = os.path.join(out_dir, f"{collector_name}__{chain.name}__receipts.jsonl")

    addresses = [Web3.to_checksum_address(a) for a in addresses]
    topic0_list = [t.lower() for t in topic0_list]

    # Keep tx hashes we saw in logs
    txs: Set[str] = set()
    logs_count = 0

    with open(logs_path, "a", encoding="utf-8") as logs_f:
        for (a, b) in chunk_range(from_block, to_block, chunk_size):
            flt = {
                "fromBlock": a,
                "toBlock": b,
                "address": addresses,
                "topics": [topic0_list],
            }

            def _get_logs():
                return w3.eth.get_logs(flt)

            logs = safe_call(_get_logs)

            for lg in logs:
                # Convert AttributeDict -> JSON-safe dict
                d = dict(lg)
                d["chain"] = chain.name
                d["chain_id"] = chain.chain_id
                # bytes -> hex
                for k in ("blockHash", "transactionHash", "topics"):
                    if k in d and d[k] is not None:
                        if k == "topics":
                            d[k] = [t.hex() for t in d[k]]
                        else:
                            d[k] = d[k].hex()
                if "data" in d and isinstance(d["data"], (bytes, bytearray)):
                    d["data"] = Web3.to_hex(d["data"])

                logs_f.write(json.dumps(d, ensure_ascii=False) + "\n")
                logs_count += 1

                txh = lg.get("transactionHash")
                if txh is not None:
                    txs.add(txh.hex())

    receipts_count = 0
    with open(receipts_path, "a", encoding="utf-8") as rec_f:
        for txh_hex in txs:
            def _get_receipt():
                return w3.eth.get_transaction_receipt(txh_hex)

            r = safe_call(_get_receipt)
            d = dict(r)
            d["chain"] = chain.name
            d["chain_id"] = chain.chain_id

            # bytes -> hex
            for k in ("transactionHash", "blockHash"):
                if k in d and d[k] is not None:
                    d[k] = d[k].hex()

            # logs inside receipt (opcional: podes remover para ser mais leve)
            if "logs" in d and d["logs"] is not None:
                out_logs = []
                for lg in d["logs"]:
                    ld = dict(lg)
                    for kk in ("blockHash", "transactionHash", "topics"):
                        if kk in ld and ld[kk] is not None:
                            if kk == "topics":
                                ld[kk] = [t.hex() for t in ld[kk]]
                            else:
                                ld[kk] = ld[kk].hex()
                    if "data" in ld and isinstance(ld["data"], (bytes, bytearray)):
                        ld["data"] = Web3.to_hex(ld["data"])
                    out_logs.append(ld)
                d["logs"] = out_logs

            rec_f.write(json.dumps(d, ensure_ascii=False) + "\n")
            receipts_count += 1

    return logs_count, receipts_count


def main():
    load_dotenv()

    ap = argparse.ArgumentParser()
    ap.add_argument("--chains", default="configs/chains.yml")
    ap.add_argument("--collectors", default="configs/collectors.yml")
    ap.add_argument("--out", default="out")
    ap.add_argument("--from-block", type=int, default=None)
    ap.add_argument("--to-block", type=int, default=None)
    ap.add_argument("--last-n-blocks", type=int, default=2000, help="if from/to not set, collect [head-confirmations-last_n, head-confirmations]")
    ap.add_argument("--chunk-size", type=int, default=500, help="block range per eth_getLogs call")
    args = ap.parse_args()

    ensure_out_dir(args.out)

    chains_doc = load_yaml(args.chains)
    collectors_doc = load_yaml(args.collectors)

    # Build chain cfgs
    chain_cfgs: Dict[str, ChainCfg] = {}
    for name, c in chains_doc["chains"].items():
        rpc_env = c["rpc_url_env"]
        rpc_url = os.environ.get(rpc_env)
        if not rpc_url:
            raise RuntimeError(f"Missing env var {rpc_env} for chain '{name}'")
        chain_cfgs[name] = ChainCfg(
            name=name,
            chain_id=int(c["chain_id"]),
            rpc_url=rpc_url,
            confirmations=int(c.get("confirmations", 0)),
        )

    for collector_name, col in collectors_doc["collectors"].items():
        chain_name = col["chain"]
        chain = chain_cfgs[chain_name]
        w3 = rpc_web3(chain.rpc_url)

        head = w3.eth.block_number
        safe_head = max(0, head - chain.confirmations)

        if args.from_block is not None and args.to_block is not None:
            from_block = args.from_block
            to_block = args.to_block
        else:
            from_block = max(0, safe_head - args.last_n_blocks)
            to_block = safe_head

        print(f"[{collector_name}] chain={chain.name} head={head} safe_head={safe_head} range={from_block}->{to_block}")

        logs_count, receipts_count = collect_logs_and_receipts(
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

        print(f"[{collector_name}] wrote logs={logs_count}, receipts={receipts_count} into '{args.out}/'")

if __name__ == "__main__":
    main()
