import os
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from web3 import Web3

from .rpc import safe_call, chunk_range
from .storage import append_jsonl
from .models import ChainCfg


# -----------------------------
# Helpers (normalização JSON)
# -----------------------------

def _hexify(value: Any) -> Any:
    """Convert bytes/HexBytes/AttributeDict-like fields into JSON-safe primitives."""
    if value is None:
        return None
    if isinstance(value, (bytes, bytearray)):
        return Web3.to_hex(value)
    # Web3's HexBytes has .hex()
    if hasattr(value, "hex") and callable(getattr(value, "hex")):
        try:
            return value.hex()
        except Exception:
            pass
    return value


def _normalize_log(lg: Dict[str, Any], chain: ChainCfg) -> Dict[str, Any]:
    d = dict(lg)
    d["chain"] = chain.name
    d["chain_id"] = chain.chain_id

    # common log fields
    for k in ("blockHash", "transactionHash"):
        if k in d:
            d[k] = _hexify(d[k])

    # topics is a list of bytes/HexBytes
    if "topics" in d and d["topics"] is not None:
        d["topics"] = [_hexify(t) for t in d["topics"]]

    if "data" in d:
        d["data"] = _hexify(d["data"])

    # address should already be a hex string, but normalize checksum if possible
    if "address" in d and d["address"]:
        try:
            d["address"] = Web3.to_checksum_address(d["address"])
        except Exception:
            # keep original
            pass

    return d


def _normalize_receipt(r: Dict[str, Any], chain: ChainCfg) -> Dict[str, Any]:
    d = dict(r)
    d["chain"] = chain.name
    d["chain_id"] = chain.chain_id

    for k in ("transactionHash", "blockHash"):
        if k in d:
            d[k] = _hexify(d[k])

    # logs inside receipt (podes desligar se quiseres ficheiro mais leve)
    if "logs" in d and d["logs"] is not None:
        out_logs = []
        for lg in d["logs"]:
            ld = dict(lg)
            for kk in ("blockHash", "transactionHash"):
                if kk in ld:
                    ld[kk] = _hexify(ld[kk])
            if "topics" in ld and ld["topics"] is not None:
                ld["topics"] = [_hexify(t) for t in ld["topics"]]
            if "data" in ld:
                ld["data"] = _hexify(ld["data"])
            if "address" in ld and ld["address"]:
                try:
                    ld["address"] = Web3.to_checksum_address(ld["address"])
                except Exception:
                    pass
            out_logs.append(ld)
        d["logs"] = out_logs

    return d


def _normalize_block(b: Dict[str, Any], chain: ChainCfg) -> Dict[str, Any]:
    d = dict(b)
    d["chain"] = chain.name
    d["chain_id"] = chain.chain_id

    # hexify common hashes
    for k in ("hash", "parentHash", "sha3Uncles", "stateRoot", "transactionsRoot", "receiptsRoot"):
        if k in d:
            d[k] = _hexify(d[k])

    # 'miner'/'author'/'beneficiary' addresses differ by client; normalize if present
    for addr_k in ("miner", "author"):
        if addr_k in d and d[addr_k]:
            try:
                d[addr_k] = Web3.to_checksum_address(d[addr_k])
            except Exception:
                pass

    # Keep transactions list light: we call get_block(..., full_transactions=False)
    # so transactions is list of tx hashes -> hexify
    if "transactions" in d and isinstance(d["transactions"], list):
        d["transactions"] = [_hexify(x) for x in d["transactions"]]

    return d


def _keccak_hex(hexstr: str) -> str:
    """Keccak-256 of a hexstring (0x...). Returns 0x..."""
    if not hexstr:
        return "0x"
    try:
        return Web3.keccak(hexstr=hexstr).hex()
    except Exception:
        # fallback: if node returns '0x' for EOAs, keccak('0x') is still valid,
        # but if something odd happens, don't crash collection
        return "0x"


# -----------------------------
# Coleta estruturada
# -----------------------------

@dataclass(frozen=True)
class CallSpec:
    """Generic eth_call spec."""
    to: str
    data: str
    block: str = "latest"  # or hex block number like "0x1234" or int via caller


