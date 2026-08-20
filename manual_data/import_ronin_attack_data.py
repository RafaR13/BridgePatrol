#!/usr/bin/env python3
"""Import the curated 2022 Ronin Bridge attacker transactions.

Defaults to the local xchain_test database used in this workspace:
postgresql://admin:pwd@localhost:5432/xchain_test
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from decimal import Decimal
from pathlib import Path
from typing import Any

DEFAULT_DATABASE_URL = "postgresql://admin:pwd@localhost:5432/xchain_test"
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_FILE = DATA_DIR / "ronin_attack_transactions_2022.md"

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
    "id",
    "src_blockchain",
    "src_transaction_hash",
    "src_from_address",
    "src_to_address",
    "src_fee",
    "src_fee_usd",
    "src_timestamp",
    "dst_blockchain",
    "dst_transaction_hash",
    "dst_from_address",
    "dst_to_address",
    "dst_fee",
    "dst_fee_usd",
    "dst_timestamp",
    "deposit_id",
    "depositor",
    "recipient",
    "src_contract_address",
    "dst_contract_address",
    "amount",
    "amount_usd",
)

RONIN_TOKEN_WITHDREW_FIELDS = (
    "id",
    "blockchain",
    "transaction_hash",
    "withdrawal_id",
    "kind",
    "src_blockchain",
    "withdrawer",
    "input_token",
    "recipient",
    "output_token",
    "token_standard",
    "amount",
)

NORMALIZED_EVENT_FIELDS = (
    "id",
    "bridge",
    "blockchain",
    "raw_table",
    "raw_pk",
    "transaction_hash",
    "cctx_id",
    "block_number",
    "timestamp",
    "log_index",
    "event_type",
    "correlation_id",
    "src_blockchain",
    "dst_blockchain",
    "actor_from",
    "actor_to",
    "signer",
    "relayer",
    "token_in",
    "token_out",
    "amount_in",
    "amount_out",
    "nonce",
    "message_id",
    "message_hash",
    "payload_hash",
    "proof_hash",
    "guid",
    "contract_address",
    "status",
    "extra_data",
)

TRANSFER_FIELDS = (
    "id",
    "blockchain",
    "transaction_hash",
    "block_number",
    "log_index",
    "token_address",
    "from_address",
    "to_address",
    "amount",
    "trigger_event_topic",
    "trigger_contract_address",
)

NUMERIC_FIELDS = {
    "amount",
    "amount_in",
    "amount_out",
    "dst_fee",
    "fee",
    "src_fee",
    "value",
}

CREATE_TX_TABLE = """
CREATE TABLE IF NOT EXISTS ronin_blockchain_transactions (
    blockchain VARCHAR(16) NOT NULL,
    transaction_hash VARCHAR(128) PRIMARY KEY,
    block_number BIGINT NOT NULL,
    timestamp BIGINT NOT NULL,
    from_address VARCHAR(128),
    to_address VARCHAR(128),
    status INTEGER NOT NULL,
    value NUMERIC(78, 0),
    input_data VARCHAR(35000),
    calls JSONB,
    fee NUMERIC(78, 0) NOT NULL
)
"""

CREATE_CCTX_TABLE = """
CREATE TABLE IF NOT EXISTS ronin_cross_chain_transactions (
    id BIGINT PRIMARY KEY,
    src_blockchain VARCHAR(16),
    src_transaction_hash VARCHAR(128),
    src_from_address VARCHAR(128),
    src_to_address VARCHAR(128),
    src_fee NUMERIC(78, 0),
    src_fee_usd DOUBLE PRECISION,
    src_timestamp BIGINT,
    dst_blockchain VARCHAR(16),
    dst_transaction_hash VARCHAR(128),
    dst_from_address VARCHAR(128),
    dst_to_address VARCHAR(128),
    dst_fee NUMERIC(78, 0),
    dst_fee_usd DOUBLE PRECISION,
    dst_timestamp BIGINT,
    deposit_id BIGINT,
    depositor VARCHAR(128),
    recipient VARCHAR(128),
    src_contract_address VARCHAR(128),
    dst_contract_address VARCHAR(128),
    amount NUMERIC(78, 0),
    amount_usd DOUBLE PRECISION
)
"""

CREATE_RONIN_TOKEN_WITHDREW_TABLE = """
CREATE TABLE IF NOT EXISTS ronin_token_withdrew (
    id BIGINT PRIMARY KEY,
    blockchain VARCHAR(16) NOT NULL,
    transaction_hash VARCHAR(128) NOT NULL,
    withdrawal_id BIGINT NOT NULL,
    kind VARCHAR(16) NOT NULL,
    src_blockchain VARCHAR(16) NOT NULL,
    withdrawer VARCHAR(128) NOT NULL,
    input_token VARCHAR(128) NOT NULL,
    recipient VARCHAR(128) NOT NULL,
    output_token VARCHAR(128) NOT NULL,
    token_standard VARCHAR(16) NOT NULL,
    amount NUMERIC(78, 0) NOT NULL
)
"""

CREATE_NORMALIZED_EVENT_TABLE = """
CREATE TABLE IF NOT EXISTS ronin_normalized_event (
    id BIGINT PRIMARY KEY,
    bridge VARCHAR(32) NOT NULL,
    blockchain VARCHAR(16) NOT NULL,
    raw_table VARCHAR(128) NOT NULL,
    raw_pk VARCHAR(256) NOT NULL,
    transaction_hash VARCHAR(128) NOT NULL,
    cctx_id VARCHAR(128),
    block_number BIGINT,
    timestamp BIGINT,
    log_index INTEGER,
    event_type VARCHAR(64) NOT NULL,
    correlation_id VARCHAR(128),
    src_blockchain VARCHAR(16),
    dst_blockchain VARCHAR(16),
    actor_from VARCHAR(128),
    actor_to VARCHAR(128),
    signer VARCHAR(128),
    relayer VARCHAR(128),
    token_in VARCHAR(128),
    token_out VARCHAR(128),
    amount_in NUMERIC(78, 0),
    amount_out NUMERIC(78, 0),
    nonce VARCHAR(128),
    message_id VARCHAR(128),
    message_hash VARCHAR(128),
    payload_hash VARCHAR(128),
    proof_hash VARCHAR(128),
    guid VARCHAR(128),
    contract_address VARCHAR(128),
    status VARCHAR(32),
    extra_data VARCHAR(20000)
)
"""

CREATE_TRANSFER_TABLE = """
CREATE TABLE IF NOT EXISTS ronin_transfers (
    id BIGINT PRIMARY KEY,
    blockchain VARCHAR(16) NOT NULL,
    transaction_hash VARCHAR(128) NOT NULL,
    block_number BIGINT NOT NULL,
    log_index INTEGER NOT NULL,
    token_address VARCHAR(128) NOT NULL,
    from_address VARCHAR(128) NOT NULL,
    to_address VARCHAR(128) NOT NULL,
    amount NUMERIC(78, 0) NOT NULL,
    trigger_event_topic VARCHAR(66) NOT NULL,
    trigger_contract_address VARCHAR(128) NOT NULL
)
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import Ronin attack transactions/events into PostgreSQL."
    )
    parser.add_argument(
        "--database-url",
        default=os.getenv("RONIN_ATTACK_DATABASE_URL", DEFAULT_DATABASE_URL),
        help=f"PostgreSQL URL. Defaults to {DEFAULT_DATABASE_URL}",
    )
    parser.add_argument(
        "--data-file",
        default=str(DEFAULT_DATA_FILE),
        help=f"Markdown file to import. Defaults to {DEFAULT_DATA_FILE}",
    )
    return parser.parse_args()


