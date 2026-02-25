import time
from typing import List, Tuple
from .rpcManager import RPCManager

def rpc_web3(chain_name: str, rpc_envs: List[str]) -> RPCManager:
    """Initializes and returns an RPCManager instance for the specified chain"""
    return RPCManager(chain_name, rpc_envs)

def safe_call(fn, retries: int = 5, base_sleep: float = 0.8):
    """Executes a function with retries and exponential backoff in case of exceptions"""
    last_err = None
    for i in range(retries):
        try:
            return fn()
        except Exception as e:
            last_err = e
            time.sleep(base_sleep * (2 ** i))
    raise last_err

def chunk_range(start: int, end: int, step: int) -> List[Tuple[int, int]]:
    """Splits a range of integers into chunks of a specified size"""
    if end < start:
        return []

    chunks = []
    cur = start
    while cur <= end:
        nxt = min(cur + step - 1, end)
        chunks.append((cur, nxt))
        cur = nxt + 1

    return chunks