def collect_logs(
    w3_manager: Web3,
    chain: ChainCfg,
    collector_name: str,
    addresses: Optional[List[str]],
    topic0_list: Optional[List[str]],
    from_block: int,
    to_block: int,
    chunk_size: int,
    out_dir: str,
) -> Tuple[int, Set[str], Set[int], Set[str]]:
    """
    Returns:
      logs_count,
      tx_hashes (hex),
      block_numbers,
      emitter_addresses
    """
    logs_path = os.path.join(out_dir, f"{collector_name}__{chain.name}__logs.jsonl")

    if addresses:
        addresses = [Web3.to_checksum_address(a) for a in addresses]
    else:
        addresses = None

    topic0_list = [(t if t.startswith("0x") else "0x" + t).lower() for t in (topic0_list or [])]

    txs: Set[str] = set()
    block_numbers: Set[int] = set()
    emitters: Set[str] = set()
    logs_count = 0

    for (a, b) in chunk_range(from_block, to_block, chunk_size):
        flt: Dict[str, Any] = {"fromBlock": a, "toBlock": b}
        if addresses:
            flt["address"] = addresses
        if topic0_list:
            # OR over topic0 values
            flt["topics"] = [topic0_list]

        def _get_logs():
            return w3_manager.call_with_failover("get_logs", flt)

        logs = safe_call(_get_logs) or []

        for lg in logs:
            d = _normalize_log(lg, chain)
            append_jsonl(logs_path, d)
            logs_count += 1

            # tx hash set
            txh = lg.get("transactionHash")
            if txh is not None:
                txs.add(_hexify(txh))

            # block numbers (int)
            bn = lg.get("blockNumber")
            if isinstance(bn, int):
                block_numbers.add(bn)

            # emitter address
            addr = lg.get("address")
            if addr:
                try:
                    emitters.add(Web3.to_checksum_address(addr))
                except Exception:
                    emitters.add(addr)

    return logs_count, txs, block_numbers, emitters


def collect_receipts(
    w3_manager: Web3,
    chain: ChainCfg,
    collector_name: str,
    tx_hashes: Iterable[str],
    out_dir: str,
) -> Tuple[int, Set[int]]:
    """
    Returns:
      receipts_count,
      block_numbers_seen_in_receipts
    """
    receipts_path = os.path.join(out_dir, f"{collector_name}__{chain.name}__receipts.jsonl")

    receipts_count = 0
    block_numbers: Set[int] = set()

    for txh_hex in tx_hashes:
        def _get_receipt():
            return w3_manager.call_with_failover("get_transaction_receipt", txh_hex)

        r = safe_call(_get_receipt)
        if not r:
            continue

        d = _normalize_receipt(r, chain)
        append_jsonl(receipts_path, d)
        receipts_count += 1

        bn = r.get("blockNumber")
        if isinstance(bn, int):
            block_numbers.add(bn)

    return receipts_count, block_numbers


def collect_blocks(
    w3_manager: Web3,
    chain: ChainCfg,
    collector_name: str,
    block_numbers: Iterable[int],
    out_dir: str,
) -> int:
    """
    Collect eth_getBlockByNumber for every block in block_numbers (dedup + sorted).
    Uses full_transactions=False for lighter payload.
    """
    blocks_path = os.path.join(out_dir, f"{collector_name}__{chain.name}__blocks.jsonl")

    count = 0
    for bn in sorted(set(int(x) for x in block_numbers)):
        def _get_block():
            # Web3: get_block(block_identifier, full_transactions)
            return w3_manager.call_with_failover("get_block", bn, False)

        blk = safe_call(_get_block)
        if not blk:
            continue

        d = _normalize_block(blk, chain)
        append_jsonl(blocks_path, d)
        count += 1

    return count


