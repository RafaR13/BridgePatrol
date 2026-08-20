from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

TESE_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESE_ROOT / "blockchain-ids-tese"
if not REPO_ROOT.exists():
    REPO_ROOT = TESE_ROOT
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from config.env import load_env_file

load_env_file(REPO_ROOT / ".env")

from sqlalchemy import inspect, text

from db.database import Base, engine, get_session
from db.repository.bridge_tables.pnetwork import (
    PNetworkBitcoinBlockchainTransactions,
    PNetworkBscBlockchainTransactions,
    PNetworkCrossChainTransactions,
)
from db.repository.normalized_event.normalized_event_model import (
    NORMALIZED_EVENT_FIELDS,
    PNetworkNormalizedEvent,
)


DEFAULT_DATA_FILE = DATA_DIR / "pnetwork_txs_and_logs.md"
LEGACY_TABLE_RENAMES = {
    "bsc_blockchain_transactions": "pnetwork_bsc_blockchain_transactions",
    "bitcoin_blockchain_transactions": "pnetwork_bitcoin_blockchain_transactions",
    "bsc_normalized_events": "pnetwork_normalized_event",
}

TX_FIELDS = (
    "blockchain",
    "transaction_hash",
    "block_number",
    "timestamp",
    "from_address",
    "to_address",
    "status",
    "value",
    "input_data",
    "calls",
    "fee",
)

TX_MODEL_BY_BLOCKCHAIN = {
    "bsc": PNetworkBscBlockchainTransactions,
    "bitcoin": PNetworkBitcoinBlockchainTransactions,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import the curated pNetwork pBTC-on-BSC attack dataset."
    )
    parser.add_argument(
        "--data-file",
        default=str(DEFAULT_DATA_FILE),
        help="Markdown file containing BlockchainTransaction and NormalizedEvent blocks.",
    )
    return parser.parse_args()


def parse_value(raw_value: str):
    raw_value = raw_value.rstrip(",").strip()
    if raw_value == "None":
        return None
    try:
        return ast.literal_eval(raw_value)
    except (SyntaxError, ValueError):
        return raw_value.strip("\"'")


def parse_blocks(data_file: Path) -> tuple[list[dict], list[dict]]:
    text = data_file.read_text(encoding="utf-8")
    transactions: list[dict] = []
    events: list[dict] = []

    for block in re.findall(r"```python\n(.*?)```", text, flags=re.DOTALL):
        lines = [line.strip() for line in block.strip().splitlines() if line.strip()]
        if not lines:
            continue
        object_type = lines[0].split("(", 1)[0]
        payload = {}
        for line in lines[1:]:
            if line == ")" or "=" not in line:
                continue
            key, value = line.split("=", 1)
            payload[key.strip()] = parse_value(value)

        if object_type == "BlockchainTransaction":
            transactions.append(payload)
        elif object_type == "NormalizedEvent":
            events.append(payload)

    return transactions, events


def upsert_model(session, model, key_filter: dict, payload: dict):
    row = session.query(model).filter_by(**key_filter).one_or_none()
    if row is None:
        row = model(**payload)
        session.add(row)
        return "inserted"

    for field, value in payload.items():
        setattr(row, field, value)
    return "updated"


def migrate_legacy_table_names() -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    with engine.begin() as connection:
        for legacy_name, new_name in LEGACY_TABLE_RENAMES.items():
            if legacy_name not in table_names or new_name in table_names:
                continue
            connection.execute(
                text(f'ALTER TABLE "{legacy_name}" RENAME TO "{new_name}"')
            )
            table_names.remove(legacy_name)
            table_names.add(new_name)


def model_for_transaction(tx: dict):
    blockchain = str(tx.get("blockchain", "")).lower()
    try:
        return TX_MODEL_BY_BLOCKCHAIN[blockchain]
    except KeyError as exc:
        supported = ", ".join(sorted(TX_MODEL_BY_BLOCKCHAIN))
        raise ValueError(
            f"Unsupported blockchain {blockchain!r} for pNetwork tx import. "
            f"Supported values: {supported}"
        ) from exc


def event_for_cctx(events: list[dict], cctx_id: str) -> dict | None:
    cctx_events = [event for event in events if event.get("cctx_id") == cctx_id]
    for event in cctx_events:
        if event.get("amount_in") not in (None, 0):
            return event
    return cctx_events[0] if cctx_events else None


def tx_for_blockchain(transactions: list[dict], blockchain: str) -> dict | None:
    for tx in transactions:
        if str(tx.get("blockchain", "")).lower() == blockchain:
            return tx
    return None


