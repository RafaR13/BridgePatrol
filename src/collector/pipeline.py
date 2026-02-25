import os
from typing import List, Tuple, Set
from web3 import Web3

from .rpc import safe_call, chunk_range
from .storage import append_jsonl
from .models import ChainCfg

def collect_logs_and_receipts(
    w3_manager: Web3,
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

    if addresses:
        addresses = [Web3.to_checksum_address(a) for a in addresses]
    else:
        addresses = None
    topic0_list = [t.lower() for t in (topic0_list or [])]

    txs: Set[str] = set()
    logs_count = 0

    with open(logs_path, "a", encoding="utf-8") as logs_f:
        for (a, b) in chunk_range(from_block, to_block, chunk_size):
            flt = {
                "fromBlock": a,
                "toBlock": b,
            }
            if addresses:
                flt["address"] = addresses
            
            if topic0_list:
                flt["topics"] = [topic0_list]
            
            print(flt)

            def _get_logs():
                return w3_manager.call_with_failover("get_logs", flt)

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

                append_jsonl(logs_path, d)
                logs_count += 1

                txh = lg.get("transactionHash")
                if txh is not None:
                    txs.add(txh.hex())

    receipts_count = 0
    with open(receipts_path, "a", encoding="utf-8") as rec_f:
        for txh_hex in txs:
            def _get_receipt():
                return w3_manager.call_with_failover("get_transaction_receipt", txh_hex)

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

            append_jsonl(receipts_path, d)
            receipts_count += 1

    return logs_count, receipts_count