def collect_codes(
    w3_manager: Web3,
    chain: ChainCfg,
    collector_name: str,
    addresses: Iterable[str],
    out_dir: str,
    block: str = "latest",
    include_bytecode: bool = False,
) -> int:
    """
    Collect eth_getCode for each address (useful for UNAUTHORIZED_EMITTER / fingerprinting).
    Stores code_hash + length always; optionally stores bytecode.
    """
    codes_path = os.path.join(out_dir, f"{collector_name}__{chain.name}__codes.jsonl")

    count = 0
    for addr in sorted(set(addresses)):
        try:
            caddr = Web3.to_checksum_address(addr)
        except Exception:
            caddr = addr

        def _get_code():
            return w3_manager.call_with_failover("get_code", caddr, block)

        code_hex = safe_call(_get_code)
        if code_hex is None:
            continue

        # Some nodes return HexBytes; normalize
        if isinstance(code_hex, (bytes, bytearray)) or hasattr(code_hex, "hex"):
            code_hex = _hexify(code_hex)
        if not isinstance(code_hex, str):
            # unknown type -> coerce
            code_hex = str(code_hex)

        out: Dict[str, Any] = {
            "chain": chain.name,
            "chain_id": chain.chain_id,
            "address": caddr,
            "block": block,
            "code_len": (len(code_hex) - 2) // 2 if code_hex.startswith("0x") else len(code_hex),
            "code_hash": _keccak_hex(code_hex if code_hex.startswith("0x") else ("0x" + code_hex)),
        }
        if include_bytecode:
            out["code"] = code_hex

        append_jsonl(codes_path, out)
        count += 1

    return count


def collect_calls(
    w3_manager: Web3,
    chain: ChainCfg,
    collector_name: str,
    calls: Iterable[CallSpec],
    out_dir: str,
) -> int:
    """
    Generic eth_call collector. You pass CallSpec(to, data, block).
    """
    calls_path = os.path.join(out_dir, f"{collector_name}__{chain.name}__calls.jsonl")

    count = 0
    for cs in calls:
        try:
            to_addr = Web3.to_checksum_address(cs.to)
        except Exception:
            to_addr = cs.to

        data = cs.data if cs.data.startswith("0x") else ("0x" + cs.data)
        block_id: Any = cs.block

        payload = {"to": to_addr, "data": data}

        def _call():
            # Web3: eth_call(call_tx, block_identifier)
            return w3_manager.call_with_failover("call", payload, block_id)

        res = safe_call(_call)

        out = {
            "chain": chain.name,
            "chain_id": chain.chain_id,
            "to": to_addr,
            "data": data,
            "block": block_id,
            "result": _hexify(res),
        }
        append_jsonl(calls_path, out)
        count += 1

    return count



def collect_data(
    w3_manager: Web3,
    chain: ChainCfg,
    collector_name: str,
    addresses: Optional[List[str]],
    topic0_list: Optional[List[str]],
    from_block: int,
    to_block: int,
    chunk_size: int,
    out_dir: str,
    *,
    collect_block_headers: bool = True,
    collect_emitter_code: bool = True,
    code_block: str = "latest",
    include_bytecode: bool = False,
    extra_calls: Optional[List[CallSpec]] = None,
) -> Dict[str, int]:
    """
    One-shot pipeline:
      1) logs
      2) receipts (for txs seen in logs)
      3) blocks (for blocks referenced by logs/receipts)
      4) codes (for emitters seen in logs)
      5) optional eth_call specs

    Returns counters for each artifact.
    """
    logs_count, txs, bn_logs, emitters = collect_logs(
        w3_manager=w3_manager,
        chain=chain,
        collector_name=collector_name,
        addresses=addresses,
        topic0_list=topic0_list,
        from_block=from_block,
        to_block=to_block,
        chunk_size=chunk_size,
        out_dir=out_dir,
    )

    receipts_count, bn_receipts = collect_receipts(
        w3_manager=w3_manager,
        chain=chain,
        collector_name=collector_name,
        tx_hashes=txs,
        out_dir=out_dir,
    )

    blocks_count = 0
    if collect_block_headers:
        all_blocks = set(bn_logs) | set(bn_receipts)
        blocks_count = collect_blocks(
            w3_manager=w3_manager,
            chain=chain,
            collector_name=collector_name,
            block_numbers=all_blocks,
            out_dir=out_dir,
        )

    codes_count = 0
    if collect_emitter_code:
        codes_count = collect_codes(
            w3_manager=w3_manager,
            chain=chain,
            collector_name=collector_name,
            addresses=emitters,
            out_dir=out_dir,
            block=code_block,
            include_bytecode=include_bytecode,
        )

    calls_count = 0
    if extra_calls:
        calls_count = collect_calls(
            w3_manager=w3_manager,
            chain=chain,
            collector_name=collector_name,
            calls=extra_calls,
            out_dir=out_dir,
        )

    return {
        "logs": logs_count,
        "receipts": receipts_count,
        "blocks": blocks_count,
        "codes": codes_count,
        "calls": calls_count,
    }