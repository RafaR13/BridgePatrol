from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib import request


TESE_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESE_ROOT / "blockchain-ids-tese"
if not REPO_ROOT.exists():
    REPO_ROOT = TESE_ROOT
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from config.env import load_env_file

load_env_file(REPO_ROOT / ".env")


PBTC_BSC_CONTRACT = "0xed28a457a5a76596ac48d87c0f577020f6ea1c4c"
REDEEM_TOPIC = "0x4599e9bf0d45c505e011d0e11f473510f083a4fdc45e3f795d58bb5379dbad68"
ATTACK_TXS = {
    "0x0eb55e02bce39ec1d2d2e911eca7dcca54e74841b53412c078185e43c5a2a551",
    "0xe79e3ff4ef01a29475e6387a44c550df3e4c0a80177249bfdc9bbd66376b9ff6",
    "0xb845d636202a696949384e3570247cfdbff431992ab2c10bf653e867a18fb2ab",
}
BNB_RPC_ENV_VARS = (
    "BNB_CHAINSTACK_RPC_URL",
    "BNB_ALCHEMY_RPC_URL",
    "BNB_ANKR_RPC_URL",
    "BNB_DRPC_RPC_URL",
    "BNB_ONFINALITY_RPC_URL",
    "BNB_MORALIS_RPC_URL",
)
BNB_PUBLIC_RPC_URLS = (
    "https://bsc.rpc.blxrbdn.com",
    "https://bsc-mainnet.public.blastapi.io",
    "https://bsc-pokt.nodies.app",
    "https://bsc.blockrazor.xyz",
    "https://rpc-bsc.48.club",
    "https://bsc.meowrpc.com",
    "https://api.zan.top/bsc-mainnet",
    "https://bnb.api.onfinality.io/public",
    "https://1rpc.io/bnb",
    "https://binance.nodereal.io",
    "https://bsc-rpc.publicnode.com",
    "https://bsc.drpc.org",
    "https://binance.llamarpc.com",
    "https://rpc.ankr.com/bsc",
    "https://bnb.rpc.subquery.network/public",
    "https://bsc-dataseed1.bnbchain.org",
    "https://bsc-dataseed2.bnbchain.org",
    "https://bsc-dataseed3.bnbchain.org",
    "https://bsc-dataseed4.bnbchain.org",
    "https://bsc-dataseed1.defibit.io",
    "https://bsc-dataseed2.defibit.io",
    "https://bsc-dataseed3.defibit.io",
    "https://bsc-dataseed4.defibit.io",
    "https://bsc-dataseed1.ninicoin.io",
    "https://bsc-dataseed2.ninicoin.io",
    "https://bsc-dataseed3.ninicoin.io",
    "https://bsc-dataseed4.ninicoin.io",
    "https://bsc.publicnode.com",
    "https://56.rpc.thirdweb.com",
)
BNB_CHAIN_ID = "0x38"


def candidate_rpc_urls(include_public: bool) -> list[str]:
    urls = [os.getenv(env_var) for env_var in BNB_RPC_ENV_VARS]
    if include_public:
        urls.extend(BNB_PUBLIC_RPC_URLS)

    candidates: list[str] = []
    seen: set[str] = set()
    for rpc_url in urls:
        if not rpc_url or rpc_url in seen:
            continue
        candidates.append(rpc_url)
        seen.add(rpc_url)
    return candidates


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract legitimate pNetwork pBTC-on-BSC Redeem examples."
    )
    parser.add_argument(
        "--rpc-url",
        default=None,
        help=(
            "BNB Smart Chain RPC URL. If omitted, the script tests configured "
            "BNB RPC env vars first, then public fallback RPCs."
        ),
    )
    parser.add_argument(
        "--no-public-rpc-fallback",
        action="store_true",
        help="Only test RPC URLs from BNB RPC environment variables.",
    )
    parser.add_argument(
        "--rpc-ping-timeout",
        type=float,
        default=5.0,
        help="Seconds to wait for each eth_chainId RPC health check.",
    )
    parser.add_argument("--from-block", type=int, required=True)
    parser.add_argument("--to-block", type=int, required=True)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument(
        "--mode",
        choices=("logs", "receipts"),
        default="logs",
        help="logs uses eth_getLogs; receipts scans blocks and receipts for RPCs that block old eth_getLogs.",
    )
    parser.add_argument("--chunk-size", type=int, default=100)
    parser.add_argument("--sleep", type=float, default=0.05)
    parser.add_argument(
        "--output",
        default=str(DATA_DIR / "pnetwork_legit_redeems.md"),
    )
    return parser.parse_args()


