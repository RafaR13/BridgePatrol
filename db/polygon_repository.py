from sqlalchemy import text
from .connection import get_session

def fetch_polygon_locked_tokens(limit=10):
    session = get_session()
    try:
        result = session.execute(
            text("""
                SELECT *
                FROM polygon_locked_token
                ORDER BY id
                LIMIT :limit
            """),
            {"limit": limit},
        )
        return result.fetchall()
    finally:
        session.close()


def fetch_polygon_cctx_by_src_tx_hash(src_tx_hash):
    session = get_session()
    try:
        result = session.execute(
            text("""
                SELECT *
                FROM polygon_cross_chain_transactions
                WHERE src_transaction_hash = :src_tx_hash
                LIMIT 1
            """),
            {"src_tx_hash": src_tx_hash},
        )
        return result.fetchone()
    finally:
        session.close()


def fetch_polygon_lock_without_cctx(limit=20):
    session = get_session()
    try:
        result = session.execute(
            text("""
                SELECT l.*
                FROM polygon_locked_token l
                LEFT JOIN polygon_cross_chain_transactions c
                  ON l.transaction_hash = c.src_transaction_hash
                WHERE c.src_transaction_hash IS NULL
                ORDER BY l.id
                LIMIT :limit
            """),
            {"limit": limit},
        )
        return result.fetchall()
    finally:
        session.close()


def fetch_polygon_cctxs_without_dst(limit=20):
    session = get_session()
    try:
        result = session.execute(
            text("""
                SELECT *
                FROM polygon_cross_chain_transactions
                WHERE dst_transaction_hash IS NULL
                   OR dst_transaction_hash = ''
                ORDER BY id
                LIMIT :limit
            """),
            {"limit": limit},
        )
        return result.fetchall()
    finally:
        session.close()