def decimalize(value: Any) -> Any:
    if isinstance(value, int):
        return Decimal(value)
    return value


def parse_json_blocks(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    blocks = re.findall(r"```json\n(.*?)```", text, flags=re.DOTALL)
    rows: list[dict[str, Any]] = []
    for block in blocks:
        rows.append(json.loads(block))
    return rows


def split_rows(rows: list[dict[str, Any]]) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    transactions = [row for row in rows if set(TX_FIELDS).issubset(row)]
    cctx_rows = [row for row in rows if "deposit_id" in row and "dst_transaction_hash" in row]
    token_withdrew_rows = [
        row for row in rows if "withdrawal_id" in row and "withdrawer" in row
    ]
    transfer_rows = [row for row in rows if "trigger_event_topic" in row]

    if not transactions:
        raise RuntimeError("No BlockchainTransaction JSON blocks found.")
    if not cctx_rows:
        raise RuntimeError("No RoninCrossChainTransaction JSON blocks found.")
    if not token_withdrew_rows:
        raise RuntimeError("No RoninTokenWithdrew JSON blocks found.")

    return transactions, cctx_rows, token_withdrew_rows, transfer_rows


def normalize_numeric_fields(row: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(row)
    for field in NUMERIC_FIELDS:
        if field in normalized and normalized[field] is not None:
            normalized[field] = decimalize(normalized[field])
    return normalized


def next_id(cursor, table: str) -> int:
    cursor.execute(f"SELECT COALESCE(MAX(id), 0) + 1 FROM {table}")
    return int(cursor.fetchone()[0])


def create_tables(cursor) -> None:
    cursor.execute(CREATE_TX_TABLE)
    cursor.execute(CREATE_CCTX_TABLE)
    cursor.execute(CREATE_RONIN_TOKEN_WITHDREW_TABLE)
    cursor.execute(CREATE_NORMALIZED_EVENT_TABLE)
    cursor.execute(CREATE_TRANSFER_TABLE)
    cursor.execute(
        """
        ALTER TABLE ronin_cross_chain_transactions
            ALTER COLUMN src_transaction_hash DROP NOT NULL,
            ALTER COLUMN src_from_address DROP NOT NULL,
            ALTER COLUMN src_to_address DROP NOT NULL,
            ALTER COLUMN src_fee DROP NOT NULL,
            ALTER COLUMN src_timestamp DROP NOT NULL
        """
    )
    cursor.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ux_ronin_cctx_deposit_id
        ON ronin_cross_chain_transactions (deposit_id)
        """
    )
    cursor.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ux_ronin_token_withdrew_withdrawal_id
        ON ronin_token_withdrew (withdrawal_id)
        """
    )
    cursor.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ux_ronin_normalized_event_raw
        ON ronin_normalized_event (raw_table, raw_pk)
        """
    )
    cursor.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ux_ronin_transfers_tx_log_token
        ON ronin_transfers (transaction_hash, log_index, token_address)
        """
    )


