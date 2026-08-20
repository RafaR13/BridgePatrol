#!/usr/bin/env python3
"""Import manually curated bridge transactions and normalized events.

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
MANUAL_LOGS = DATA_DIR / "manual_logs.md"
MANUAL_TXS = DATA_DIR / "manual_txs.md"
THORCHAIN_DATA = DATA_DIR / "thorchain_txs_and_logs.md"
THORCHAIN2_DATA = DATA_DIR / "thorchain2_txs_and_logs.md"
THORCHAIN_DATA_FILES = (THORCHAIN_DATA, THORCHAIN2_DATA)
BRIDGE_TRANSACTION_TABLES = {
    "meterio": "meterio_blockchain_transactions",
    "qubit": "qubit_blockchain_transactions",
    "thorchain": "thorchain_blockchain_transactions",
}
BRIDGE_CCTX_TABLES = {
    "meterio": "meterio_cross_chain_transactions",
    "qubit": "qubit_cross_chain_transactions",
    "thorchain": "thorchain_cross_chain_transactions",
}
BRIDGE_NORMALIZED_EVENT_TABLES = {
    "meterio": ("meter.io", "meter_io_normalized_event"),
    "qubit": ("qubit", "qubit_normalized_event"),
    "thorchain": ("thorchain", "thorchain_normalized_event"),
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

EVENT_FIELDS = (
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

INTEGER_FIELDS = {"block_number", "timestamp", "log_index"}
TX_INTEGER_FIELDS = {"block_number", "timestamp", "status"}
NUMERIC_FIELDS = {"amount_in", "amount_out", "value", "fee"}
EMPTY_VALUES = {"", "NULL", "UNKNOWN"}
REQUIRED_TX_FIELDS = (
    "blockchain",
    "transaction_hash",
    "block_number",
    "timestamp",
    "status",
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


CREATE_TX_TABLE = """
CREATE TABLE IF NOT EXISTS {table_name} (
    blockchain VARCHAR(16) NOT NULL,
    transaction_hash VARCHAR(128) PRIMARY KEY,
    block_number BIGINT NOT NULL,
    timestamp BIGINT NOT NULL,
    from_address VARCHAR(128),
    to_address VARCHAR(128),
    status INTEGER NOT NULL,
    value NUMERIC(50, 18),
    input_data VARCHAR(35000),
    calls JSONB,
    fee NUMERIC(50, 18) NOT NULL
)
"""

CREATE_NORMALIZED_EVENT_TABLE = """
CREATE TABLE IF NOT EXISTS {table_name} (
    id BIGSERIAL PRIMARY KEY,
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
    amount_in NUMERIC(50, 0),
    amount_out NUMERIC(50, 0),
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

CREATE_CCTX_TABLE = """
CREATE TABLE IF NOT EXISTS {table_name} (
    id BIGSERIAL PRIMARY KEY,
    cctx_id VARCHAR(128) NOT NULL UNIQUE,
    src_blockchain VARCHAR(16),
    src_transaction_hash VARCHAR(128),
    src_from_address VARCHAR(128),
    src_to_address VARCHAR(128),
    src_fee NUMERIC(50, 18),
    src_fee_usd DOUBLE PRECISION,
    src_value NUMERIC(50, 18),
    src_timestamp BIGINT,
    dst_blockchain VARCHAR(16),
    dst_transaction_hash VARCHAR(128),
    dst_from_address VARCHAR(128),
    dst_to_address VARCHAR(128),
    dst_fee NUMERIC(50, 18),
    dst_fee_usd DOUBLE PRECISION,
    dst_value NUMERIC(50, 18),
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


def extract_code_blocks(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return re.findall(r"```(?:\w+)?\n(.*?)```", text, flags=re.DOTALL)


def parse_block(block: str) -> dict[str, str]:
    values: dict[str, str] = {}
    lines = block.splitlines()
    index = 0

    while index < len(lines):
        line = lines[index].rstrip()
        index += 1
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if value == "{":
            collected = ["{"]
            while index < len(lines):
                collected.append(lines[index].rstrip())
                if lines[index].strip().rstrip(",") == "}":
                    index += 1
                    break
                index += 1
            value = "\n".join(collected)

        values[key] = value

    return values


def clean_scalar(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if value.endswith(","):
        value = value[:-1].rstrip()
    if value in EMPTY_VALUES or value == "None":
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


def canonical_bridge(raw_bridge: str | None) -> str | None:
    if raw_bridge is None:
        return None
    normalized = raw_bridge.strip().lower().replace("_", "").replace(".", "")
    if normalized in {"meter", "meterio"}:
        return "meterio"
    if normalized in {"qubit", "qubitbridge"}:
        return "qubit"
    if normalized == "thorchain":
        return "thorchain"
    return normalized or None


def detector_bridge_name(bridge: str) -> str:
    try:
        return BRIDGE_NORMALIZED_EVENT_TABLES[bridge][0]
    except KeyError as exc:
        raise ValueError(f"Unsupported bridge for normalized events: {bridge}") from exc


def normalized_event_table_for_event(row: dict[str, Any]) -> str:
    bridge = canonical_bridge(row.get("bridge"))
    if bridge is None:
        raise ValueError(f"Normalized event {row.get('raw_pk')!r} has no bridge")
    try:
        return BRIDGE_NORMALIZED_EVENT_TABLES[bridge][1]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported bridge for normalized events: {row.get('bridge')!r}"
        ) from exc


def cctx_id_for(bridge: str, label: str) -> str:
    normalized_label = re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")
    return f"{bridge}:{normalized_label}"


def generated_event_raw_pk(
    row: dict[str, Any],
    ordinal: int,
    source_name: str = "manual_logs",
) -> str:
    log_index = row.get("log_index")
    log_part = "unknown" if log_index is None else str(log_index)
    return ":".join(
        [
            source_name,
            str(row["bridge"]).lower(),
            str(row["blockchain"]).lower(),
            str(row["transaction_hash"]),
            log_part,
            str(row["event_type"]),
            str(ordinal),
        ]
    )


def parse_event_block(path: Path, block: str, ordinal: int) -> dict[str, Any]:
    parsed = parse_block(block)
    row: dict[str, Any] = {}
    for field in EVENT_FIELDS:
        if field == "id":
            continue
        if field in INTEGER_FIELDS:
            row[field] = clean_int(parsed.get(field))
        elif field in NUMERIC_FIELDS:
            row[field] = clean_decimal(parsed.get(field))
        else:
            row[field] = clean_scalar(parsed.get(field))

    row["raw_table"] = row["raw_table"] or path.name
    row["raw_pk"] = row["raw_pk"] or generated_event_raw_pk(
        row,
        ordinal,
        path.stem,
    )
    return row


def parse_manual_events(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for block in extract_code_blocks(path):
        if block.lstrip().startswith("BlockchainTransaction("):
            continue
        parsed = parse_block(block)
        if not parsed or "transaction_hash" not in parsed:
            continue
        events.append(parse_event_block(path, block, len(events) + 1))
    return events


def parse_transaction_block(path: Path, block: str) -> dict[str, Any]:
    parsed = parse_block(block)
    row: dict[str, Any] = {}
    for field in TX_FIELDS:
        if field in TX_INTEGER_FIELDS:
            row[field] = clean_int(parsed.get(field))
        elif field in NUMERIC_FIELDS:
            row[field] = clean_decimal(parsed.get(field))
        else:
            row[field] = clean_scalar(parsed.get(field))

    missing_fields = [field for field in REQUIRED_TX_FIELDS if row[field] is None]
    if missing_fields:
        missing = ", ".join(missing_fields)
        transaction_hash = row["transaction_hash"] or "<unknown hash>"
        raise ValueError(
            f"{path.name}: transaction {transaction_hash} is missing required fields: {missing}"
        )
    return row


def parse_manual_transactions(path: Path) -> dict[str, list[dict[str, Any]]]:
    grouped = {bridge: [] for bridge in BRIDGE_TRANSACTION_TABLES}
    current_bridge: str | None = None
    text = path.read_text(encoding="utf-8")
    parts = re.split(r"(^# .*$)", text, flags=re.MULTILINE)

    for index in range(1, len(parts), 2):
        heading = parts[index].strip().lower()
        section = parts[index + 1]
        if "meter" in heading:
            current_bridge = "meterio"
        elif "qubit" in heading:
            current_bridge = "qubit"
        else:
            current_bridge = None

        if current_bridge is None:
            continue

        for block in re.findall(r"```(?:\w+)?\n(.*?)```", section, flags=re.DOTALL):
            parsed = parse_block(block)
            if not parsed or "transaction_hash" not in parsed:
                continue
            grouped[current_bridge].append(parse_transaction_block(path, block))

    return grouped


def parse_manual_transaction_groups(
    path: Path,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[dict[str, Any]]]]:
    transactions = {bridge: [] for bridge in BRIDGE_TRANSACTION_TABLES}
    cctx_groups = {bridge: [] for bridge in BRIDGE_TRANSACTION_TABLES}
    current_bridge: str | None = None
    current_cctx_label: str | None = None
    current_rows: list[dict[str, Any]] = []
    synthetic_counters = {bridge: 0 for bridge in BRIDGE_TRANSACTION_TABLES}

    def flush_group() -> None:
        nonlocal current_cctx_label, current_rows
        if current_bridge is None or not current_rows:
            current_rows = []
            return

        label = current_cctx_label
        if label is None:
            for row in current_rows:
                synthetic_counters[current_bridge] += 1
                generated_id = cctx_id_for(
                    current_bridge,
                    f"manual_tx_{synthetic_counters[current_bridge]}",
                )
                row["cctx_id"] = generated_id
                cctx_groups[current_bridge].append(
                    {"cctx_id": generated_id, "transactions": [row]}
                )
        else:
            generated_id = cctx_id_for(current_bridge, label)
            for row in current_rows:
                row["cctx_id"] = generated_id
            cctx_groups[current_bridge].append(
                {"cctx_id": generated_id, "transactions": list(current_rows)}
            )
        current_rows = []

    text = path.read_text(encoding="utf-8")
    chunks = re.split(r"(^#{1,2} .*$)", text, flags=re.MULTILINE)

    for chunk in chunks:
        stripped = chunk.strip()
        lower = stripped.lower()
        if lower.startswith("# "):
            flush_group()
            current_cctx_label = None
            if "meter" in lower:
                current_bridge = "meterio"
            elif "qubit" in lower:
                current_bridge = "qubit"
            else:
                current_bridge = None
            continue

        if lower.startswith("## cctx"):
            flush_group()
            current_cctx_label = stripped.lstrip("#").strip()
            continue

        if current_bridge is None:
            continue

        for block in re.findall(r"```(?:\w+)?\n(.*?)```", chunk, flags=re.DOTALL):
            parsed = parse_block(block)
            if not parsed or "transaction_hash" not in parsed:
                continue
            row = parse_transaction_block(path, block)
            current_rows.append(row)
            transactions[current_bridge].append(row)

    flush_group()
    return transactions, cctx_groups


def parse_thorchain_data(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    transactions: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []

    for block in extract_code_blocks(path):
        block_type = block.lstrip()
        if block_type.startswith("BlockchainTransaction("):
            transaction = parse_transaction_block(path, block)
            transaction["cctx_id"] = cctx_id_for("thorchain", transaction["transaction_hash"])
            transactions.append(transaction)
        elif block_type.startswith("NormalizedEvent("):
            event = parse_event_block(path, block, len(events) + 1)
            bridge = canonical_bridge(event.get("bridge"))
            if bridge != "thorchain":
                raise ValueError(
                    f"{path.name}: expected a thorchain event, got {event['bridge']!r}"
                )
            event["bridge"] = detector_bridge_name(bridge)
            event["cctx_id"] = event["cctx_id"] or cctx_id_for(
                bridge,
                event["transaction_hash"],
            )
            events.append(event)

    return transactions, events


def create_tables(cursor) -> None:
    for table_name in BRIDGE_TRANSACTION_TABLES.values():
        cursor.execute(CREATE_TX_TABLE.format(table_name=table_name))
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS calls JSONB")
    for table_name in BRIDGE_CCTX_TABLES.values():
        cursor.execute(CREATE_CCTX_TABLE.format(table_name=table_name))
    for _, table_name in BRIDGE_NORMALIZED_EVENT_TABLES.values():
        cursor.execute(CREATE_NORMALIZED_EVENT_TABLE.format(table_name=table_name))


def upsert_transactions(cursor, table_name: str, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0

    placeholders = ", ".join(["%s"] * len(TX_FIELDS))
    update_columns = ", ".join(
        f"{field} = EXCLUDED.{field}"
        for field in TX_FIELDS
        if field != "transaction_hash"
    )
    query = f"""
        INSERT INTO {table_name} ({", ".join(TX_FIELDS)})
        VALUES ({placeholders})
        ON CONFLICT (transaction_hash)
        DO UPDATE SET {update_columns}
    """
    cursor.executemany(query, [tuple(row[field] for field in TX_FIELDS) for row in rows])
    return len(rows)


def upsert_events(cursor, rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = {table_name: 0 for _, table_name in BRIDGE_NORMALIZED_EVENT_TABLES.values()}
    event_columns = ", ".join(EVENT_FIELDS)
    event_placeholders = ", ".join(["%s"] * len(EVENT_FIELDS))
    update_assignments = ", ".join(f"{field} = %s" for field in EVENT_FIELDS)

    for row in rows:
        table_name = normalized_event_table_for_event(row)
        cursor.execute(f"SELECT id FROM {table_name} WHERE raw_pk = %s LIMIT 1", (row["raw_pk"],))
        result = cursor.fetchone()

        if result is None:
            cursor.execute(
                f"INSERT INTO {table_name} ({event_columns}) VALUES ({event_placeholders})",
                tuple(row[field] for field in EVENT_FIELDS),
            )
        else:
            cursor.execute(
                f"UPDATE {table_name} SET {update_assignments} WHERE id = %s",
                tuple(row[field] for field in EVENT_FIELDS) + (result[0],),
            )
        counts[table_name] += 1

    return counts


def first_present(rows: list[dict[str, Any]], *fields: str):
    for row in rows:
        for field in fields:
            value = row.get(field)
            if value is not None:
                return value
    return None


def transaction_side_payload(prefix: str, tx: dict[str, Any] | None) -> dict[str, Any]:
    if tx is None:
        return {
            f"{prefix}_blockchain": None,
            f"{prefix}_transaction_hash": None,
            f"{prefix}_from_address": None,
            f"{prefix}_to_address": None,
            f"{prefix}_fee": None,
            f"{prefix}_fee_usd": None,
            f"{prefix}_value": None,
            f"{prefix}_timestamp": None,
        }
    return {
        f"{prefix}_blockchain": tx.get("blockchain"),
        f"{prefix}_transaction_hash": tx.get("transaction_hash"),
        f"{prefix}_from_address": tx.get("from_address"),
        f"{prefix}_to_address": tx.get("to_address"),
        f"{prefix}_fee": tx.get("fee"),
        f"{prefix}_fee_usd": None,
        f"{prefix}_value": tx.get("value"),
        f"{prefix}_timestamp": tx.get("timestamp"),
    }


def build_cctx_row(
    cctx_id: str,
    transactions: list[dict[str, Any]],
    events: list[dict[str, Any]],
    single_transaction_side: str | None = None,
) -> dict[str, Any]:
    sorted_transactions = sorted(
        transactions,
        key=lambda row: (
            row.get("timestamp") if row.get("timestamp") is not None else 0,
            str(row.get("transaction_hash") or ""),
        ),
    )
    if len(sorted_transactions) == 1:
        if single_transaction_side == "src":
            src_tx = sorted_transactions[0]
            dst_tx = None
        elif single_transaction_side == "dst":
            src_tx = None
            dst_tx = sorted_transactions[0]
        else:
            src_tx = None
            dst_tx = None
    else:
        src_tx = sorted_transactions[0] if sorted_transactions else None
        dst_tx = sorted_transactions[-1] if sorted_transactions else None

    source_events = [
        event
        for event in events
        if src_tx is not None and event.get("transaction_hash") == src_tx.get("transaction_hash")
    ]
    destination_events = [
        event
        for event in events
        if dst_tx is not None and event.get("transaction_hash") == dst_tx.get("transaction_hash")
    ]

    row = {"cctx_id": cctx_id}
    row.update(transaction_side_payload("src", src_tx))
    row.update(transaction_side_payload("dst", dst_tx))
    row.update(
        {
            "correlation_id": first_present(events, "correlation_id"),
            "depositor": first_present(source_events, "actor_from", "signer")
            or first_present(events, "actor_from", "signer"),
            "recipient": first_present(destination_events, "actor_to")
            or first_present(events, "actor_to"),
            "src_contract_address": first_present(source_events, "contract_address"),
            "dst_contract_address": first_present(destination_events, "contract_address"),
            "token_in": first_present(source_events, "token_in")
            or first_present(events, "token_in"),
            "token_out": first_present(destination_events, "token_out")
            or first_present(events, "token_out"),
            "amount_in": first_present(source_events, "amount_in")
            or first_present(events, "amount_in"),
            "amount_out": first_present(destination_events, "amount_out")
            or first_present(events, "amount_out"),
            "amount_usd": None,
        }
    )
    return row


def build_cctx_rows(
    cctx_groups: dict[str, list[dict[str, Any]]],
    events: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    events_by_cctx: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        if event.get("cctx_id") is not None:
            events_by_cctx.setdefault(event["cctx_id"], []).append(event)

    rows_by_bridge = {bridge: [] for bridge in BRIDGE_CCTX_TABLES}
    seen_ids: set[str] = set()
    for bridge, groups in cctx_groups.items():
        for group in groups:
            cctx_id = group["cctx_id"]
            seen_ids.add(cctx_id)
            rows_by_bridge[bridge].append(
                build_cctx_row(
                    cctx_id,
                    group["transactions"],
                    events_by_cctx.get(cctx_id, []),
                    single_transaction_side=group.get("single_transaction_side"),
                )
            )

    for cctx_id, grouped_events in events_by_cctx.items():
        if cctx_id in seen_ids:
            continue
        bridge = canonical_bridge(first_present(grouped_events, "bridge"))
        if bridge not in rows_by_bridge:
            continue
        rows_by_bridge[bridge].append(build_cctx_row(cctx_id, [], grouped_events))

    return rows_by_bridge


def upsert_cctx_rows(cursor, table_name: str, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0

    placeholders = ", ".join(["%s"] * len(CCTX_FIELDS))
    update_columns = ", ".join(
        f"{field} = EXCLUDED.{field}" for field in CCTX_FIELDS if field != "cctx_id"
    )
    query = f"""
        INSERT INTO {table_name} ({", ".join(CCTX_FIELDS)})
        VALUES ({placeholders})
        ON CONFLICT (cctx_id)
        DO UPDATE SET {update_columns}
    """
    cursor.executemany(
        query,
        [tuple(row.get(field) for field in CCTX_FIELDS) for row in rows],
    )
    return len(rows)


def parse_manual_event_groups(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    current_bridge: str | None = None
    current_cctx_label: str | None = None
    text = path.read_text(encoding="utf-8")
    chunks = re.split(r"(^#{1,3} .*$)", text, flags=re.MULTILINE)

    for chunk in chunks:
        stripped = chunk.strip()
        lower = stripped.lower()
        if lower.startswith("# "):
            if "meter" in lower:
                current_bridge = "meterio"
            elif "qubit" in lower:
                current_bridge = "qubit"
            else:
                current_bridge = None
            current_cctx_label = None
            continue
        if lower.startswith("## cctx"):
            current_cctx_label = stripped.lstrip("#").strip()
            continue

        for block in re.findall(r"```(?:\w+)?\n(.*?)```", chunk, flags=re.DOTALL):
            if block.lstrip().startswith("BlockchainTransaction("):
                continue
            parsed = parse_block(block)
            if not parsed or "transaction_hash" not in parsed:
                continue
            event = parse_event_block(path, block, len(events) + 1)
            bridge = canonical_bridge(event.get("bridge")) or current_bridge
            if bridge is not None:
                event["bridge"] = detector_bridge_name(bridge)
            if event.get("cctx_id") is None and bridge is not None and current_cctx_label:
                event["cctx_id"] = cctx_id_for(bridge, current_cctx_label)
            events.append(event)

    return events


def import_manual_data(database_url: str) -> dict[str, int]:
    try:
        import psycopg2
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Missing PostgreSQL driver. Install psycopg2-binary in the Python environment "
            "used to run this script, then rerun it."
        ) from exc

    events = parse_manual_event_groups(MANUAL_LOGS)
    transactions, cctx_groups = parse_manual_transaction_groups(MANUAL_TXS)
    for thorchain_path in THORCHAIN_DATA_FILES:
        thorchain_transactions, thorchain_events = parse_thorchain_data(
            thorchain_path
        )
        transactions["thorchain"].extend(thorchain_transactions)
        for transaction in thorchain_transactions:
            cctx_groups["thorchain"].append(
                {
                    "cctx_id": transaction["cctx_id"],
                    "transactions": [transaction],
                    "single_transaction_side": "src",
                }
            )
        events.extend(thorchain_events)
    cctx_rows = build_cctx_rows(cctx_groups, events)

    with psycopg2.connect(database_url) as connection:
        with connection.cursor() as cursor:
            create_tables(cursor)
            transaction_counts = {}
            for bridge, table_name in BRIDGE_TRANSACTION_TABLES.items():
                transaction_counts[table_name] = upsert_transactions(
                    cursor,
                    table_name,
                    transactions[bridge],
                )
            event_counts = upsert_events(cursor, events)
            cctx_counts = {}
            for bridge, table_name in BRIDGE_CCTX_TABLES.items():
                cctx_counts[table_name] = upsert_cctx_rows(
                    cursor,
                    table_name,
                    cctx_rows[bridge],
                )

    return transaction_counts | event_counts | cctx_counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Import manual bridge data into PostgreSQL.")
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL),
        help=f"PostgreSQL URL. Defaults to {DEFAULT_DATABASE_URL}",
    )
    args = parser.parse_args()

    counts = import_manual_data(args.database_url)
    event_total = sum(
        count
        for table_name, count in counts.items()
        if table_name.endswith("_normalized_event")
    )
    transaction_summary = ", ".join(
        f"{count} {table_name}"
        for table_name, count in counts.items()
        if not table_name.endswith("_normalized_event")
    )
    event_summary = ", ".join(
        f"{count} {table_name}"
        for table_name, count in counts.items()
        if table_name.endswith("_normalized_event")
    )
    print(
        "Imported/updated "
        f"{event_total} normalized events ({event_summary}) and "
        f"{transaction_summary}."
    )


if __name__ == "__main__":
    main()
