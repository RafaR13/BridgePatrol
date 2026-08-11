from db.database import get_session
from types import SimpleNamespace

from sqlalchemy import bindparam, text
from sqlalchemy.exc import OperationalError, ProgrammingError


class TransferRepository:
    def __init__(self, table_name: str):
        self.table_name = table_name

    def get_all(self) -> list[SimpleNamespace]:
        session = get_session()
        try:
            rows = session.execute(
                text(
                    f"""
                    SELECT
                        blockchain,
                        transaction_hash,
                        block_number,
                        log_index,
                        token_address,
                        from_address,
                        to_address,
                        amount
                    FROM {self.table_name}
                    """
                )
            ).mappings()
            return [SimpleNamespace(**row) for row in rows]
        except (OperationalError, ProgrammingError):
            return []
        finally:
            session.close()

    def get_by_transaction_hash(self, transaction_hash: str) -> list[SimpleNamespace]:
        session = get_session()
        try:
            rows = session.execute(
                text(
                    f"""
                    SELECT
                        blockchain,
                        transaction_hash,
                        block_number,
                        log_index,
                        token_address,
                        from_address,
                        to_address,
                        amount
                    FROM {self.table_name}
                    WHERE transaction_hash = :transaction_hash
                    ORDER BY log_index
                    """
                ),
                {"transaction_hash": transaction_hash},
            ).mappings()
            return [SimpleNamespace(**row) for row in rows]
        except (OperationalError, ProgrammingError):
            return []
        finally:
            session.close()

    def get_by_transaction_hashes(
        self, transaction_hashes: set[str] | list[str] | tuple[str, ...]
    ) -> list[SimpleNamespace]:
        tx_hashes = [tx_hash for tx_hash in transaction_hashes if tx_hash is not None]
        if not tx_hashes:
            return []

        session = get_session()
        try:
            stmt = text(
                f"""
                SELECT
                    blockchain,
                    transaction_hash,
                    block_number,
                    log_index,
                    token_address,
                    from_address,
                    to_address,
                    amount
                FROM {self.table_name}
                WHERE transaction_hash IN :transaction_hashes
                ORDER BY transaction_hash, log_index
                """
            ).bindparams(bindparam("transaction_hashes", expanding=True))
            rows = session.execute(stmt, {"transaction_hashes": tx_hashes}).mappings()
            return [SimpleNamespace(**row) for row in rows]
        except (OperationalError, ProgrammingError):
            return []
        finally:
            session.close()
