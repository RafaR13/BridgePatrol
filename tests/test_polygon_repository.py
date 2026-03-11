from db.repository import *
from db.polygon_repository import *


def test_fetch_polygon_cctxs():
    rows = fetch_bridge_cctxs("polygon", limit=5)
    assert rows is not None


def test_fetch_polygon_locked_tokens():
    rows = fetch_polygon_locked_tokens(limit=5)
    assert rows is not None


def test_polygon_tables_exist():
    tables = list_tables()

    assert "polygon_blockchain_transactions" in tables
    assert "polygon_bridge_withdraw" in tables
    assert "polygon_cross_chain_transactions" in tables
    assert "polygon_exited_token" in tables
    assert "polygon_locked_token" in tables
    assert "polygon_new_deposit_block" in tables
    assert "polygon_plasma_cross_chain_transactions" in tables
    assert "polygon_pol_withdraw" in tables
    assert "polygon_state_committed" in tables
    assert "polygon_state_synced" in tables
    assert "polygon_token_deposited" in tables

def test_polygon_cctx_columns_exist():
    columns = list_columns("polygon_cross_chain_transactions")
    column_names = {col[0] for col in columns}

    assert "id" in column_names
    assert "src_blockchain" in column_names
    assert "src_transaction_hash" in column_names
    assert "src_from_address" in column_names
    assert "src_to_address" in column_names
    assert "src_fee" in column_names
    assert "src_fee_usd" in column_names
    assert "src_timestamp" in column_names
    assert "dst_blockchain" in column_names
    assert "dst_transaction_hash" in column_names
    assert "dst_from_address" in column_names
    assert "dst_to_address" in column_names
    assert "dst_fee" in column_names
    assert "dst_fee_usd" in column_names
    assert "dst_timestamp" in column_names
    assert "deposit_id" in column_names
    assert "depositor" in column_names
    assert "recipient" in column_names
    assert "src_contract_address" in column_names
    assert "amount" in column_names
    assert "amount_usd" in column_names