class RpcClient:
    def __init__(
        self,
        rpc_url: str,
        sleep_seconds: float = 0.0,
        timeout_seconds: float = 30.0,
    ):
        self.rpc_url = rpc_url
        self.sleep_seconds = sleep_seconds
        self.timeout_seconds = timeout_seconds
        self._request_id = 0

    def call(self, method: str, params: list):
        self._request_id += 1
        payload = json.dumps(
            {
                "jsonrpc": "2.0",
                "id": self._request_id,
                "method": method,
                "params": params,
            }
        ).encode("utf-8")
        req = request.Request(
            self.rpc_url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "pnetwork-data-extractor/1.0",
            },
            method="POST",
        )
        if self.sleep_seconds:
            time.sleep(self.sleep_seconds)
        with request.urlopen(req, timeout=self.timeout_seconds) as response:
            body = json.loads(response.read().decode("utf-8"))
        if body.get("error"):
            raise RuntimeError(f"{method} failed: {body['error']}")
        return body.get("result")


def select_rpc_url(args: argparse.Namespace) -> str:
    if args.rpc_url:
        candidates = [args.rpc_url]
    else:
        candidates = candidate_rpc_urls(include_public=not args.no_public_rpc_fallback)

    failures: list[str] = []
    for rpc_url in candidates:
        try:
            chain_id = RpcClient(
                rpc_url,
                timeout_seconds=args.rpc_ping_timeout,
            ).call("eth_chainId", [])
        except Exception as exc:
            failures.append(f"{rpc_url} ({exc})")
            continue

        if str(chain_id).lower() == BNB_CHAIN_ID:
            print(f"using BNB RPC: {rpc_url}", file=sys.stderr)
            return rpc_url
        failures.append(f"{rpc_url} (unexpected chain id {chain_id})")

    hint = (
        "--rpc-url, one of "
        + ", ".join(BNB_RPC_ENV_VARS)
        + ", or a working public fallback RPC"
    )
    details = "\n".join(f"  - {failure}" for failure in failures)
    raise RuntimeError(f"Missing working BNB RPC. Set {hint}.\nTried:\n{details}")


def hex_int(value) -> int | None:
    if value is None:
        return None
    return int(str(value), 16)


def topic_address(topic: str) -> str:
    return "0x" + topic[-40:]


def words(data: str) -> list[str]:
    payload = data[2:] if data.startswith("0x") else data
    return [payload[index : index + 64] for index in range(0, len(payload), 64)]


def decode_dynamic_string(event_words: list[str], offset_word_index: int) -> str | None:
    if len(event_words) <= offset_word_index:
        return None
    offset = int(event_words[offset_word_index], 16) // 32
    if len(event_words) <= offset:
        return None
    length = int(event_words[offset], 16)
    data_words = "".join(event_words[offset + 1 :])
    raw = bytes.fromhex(data_words[: length * 2])
    return raw.decode("utf-8", errors="replace")


def decode_redeem_log(log: dict) -> dict:
    event_words = words(log["data"])
    return {
        "redeemer": topic_address(log["topics"][1]) if len(log.get("topics", [])) > 1 else None,
        "amount": int(event_words[0], 16) if event_words else None,
        "recipient": decode_dynamic_string(event_words, 1),
    }


def get_logs(client: RpcClient, from_block: int, to_block: int, chunk_size: int) -> list[dict]:
    logs: list[dict] = []
    start = from_block
    while start <= to_block:
        end = min(start + chunk_size - 1, to_block)
        logs.extend(
            client.call(
                "eth_getLogs",
                [
                    {
                        "fromBlock": hex(start),
                        "toBlock": hex(end),
                        "address": PBTC_BSC_CONTRACT,
                        "topics": [REDEEM_TOPIC],
                    }
                ],
            )
        )
        start = end + 1
    return logs


