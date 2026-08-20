#!/usr/bin/env python3
"""Import the curated ChainSwap attacker transactions into PostgreSQL.

Defaults to the local xchain_test database used in XChainDataGen:
postgresql://admin:pwd@localhost:5432/xchain_test
"""

from __future__ import annotations

import argparse
import ast
import os
import re
from decimal import Decimal
from pathlib import Path
from typing import Any

DEFAULT_DATABASE_URL = "postgresql://admin:pwd@localhost:5432/xchain_test"
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_FILE = DATA_DIR / "chainswap_blockchain_transactions.md"

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

CCTX_FIELDS = (
    "cctx_id",
    "src_blockchain",
    "src_transaction_hash",
    "src_from_address",
    "src_to_address",
    "src_fee",
    "src_fee_usd",
    "src_value",
    "src_timestamp",
    "dst_blockchain",
    "dst_transaction_hash",
    "dst_from_address",
    "dst_to_address",
    "dst_fee",
    "dst_fee_usd",
    "dst_value",
    "dst_timestamp",
    "correlation_id",
    "depositor",
    "recipient",
    "src_contract_address",
    "dst_contract_address",
    "token_in",
    "token_out",
    "amount_in",
    "amount_out",
    "amount_usd",
)

INTEGER_FIELDS = {"block_number", "timestamp", "status"}
NUMERIC_FIELDS = {"value", "fee"}
EMPTY_VALUES = {"", "NULL", "None"}

CREATE_TX_TABLE = """
CREATE TABLE IF NOT EXISTS chainswap_blockchain_transactions (
    blockchain VARCHAR(16) NOT NULL,
    transaction_hash VARCHAR(128) PRIMARY KEY,
    block_number BIGINT NOT NULL,
    timestamp BIGINT NOT NULL,
    from_address VARCHAR(128),
    to_address VARCHAR(128),
    status INTEGER NOT NULL,
    value NUMERIC(50, 0),
    input_data VARCHAR(35000),
    calls JSONB,
    fee NUMERIC(50, 0) NOT NULL
)
"""

CREATE_CCTX_TABLE = """
CREATE TABLE IF NOT EXISTS chainswap_cross_chain_transactions (
    id BIGSERIAL PRIMARY KEY,
    cctx_id VARCHAR(128) NOT NULL UNIQUE,
    src_blockchain VARCHAR(16),
    src_transaction_hash VARCHAR(128),
    src_from_address VARCHAR(128),
    src_to_address VARCHAR(128),
    src_fee NUMERIC(50, 0),
    src_fee_usd DOUBLE PRECISION,
    src_value NUMERIC(50, 0),
    src_timestamp BIGINT,
    dst_blockchain VARCHAR(16),
    dst_transaction_hash VARCHAR(128),
    dst_from_address VARCHAR(128),
    dst_to_address VARCHAR(128),
    dst_fee NUMERIC(50, 0),
    dst_fee_usd DOUBLE PRECISION,
    dst_value NUMERIC(50, 0),
    dst_timestamp BIGINT,
    correlation_id VARCHAR(128),
    depositor VARCHAR(128),
    recipient VARCHAR(128),
    src_contract_address VARCHAR(128),
    dst_contract_address VARCHAR(128),
    token_in VARCHAR(128),
    token_out VARCHAR(128),
    amount_in NUMERIC(50, 0),
    amount_out NUMERIC(50, 0),
    amount_usd DOUBLE PRECISION
)
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import ChainSwap attack BlockchainTransaction rows into PostgreSQL."
    )
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL),
        help=f"PostgreSQL URL. Defaults to {DEFAULT_DATABASE_URL}",
    )
    parser.add_argument(
        "--data-file",
        default=str(DEFAULT_DATA_FILE),
        help=f"Markdown file to import. Defaults to {DEFAULT_DATA_FILE}",
    )
    return parser.parse_args()


def extract_code_blocks(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return re.findall(r"```(?:\w+)?\n(.*?)```", text, flags=re.DOTALL)


def parse_block(block: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def clean_scalar(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if value.endswith(","):
        value = value[:-1].rstrip()
    if value in EMPTY_VALUES:
        return None
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return str(ast.literal_eval(value))
    return value


def clean_int(value: str | None) -> int | None:
    value = clean_scalar(value)
    if value is None:
        return None
    return int(value)


def clean_decimal(value: str | None) -> Decimal | None:
    value = clean_scalar(value)
    if value is None:
        return None
    return Decimal(value)


def clean_calls(value: str | None) -> Any:
    value = clean_scalar(value)
    if value is None:
        return None
    return value


def parse_transaction_block(path: Path, block: str) -> dict[str, Any]:
    parsed = parse_block(block)
    row: dict[str, Any] = {}

    for field in TX_FIELDS:
        if field in INTEGER_FIELDS:
            row[field] = clean_int(parsed.get(field))
        elif field in NUMERIC_FIELDS:
            row[field] = clean_decimal(parsed.get(field))
        elif field == "calls":
            row[field] = clean_calls(parsed.get(field))
        else:
            row[field] = clean_scalar(parsed.get(field))

    required = (
        "blockchain",
        "transaction_hash",
        "block_number",
        "timestamp",
        "status",
        "value",
        "fee",
    )
    missing = [field for field in required if row.get(field) is None]
    if missing:
        raise ValueError(
            f"{path.name}: transaction {row.get('transaction_hash') or '<unknown>'} "
            f"is missing required fields: {', '.join(missing)}"
        )
    return row


def parse_transactions(path: Path) -> list[dict[str, Any]]:
    transactions: list[dict[str, Any]] = []
    seen_hashes: set[str] = set()

    for block in extract_code_blocks(path):
        parsed = parse_block(block)
        if not parsed or "transaction_hash" not in parsed:
            continue
        transaction = parse_transaction_block(path, block)
        tx_hash = transaction["transaction_hash"]
        if tx_hash in seen_hashes:
            continue
        seen_hashes.add(tx_hash)
        transactions.append(transaction)

    if not transactions:
        raise RuntimeError(f"No BlockchainTransaction blocks found in {path}")
    return transactions


def create_tables(cursor) -> None:
    cursor.execute(CREATE_TX_TABLE)
    cursor.execute(CREATE_CCTX_TABLE)
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_chainswap_cctx_dst_tx_hash
        ON chainswap_cross_chain_transactions (dst_transaction_hash)
        """
    )


