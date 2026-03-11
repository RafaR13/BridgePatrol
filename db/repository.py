from sqlalchemy import text
from .connection import get_session


def list_tables():
    session = get_session()

    result = session.execute(
        text("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
        ORDER BY table_name;
        """)
    )

    tables = [row[0] for row in result]

    session.close()

    return tables

def list_columns(table_name):
    session = get_session()

    result = session.execute(
        text("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = :table_name
        ORDER BY ordinal_position;
        """),
        {"table_name": table_name}
    )

    columns = result.fetchall()

    session.close()

    return columns

def preview_table(table_name, limit=5):
    session = get_session()

    query = text(f"SELECT * FROM {table_name} LIMIT :limit")

    result = session.execute(query, {"limit": limit})

    rows = result.fetchall()

    session.close()

    return rows

def fetch_rows(table_name, limit=10, order_by=None):
    """Generic function to fetch rows from a given table"""
    session = get_session()

    try:
        query = f"SELECT * FROM {table_name}"

        if order_by:
            query += f" ORDER BY {order_by}"
        
        if limit:
            query += " LIMIT :limit"

        result = session.execute(text(query), {"limit": limit} if limit else {})
        return result.fetchall()
    finally:        
        session.close()

def fetch_by_column(table_name, column, value, limit=10):
    session = get_session()

    query = text(f"""
        SELECT *
        FROM {table_name}
        WHERE {column} = :value
        LIMIT :limit
    """)

    result = session.execute(query, {"value": value, "limit": limit})

    rows = result.fetchall()

    session.close()

    return rows

def count_rows(table_name):
    session = get_session()
    try:
        result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        count = result.scalar()
        return count
    finally:        session.close()

# TODO: add actual fetching functions depending on what we need (fetch_cctx(), fetch_events(), fetch_locks()...)

def fetch_bridge_cctxs(bridge_name, limit=10):
    """Fetch cross-chain transactions for a specific bridge"""
    return fetch_rows(f"{bridge_name}_cross_chain_transactions", limit=limit, order_by="id")