def upsert_by_conflict(cursor, table: str, fields: tuple[str, ...], conflict: str, rows: list[dict[str, Any]]) -> int:
    placeholders = ", ".join(["%s"] * len(fields))
    update_columns = ", ".join(
        f"{field} = EXCLUDED.{field}" for field in fields if field != "id"
    )
    query = f"""
        INSERT INTO {table} ({", ".join(fields)})
        VALUES ({placeholders})
        ON CONFLICT {conflict}
        DO UPDATE SET {update_columns}
    """
    cursor.executemany(query, [tuple(row.get(field) for field in fields) for row in rows])
    return len(rows)


def upsert_transactions(cursor, rows: list[dict[str, Any]]) -> int:
    prepared = []
    for row in rows:
        payload = normalize_numeric_fields({field: row.get(field) for field in TX_FIELDS})
        prepared.append(payload)

    placeholders = ", ".join(["%s"] * len(TX_FIELDS))
    update_columns = ", ".join(
        f"{field} = EXCLUDED.{field}"
        for field in TX_FIELDS
        if field != "transaction_hash"
    )
    query = f"""
        INSERT INTO ronin_blockchain_transactions ({", ".join(TX_FIELDS)})
        VALUES ({placeholders})
        ON CONFLICT (transaction_hash)
        DO UPDATE SET {update_columns}
    """
    cursor.executemany(
        query,
        [tuple(row[field] for field in TX_FIELDS) for row in prepared],
    )
    return len(prepared)


def sql_literal(value: Any, *, json_value: bool = False) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(value)

    if json_value:
        value = json.dumps(value, sort_keys=True)

    escaped = str(value).replace("'", "''")
    literal = f"'{escaped}'"
    return f"{literal}::jsonb" if json_value else literal


def insert_sql(
    table: str,
    fields: tuple[str, ...],
    row: dict[str, Any],
    conflict: str,
    id_expression: str | None = None,
) -> str:
    values = []
    for field in fields:
        if field == "id" and id_expression:
            values.append(id_expression)
        else:
            values.append(sql_literal(row.get(field), json_value=field == "calls"))

    update_columns = ", ".join(
        f"{field} = EXCLUDED.{field}" for field in fields if field != "id"
    )
    return f"""
INSERT INTO {table} ({", ".join(fields)})
VALUES ({", ".join(values)})
ON CONFLICT {conflict}
DO UPDATE SET {update_columns};
"""


def update_then_insert_sql(
    table: str,
    fields: tuple[str, ...],
    row: dict[str, Any],
    where_clause: str,
    id_expression: str,
) -> str:
    assignments = ", ".join(
        f"{field} = {sql_literal(row.get(field))}"
        for field in fields
        if field != "id"
    )
    values = [
        id_expression if field == "id" else sql_literal(row.get(field))
        for field in fields
    ]
    return f"""
UPDATE {table}
SET {assignments}
WHERE {where_clause};

INSERT INTO {table} ({", ".join(fields)})
SELECT {", ".join(values)}
WHERE NOT EXISTS (SELECT 1 FROM {table} WHERE {where_clause});
"""


