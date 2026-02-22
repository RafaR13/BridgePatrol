import time
from typing import List, Tuple
from web3 import Web3

def rpc_web3(rpc_url: str) -> Web3:
    w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 30}))
    if not w3.is_connected():
        raise RuntimeError(f"Failed to connect to RPC: {rpc_url}")
    return w3

def safe_call(fn, retries: int = 5, base_sleep: float = 0.8):
    last_err = None
    for i in range(retries):
        try:
            return fn()
        except Exception as e:
            last_err = e
            time.sleep(base_sleep * (2 ** i))
    raise last_err

def chunk_range(start: int, end: int, step: int) -> List[Tuple[int, int]]:
    if end < start:
        return []

    chunks = []
    cur = start
    while cur <= end:
        nxt = min(cur + step - 1, end)
        chunks.append((cur, nxt))
        cur = nxt + 1

    return chunks