def upsert_transactions(cursor, rows: list[dict[str, Any]]) -> int:
    placeholders = ", ".join(["%s"] * len(TX_FIELDS))
    update_columns = ", ".join(
        f"{field} = EXCLUDED.{field}"
        for field in TX_FIELDS
        if field != "transaction_hash"
    )
    query = f"""
        INSERT INTO chainswap_blockchain_transactions ({", ".join(TX_FIELDS)})
        VALUES ({placeholders})
        ON CONFLICT (transaction_hash)
        DO UPDATE SET {update_columns}
    """
    cursor.executemany(query, [tuple(row[field] for field in TX_FIELDS) for row in rows])
    return len(rows)


def cctx_id_for(tx: dict[str, Any]) -> str:
    return f"chainswap:{tx['transaction_hash']}"


def build_cctx_rows(transactions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for tx in transactions:
        rows.append(
            {
                "cctx_id": cctx_id_for(tx),
                "src_blockchain": None,
                "src_transaction_hash": None,
                "src_from_address": None,
                "src_to_address": None,
                "src_fee": None,
                "src_fee_usd": None,
                "src_value": None,
                "src_timestamp": None,
                "dst_blockchain": tx["blockchain"],
                "dst_transaction_hash": tx["transaction_hash"],
                "dst_from_address": tx["from_address"],
                "dst_to_address": tx["to_address"],
                "dst_fee": tx["fee"],
                "dst_fee_usd": None,
                "dst_value": tx["value"],
                "dst_timestamp": tx["timestamp"],
                "correlation_id": tx["transaction_hash"],
                "depositor": tx["from_address"],
                "recipient": tx["to_address"],
                "src_contract_address": None,
                "dst_contract_address": tx["to_address"],
                "token_in": None,
                "token_out": None,
                "amount_in": None,
                "amount_out": None,
                "amount_usd": None,
            }
        )
    return rows


def upsert_cctx_rows(cursor, rows: list[dict[str, Any]]) -> int:
    placeholders = ", ".join(["%s"] * len(CCTX_FIELDS))
    update_columns = ", ".join(
        f"{field} = EXCLUDED.{field}" for field in CCTX_FIELDS if field != "cctx_id"
    )
    query = f"""
        INSERT INTO chainswap_cross_chain_transactions ({", ".join(CCTX_FIELDS)})
        VALUES ({placeholders})
        ON CONFLICT (cctx_id)
        DO UPDATE SET {update_columns}
    """
    cursor.executemany(
        query,
        [tuple(row.get(field) for field in CCTX_FIELDS) for row in rows],
    )
    return len(rows)


def import_chainswap_data(database_url: str, data_file: Path) -> dict[str, int]:
    try:
        import psycopg2
        from psycopg2.extras import Json
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Missing PostgreSQL driver. Install psycopg2-binary in the Python "
            "environment used to run this script, then rerun it."
        ) from exc

    transactions = parse_transactions(data_file)
    for tx in transactions:
        if tx["calls"] is not None:
            tx["calls"] = Json(tx["calls"])

    cctx_rows = build_cctx_rows(transactions)

    with psycopg2.connect(database_url) as connection:
        with connection.cursor() as cursor:
            create_tables(cursor)
            tx_count = upsert_transactions(cursor, transactions)
            cctx_count = upsert_cctx_rows(cursor, cctx_rows)

    return {
        "chainswap_blockchain_transactions": tx_count,
        "chainswap_cross_chain_transactions": cctx_count,
    }


def main() -> None:
    args = parse_args()
    data_file = Path(args.data_file).resolve()
    counts = import_chainswap_data(args.database_url, data_file)
    print(
        "Imported/updated "
        f"{counts['chainswap_blockchain_transactions']} chainswap_blockchain_transactions "
        "and "
        f"{counts['chainswap_cross_chain_transactions']} chainswap_cross_chain_transactions."
    )


if __name__ == "__main__":
    main()