def run_psql(database_url: str, sql: str) -> None:
    if not shutil.which("psql"):
        raise SystemExit(
            "Missing PostgreSQL driver psycopg2-binary and psql was not found. "
            "Install one of them, then rerun the script."
        )

    subprocess.run(
        ["psql", database_url, "-v", "ON_ERROR_STOP=1"],
        input=sql,
        text=True,
        check=True,
    )


def psql_id_expression(table: str, where_clause: str) -> str:
    return (
        f"COALESCE((SELECT id FROM {table} WHERE {where_clause}), "
        f"(SELECT COALESCE(MAX(id), 0) + 1 FROM {table}))"
    )


def import_with_psql(
    database_url: str,
    transactions: list[dict[str, Any]],
    cctx_rows: list[dict[str, Any]],
    token_withdrew_rows: list[dict[str, Any]],
    normalized_event_rows: list[dict[str, Any]],
    transfer_rows: list[dict[str, Any]],
) -> dict[str, int]:
    ddl = "\n".join(
        [
            f"{CREATE_TX_TABLE};",
            f"{CREATE_CCTX_TABLE};",
            f"{CREATE_RONIN_TOKEN_WITHDREW_TABLE};",
            f"{CREATE_NORMALIZED_EVENT_TABLE};",
            f"{CREATE_TRANSFER_TABLE};",
            """
ALTER TABLE ronin_cross_chain_transactions
    ALTER COLUMN src_transaction_hash DROP NOT NULL,
    ALTER COLUMN src_from_address DROP NOT NULL,
    ALTER COLUMN src_to_address DROP NOT NULL,
    ALTER COLUMN src_fee DROP NOT NULL,
    ALTER COLUMN src_timestamp DROP NOT NULL;
""",
        ]
    )

    statements = [ddl]
    for row in transactions:
        payload = normalize_numeric_fields({field: row.get(field) for field in TX_FIELDS})
        statements.append(
            insert_sql(
                "ronin_blockchain_transactions",
                TX_FIELDS,
                payload,
                "(transaction_hash)",
            )
        )

    for row in cctx_rows:
        payload = normalize_numeric_fields(
            {field: row.get(field) for field in CCTX_FIELDS if field != "id"}
        )
        deposit_id = sql_literal(payload["deposit_id"])
        where_clause = f"deposit_id = {deposit_id}"
        statements.append(
            update_then_insert_sql(
                "ronin_cross_chain_transactions",
                CCTX_FIELDS,
                payload,
                where_clause,
                psql_id_expression("ronin_cross_chain_transactions", where_clause),
            )
        )

    for row in token_withdrew_rows:
        payload = normalize_numeric_fields(
            {
                field: row.get(field)
                for field in RONIN_TOKEN_WITHDREW_FIELDS
                if field != "id"
            }
        )
        withdrawal_id = sql_literal(payload["withdrawal_id"])
        where_clause = f"withdrawal_id = {withdrawal_id}"
        statements.append(
            update_then_insert_sql(
                "ronin_token_withdrew",
                RONIN_TOKEN_WITHDREW_FIELDS,
                payload,
                where_clause,
                psql_id_expression("ronin_token_withdrew", where_clause),
            )
        )

    for row in normalized_event_rows:
        payload = normalize_numeric_fields(row)
        raw_table = sql_literal(payload["raw_table"])
        raw_pk = sql_literal(payload["raw_pk"])
        where_clause = f"raw_table = {raw_table} AND raw_pk = {raw_pk}"
        statements.append(
            update_then_insert_sql(
                "ronin_normalized_event",
                NORMALIZED_EVENT_FIELDS,
                payload,
                where_clause,
                psql_id_expression("ronin_normalized_event", where_clause),
            )
        )

    for row in transfer_rows:
        payload = normalize_numeric_fields(
            {field: row.get(field) for field in TRANSFER_FIELDS if field != "id"}
        )
        transaction_hash = sql_literal(payload["transaction_hash"])
        log_index = sql_literal(payload["log_index"])
        token_address = sql_literal(payload["token_address"])
        where_clause = (
            f"transaction_hash = {transaction_hash} "
            f"AND log_index = {log_index} "
            f"AND token_address = {token_address}"
        )
        statements.append(
            update_then_insert_sql(
                "ronin_transfers",
                TRANSFER_FIELDS,
                payload,
                where_clause,
                psql_id_expression("ronin_transfers", where_clause),
            )
        )

    imported_withdrawal_ids = ", ".join(
        sql_literal(row["withdrawal_id"]) for row in token_withdrew_rows
    )
    statements.append(
        f"""
UPDATE ronin_normalized_event normalized
SET cctx_id = cctx.id::text
FROM ronin_cross_chain_transactions cctx
WHERE normalized.raw_table = 'ronin_token_withdrew'
AND normalized.raw_pk = cctx.deposit_id::text
AND cctx.deposit_id IN ({imported_withdrawal_ids});
"""
    )

    run_psql(database_url, "\n".join(statements))
    return {
        "ronin_blockchain_transactions": len(transactions),
        "ronin_cross_chain_transactions": len(cctx_rows),
        "ronin_token_withdrew": len(token_withdrew_rows),
        "ronin_normalized_event": len(normalized_event_rows),
        "ronin_transfers": len(transfer_rows),
    }


