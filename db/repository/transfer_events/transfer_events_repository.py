from db.database import get_session
from db.repository.bridge_tables.ccip import CCIPTransfer
from db.repository.bridge_tables.cctp import CCTPTransfer
from db.repository.bridge_tables.polygon import PolygonTransfer
from db.repository.bridge_tables.ronin import RoninTransfer


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
