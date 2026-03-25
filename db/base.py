from sqlalchemy import text
from .database import get_session


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

def clear_table(table_name, restart_identity=True, cascade=True):
    """
    Removes all rows from a table

    Args:
        table_name (str): Table name
        restart_identity (bool): restart sequences/ids.
        cascade (bool): Aplica CASCADE no TRUNCATE.

    Raises:
        ValueError: if table doesn't exist
    """
    session = get_session()

    try:
        valid_tables = set(list_tables())
        if table_name not in valid_tables:
            raise ValueError(f"Table '{table_name}' does not exist.")

        query = f"TRUNCATE TABLE {table_name}"

        if restart_identity:
            query += " RESTART IDENTITY"

        if cascade:
            query += " CASCADE"

        session.execute(text(query))
        session.commit()

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def clear_tables(table_names, restart_identity=True, cascade=True):
    """
    Remove todas as rows de várias tabelas.

    Args:
        table_names (list[str]): Lista de nomes de tabelas.
        restart_identity (bool): Reinicia sequences/ids.
        cascade (bool): Aplica CASCADE no TRUNCATE.

    Raises:
        ValueError: Se alguma tabela não existir.
    """
    if not table_names:
        return

    session = get_session()

    try:
        valid_tables = set(list_tables())
        invalid_tables = [table for table in table_names if table not in valid_tables]
        if invalid_tables:
            raise ValueError(f"Invalid tables: {', '.join(invalid_tables)}")

        tables_sql = ", ".join(table_names)
        query = f"TRUNCATE TABLE {tables_sql}"

        if restart_identity:
            query += " RESTART IDENTITY"

        if cascade:
            query += " CASCADE"

        session.execute(text(query))
        session.commit()

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def get_bridge_tables(bridge_name):
    """
    Devolve todas as tabelas cujo nome contém o nome da bridge.

    Exemplo:
        get_bridge_tables("cctp") -> ['cctp_deposit_for_burn', ...]
    """
    all_tables = list_tables()
    bridge_name = bridge_name.lower()
    return [table for table in all_tables if bridge_name in table.lower()]

def clear_bridge_tables(bridge_name, restart_identity=True, cascade=True):
    """
    Esvazia todas as tabelas associadas a uma bridge.
    """
    bridge_tables = get_bridge_tables(bridge_name)

    if not bridge_tables:
        raise ValueError(f"No tables found for bridge '{bridge_name}'.")

    clear_tables(
        bridge_tables,
        restart_identity=restart_identity,
        cascade=cascade,
    )

def clear_all_tables(restart_identity=True, cascade=True):
    """
    Esvazia todas as tabelas do schema public.
    """
    all_tables = list_tables()
    clear_tables(
        all_tables,
        restart_identity=restart_identity,
        cascade=cascade,
    )

"""def preview_table(table_name, limit=5):
    session = get_session()

    query = text(f"SELECT * FROM {table_name} LIMIT :limit")

    result = session.execute(query, {"limit": limit})

    rows = result.fetchall()

    session.close()

    return rows

def fetch_rows(table_name, limit=10, order_by=None):
    Generic function to fetch rows from a given table
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

    query = text(f
        SELECT *
        FROM {table_name}
        WHERE {column} = :value
        LIMIT :limit
    )

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
    finally:        session.close()"""
