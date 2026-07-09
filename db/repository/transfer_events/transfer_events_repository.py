from db.database import get_session
from db.repository.bridge_tables.ccip import CCIPTransfer
from db.repository.bridge_tables.cctp import CCTPTransfer
from db.repository.bridge_tables.polygon import PolygonTransfer
from db.repository.bridge_tables.ronin import RoninTransfer
from types import SimpleNamespace

from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError


class GenericTransferRepository:
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


class CCIPTransferRepository:
    def get_all() -> list[CCIPTransfer]:
        session = get_session()
        try:
            return session.query(CCIPTransfer).all()
        finally:
            session.close()

    def get_by_transaction_hash(transaction_hash: str) -> list[CCIPTransfer]:
        session = get_session()
        try:
            return (
                session.query(CCIPTransfer)
                .filter(CCIPTransfer.transaction_hash == transaction_hash)
                .order_by(CCIPTransfer.log_index)
                .all()
            )
        finally:
            session.close()


class CCTPTransferRepository:
    def get_all() -> list[CCTPTransfer]:
        session = get_session()
        try:
            return session.query(CCTPTransfer).all()
        finally:
            session.close()

    def get_by_transaction_hash(transaction_hash: str) -> list[CCTPTransfer]:
        session = get_session()
        try:
            return (
                session.query(CCTPTransfer)
                .filter(CCTPTransfer.transaction_hash == transaction_hash)
                .order_by(CCTPTransfer.log_index)
                .all()
            )
        finally:
            session.close()


class PolygonTransferRepository:
    def get_all() -> list[PolygonTransfer]:
        session = get_session()
        try:
            return session.query(PolygonTransfer).all()
        finally:
            session.close()

    def get_by_transaction_hash(transaction_hash: str) -> list[PolygonTransfer]:
        session = get_session()
        try:
            return (
                session.query(PolygonTransfer)
                .filter(PolygonTransfer.transaction_hash == transaction_hash)
                .order_by(PolygonTransfer.log_index)
                .all()
            )
        finally:
            session.close()


class RoninTransferRepository:
    def get_all() -> list[RoninTransfer]:
        session = get_session()
        try:
            return session.query(RoninTransfer).all()
        finally:
            session.close()

    def get_by_transaction_hash(transaction_hash: str) -> list[RoninTransfer]:
        session = get_session()
        try:
            return (
                session.query(RoninTransfer)
                .filter(RoninTransfer.transaction_hash == transaction_hash)
                .order_by(RoninTransfer.log_index)
                .all()
            )
        finally:
            session.close()