def repeated_event_count(event: dict | None) -> int:
    if not event or not event.get("extra_data"):
        return 1
    try:
        extra_data = json.loads(event["extra_data"])
    except (TypeError, json.JSONDecodeError):
        return 1
    return int(extra_data.get("repeated_faulty_log_count") or 1)


def cctx_amount_in(event: dict | None):
    if not event or event.get("amount_in") is None:
        return None
    return event["amount_in"] * repeated_event_count(event)


def cctx_payload(
    cctx_id: str,
    source_tx: dict | None,
    destination_tx: dict | None,
    event: dict | None,
) -> dict:
    source_tx = source_tx or {}
    destination_tx = destination_tx or {}
    return {
        "cctx_id": cctx_id,
        "src_blockchain": source_tx.get("blockchain"),
        "src_transaction_hash": source_tx.get("transaction_hash"),
        "src_from_address": source_tx.get("from_address"),
        "src_to_address": source_tx.get("to_address"),
        "src_fee": source_tx.get("fee"),
        "src_fee_usd": None,
        "src_value": source_tx.get("value"),
        "src_timestamp": source_tx.get("timestamp"),
        "dst_blockchain": destination_tx.get("blockchain") or (event.get("dst_blockchain") if event else "bitcoin"),
        "dst_transaction_hash": destination_tx.get("transaction_hash"),
        "dst_from_address": destination_tx.get("from_address"),
        "dst_to_address": destination_tx.get("to_address") or (event.get("actor_to") if event else None),
        "dst_fee": destination_tx.get("fee"),
        "dst_fee_usd": None,
        "dst_value": destination_tx.get("value"),
        "dst_timestamp": destination_tx.get("timestamp"),
        "correlation_id": event.get("correlation_id") if event else source_tx.get("transaction_hash"),
        "depositor": event.get("actor_from") if event else source_tx.get("from_address"),
        "recipient": event.get("actor_to") if event else None,
        "src_contract_address": event.get("contract_address") if event else None,
        "dst_contract_address": None,
        "token_in": event.get("token_in") if event else None,
        "token_out": event.get("token_out") if event else "BTC",
        "amount_in": cctx_amount_in(event),
        "amount_out": event.get("amount_out") if event and event.get("amount_out") is not None else destination_tx.get("value"),
        "amount_usd": None,
    }


def main() -> int:
    args = parse_args()
    data_file = Path(args.data_file).resolve()
    transactions, events = parse_blocks(data_file)

    if not transactions:
        raise RuntimeError(f"No BlockchainTransaction blocks found in {data_file}")
    if not events:
        raise RuntimeError(f"No NormalizedEvent blocks found in {data_file}")

    migrate_legacy_table_names()
    Base.metadata.create_all(bind=engine)
    session = get_session()
    try:
        tx_counts = {"inserted": 0, "updated": 0}
        event_counts = {"inserted": 0, "updated": 0}
        cctx_counts = {"inserted": 0, "updated": 0}

        transactions_by_cctx: dict[str, list[dict]] = {}

        for tx in transactions:
            tx_payload = {field: tx.get(field) for field in TX_FIELDS}
            action = upsert_model(
                session,
                model_for_transaction(tx),
                {"transaction_hash": tx_payload["transaction_hash"]},
                tx_payload,
            )
            tx_counts[action] += 1
            transactions_by_cctx.setdefault(tx["cctx_id"], []).append(tx)

        for cctx_id, cctx_transactions in transactions_by_cctx.items():
            source_tx = tx_for_blockchain(cctx_transactions, "bsc")
            destination_tx = tx_for_blockchain(cctx_transactions, "bitcoin")
            cctx = cctx_payload(
                cctx_id,
                source_tx,
                destination_tx,
                event_for_cctx(events, cctx_id),
            )
            action = upsert_model(
                session,
                PNetworkCrossChainTransactions,
                {"cctx_id": cctx["cctx_id"]},
                cctx,
            )
            cctx_counts[action] += 1

        for event in events:
            event_payload = {
                field: event.get(field)
                for field in NORMALIZED_EVENT_FIELDS
            }
            action = upsert_model(
                session,
                PNetworkNormalizedEvent,
                {
                    "raw_table": event_payload["raw_table"],
                    "raw_pk": event_payload["raw_pk"],
                },
                event_payload,
            )
            event_counts[action] += 1

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    print(
        "pNetwork import complete: "
        f"transactions={tx_counts}, cctx={cctx_counts}, events={event_counts}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