def assign_ids(
    cursor,
    table: str,
    id_lookup_sql: str,
    lookup_params: tuple[str, ...],
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    next_row_id = next_id(cursor, table)
    prepared = []
    for row in rows:
        cursor.execute(id_lookup_sql, tuple(row[param] for param in lookup_params))
        existing = cursor.fetchone()
        payload = dict(row)
        if existing:
            payload["id"] = int(existing[0])
        else:
            payload["id"] = next_row_id
            next_row_id += 1
        prepared.append(payload)
    return prepared


def prepare_cctx_rows(cursor, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    base_rows = [
        normalize_numeric_fields({field: row.get(field) for field in CCTX_FIELDS if field != "id"})
        for row in rows
    ]
    return assign_ids(
        cursor,
        "ronin_cross_chain_transactions",
        "SELECT id FROM ronin_cross_chain_transactions WHERE deposit_id = %s",
        ("deposit_id",),
        base_rows,
    )


def prepare_token_withdrew_rows(cursor, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    base_rows = []
    for row in rows:
        payload = {field: row.get(field) for field in RONIN_TOKEN_WITHDREW_FIELDS if field != "id"}
        base_rows.append(normalize_numeric_fields(payload))
    return assign_ids(
        cursor,
        "ronin_token_withdrew",
        "SELECT id FROM ronin_token_withdrew WHERE withdrawal_id = %s",
        ("withdrawal_id",),
        base_rows,
    )


def build_normalized_event_rows(
    token_withdrew_rows: list[dict[str, Any]],
    transactions_by_hash: dict[str, dict[str, Any]],
    cctx_id_by_withdrawal_id: dict[int, int] | None = None,
) -> list[dict[str, Any]]:
    cctx_id_by_withdrawal_id = cctx_id_by_withdrawal_id or {}
    normalized_rows = []
    for row in token_withdrew_rows:
        tx = transactions_by_hash.get(row["transaction_hash"], {})
        cctx_id = cctx_id_by_withdrawal_id.get(int(row["withdrawal_id"]))
        normalized_rows.append(
            {
                "bridge": "ronin",
                "blockchain": row["blockchain"],
                "raw_table": "ronin_token_withdrew",
                "raw_pk": str(row["withdrawal_id"]),
                "transaction_hash": row["transaction_hash"],
                "cctx_id": str(cctx_id) if cctx_id is not None else None,
                "block_number": tx.get("block_number"),
                "timestamp": tx.get("timestamp"),
                "log_index": None,
                "event_type": "TOKEN_WITHDREW",
                "correlation_id": str(row["withdrawal_id"]),
                "src_blockchain": row["src_blockchain"],
                "dst_blockchain": row["blockchain"],
                "actor_from": row["withdrawer"],
                "actor_to": row["recipient"],
                "signer": None,
                "relayer": None,
                "token_in": row["input_token"],
                "token_out": row["output_token"],
                "amount_in": row["amount"],
                "amount_out": row["amount"],
                "nonce": None,
                "message_id": None,
                "message_hash": None,
                "payload_hash": None,
                "proof_hash": None,
                "guid": None,
                "contract_address": row.get("address"),
                "status": str(tx["status"]) if tx.get("status") is not None else None,
                "extra_data": json.dumps(
                    {
                        "kind": row["kind"],
                        "token_standard": row["token_standard"],
                    },
                    sort_keys=True,
                ),
            }
        )
    return normalized_rows


def prepare_normalized_event_rows(cursor, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    base_rows = [normalize_numeric_fields(row) for row in rows]
    return assign_ids(
        cursor,
        "ronin_normalized_event",
        """
        SELECT id
        FROM ronin_normalized_event
        WHERE raw_table = %s AND raw_pk = %s
        """,
        ("raw_table", "raw_pk"),
        base_rows,
    )


def prepare_transfer_rows(cursor, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    base_rows = [
        normalize_numeric_fields({field: row.get(field) for field in TRANSFER_FIELDS if field != "id"})
        for row in rows
    ]
    return assign_ids(
        cursor,
        "ronin_transfers",
        """
        SELECT id
        FROM ronin_transfers
        WHERE transaction_hash = %s AND log_index = %s AND token_address = %s
        """,
        ("transaction_hash", "log_index", "token_address"),
        base_rows,
    )


def import_ronin_attack_data(database_url: str, data_file: Path) -> dict[str, int]:
    rows = parse_json_blocks(data_file)
    transactions, cctx_rows, token_withdrew_rows, transfer_rows = split_rows(rows)
    transactions_by_hash = {row["transaction_hash"]: row for row in transactions}

    try:
        import psycopg2
        from psycopg2.extras import Json
    except ModuleNotFoundError:
        normalized_event_rows = build_normalized_event_rows(
            token_withdrew_rows,
            transactions_by_hash,
        )
        return import_with_psql(
            database_url,
            transactions,
            cctx_rows,
            token_withdrew_rows,
            normalized_event_rows,
            transfer_rows,
        )

    with psycopg2.connect(database_url) as connection:
        with connection.cursor() as cursor:
            create_tables(cursor)
            for tx in transactions:
                tx["calls"] = Json(tx["calls"]) if tx.get("calls") is not None else None

            tx_count = upsert_transactions(cursor, transactions)
            prepared_cctx_rows = prepare_cctx_rows(cursor, cctx_rows)
            prepared_token_withdrew_rows = prepare_token_withdrew_rows(cursor, token_withdrew_rows)
            cctx_id_by_withdrawal_id = {
                int(row["deposit_id"]): int(row["id"]) for row in prepared_cctx_rows
            }
            normalized_event_rows = build_normalized_event_rows(
                token_withdrew_rows,
                transactions_by_hash,
                cctx_id_by_withdrawal_id,
            )
            prepared_normalized_event_rows = prepare_normalized_event_rows(
                cursor,
                normalized_event_rows,
            )
            prepared_transfer_rows = prepare_transfer_rows(cursor, transfer_rows)

            cctx_count = upsert_by_conflict(
                cursor,
                "ronin_cross_chain_transactions",
                CCTX_FIELDS,
                "(deposit_id)",
                prepared_cctx_rows,
            )
            token_withdrew_count = upsert_by_conflict(
                cursor,
                "ronin_token_withdrew",
                RONIN_TOKEN_WITHDREW_FIELDS,
                "(withdrawal_id)",
                prepared_token_withdrew_rows,
            )
            normalized_event_count = upsert_by_conflict(
                cursor,
                "ronin_normalized_event",
                NORMALIZED_EVENT_FIELDS,
                "(raw_table, raw_pk)",
                prepared_normalized_event_rows,
            )
            transfer_count = upsert_by_conflict(
                cursor,
                "ronin_transfers",
                TRANSFER_FIELDS,
                "(transaction_hash, log_index, token_address)",
                prepared_transfer_rows,
            )

    return {
        "ronin_blockchain_transactions": tx_count,
        "ronin_cross_chain_transactions": cctx_count,
        "ronin_token_withdrew": token_withdrew_count,
        "ronin_normalized_event": normalized_event_count,
        "ronin_transfers": transfer_count,
    }


def main() -> None:
    args = parse_args()
    counts = import_ronin_attack_data(
        args.database_url,
        Path(args.data_file).resolve(),
    )
    print(
        "Imported/updated "
        f"{counts['ronin_blockchain_transactions']} ronin_blockchain_transactions, "
        f"{counts['ronin_cross_chain_transactions']} ronin_cross_chain_transactions, "
        f"{counts['ronin_token_withdrew']} ronin_token_withdrew, "
        f"{counts['ronin_normalized_event']} ronin_normalized_event, and "
        f"{counts['ronin_transfers']} ronin_transfers."
    )


if __name__ == "__main__":
    main()