def scan_receipts(client: RpcClient, from_block: int, to_block: int, limit: int) -> list[dict]:
    logs: list[dict] = []
    for block_number in range(to_block, from_block - 1, -1):
        block = client.call("eth_getBlockByNumber", [hex(block_number), False])
        if not block:
            continue
        for tx_hash in block.get("transactions", []):
            if tx_hash.lower() in ATTACK_TXS:
                continue
            receipt = client.call("eth_getTransactionReceipt", [tx_hash])
            for log in receipt.get("logs", []):
                if log.get("address", "").lower() != PBTC_BSC_CONTRACT:
                    continue
                if not log.get("topics") or log["topics"][0].lower() != REDEEM_TOPIC:
                    continue
                logs.append(log)
                if len(logs) >= limit:
                    return logs
    return logs


def enrich_log(client: RpcClient, log: dict) -> dict:
    tx = client.call("eth_getTransactionByHash", [log["transactionHash"]])
    receipt = client.call("eth_getTransactionReceipt", [log["transactionHash"]])
    decoded = decode_redeem_log(log)
    gas_used = hex_int(receipt.get("gasUsed")) or 0
    gas_price = hex_int(receipt.get("effectiveGasPrice") or tx.get("gasPrice")) or 0
    return {
        "tx": tx,
        "receipt": receipt,
        "log": log,
        "decoded": decoded,
        "fee": gas_used * gas_price,
    }


def markdown_entry(index: int, item: dict) -> str:
    tx = item["tx"]
    receipt = item["receipt"]
    log = item["log"]
    decoded = item["decoded"]
    tx_hash = tx["hash"]
    cctx_id = f"pnetwork:legit_redeem_{index}"
    timestamp = hex_int(log.get("blockTimestamp")) or hex_int(receipt.get("blockTimestamp"))
    status = hex_int(receipt.get("status"))
    block_number = hex_int(log.get("blockNumber"))
    log_index = hex_int(log.get("logIndex"))

    return f"""## Legit Redeem {index}

```python
BlockchainTransaction(
    cctx_id = "{cctx_id}",
    blockchain = "bsc",
    transaction_hash = "{tx_hash}",
    block_number = {block_number},
    timestamp = {timestamp},
    from_address = "{tx.get("from")}",
    to_address = "{tx.get("to")}",
    status = {status},
    value = {hex_int(tx.get("value"))},
    input_data = "{tx.get("input")}",
    calls = None,
    fee = {item["fee"]}
)
```

```python
NormalizedEvent(
    bridge = "pnetwork",
    blockchain = "bsc",
    raw_table = "pnetwork_legit_redeems.md",
    raw_pk = "pnetwork:legit_redeem_{index}",
    transaction_hash = "{tx_hash}",
    cctx_id = "{cctx_id}",
    event_type = "Redeem",
    block_number = {block_number},
    timestamp = {timestamp},
    log_index = {log_index},
    correlation_id = "{tx_hash}:{log_index}",
    src_blockchain = "bsc",
    dst_blockchain = "bitcoin",
    actor_from = "{decoded["redeemer"]}",
    actor_to = "{decoded["recipient"]}",
    token_in = "{PBTC_BSC_CONTRACT}",
    token_out = "BTC",
    amount_in = {decoded["amount"]},
    amount_out = None,
    contract_address = "{log.get("address")}",
    status = "{status}",
    extra_data = "{{\\"event\\":\\"Redeem\\",\\"is_faulty\\":false}}"
)
```
"""


def main() -> int:
    args = parse_args()
    rpc_url = select_rpc_url(args)
    client = RpcClient(rpc_url, sleep_seconds=args.sleep)
    if args.mode == "logs":
        logs = get_logs(client, args.from_block, args.to_block, args.chunk_size)
        logs = [log for log in logs if log["transactionHash"].lower() not in ATTACK_TXS]
        logs = logs[: args.limit]
    else:
        logs = scan_receipts(client, args.from_block, args.to_block, args.limit)

    enriched = [enrich_log(client, log) for log in logs]
    output = Path(args.output).resolve()
    header = (
        "# pNetwork legitimate pBTC-on-BSC Redeem examples\n\n"
        f"Source contract: `{PBTC_BSC_CONTRACT}`\n\n"
        f"Redeem topic: `{REDEEM_TOPIC}`\n\n"
    )
    body = "\n".join(markdown_entry(index, item) for index, item in enumerate(enriched, 1))
    output.write_text(header + body, encoding="utf-8")
    print(f"wrote {len(enriched)} legit Redeem examples to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
