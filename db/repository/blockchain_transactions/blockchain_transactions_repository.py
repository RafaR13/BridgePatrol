from db.database import get_session
from db.repository.bridge_tables.ronin import RoninBlockchainTransactions
from db.repository.bridge_tables.polygon import PolygonBlockchainTransactions
from db.repository.bridge_tables.across import AcrossBlockchainTransactions
from db.repository.bridge_tables.ccip import CCIPBlockchainTransactions
from db.repository.bridge_tables.cctp import CCTPBlockchainTransactions
from db.repository.bridge_tables.debridge import DeBridgeBlockchainTransactions
from db.repository.bridge_tables.mayan import MayanBlockchainTransactions
from db.repository.bridge_tables.omnibridge import OmnibridgeBlockchainTransactions


class RoninBlockchainTransactionRepository:
    def get_all() -> list[RoninBlockchainTransactions]:
        session = get_session()
        try:
            return session.query(RoninBlockchainTransactions).all()
        finally:
            session.close()

    def get_transactions_with_receipt_with_signatures() -> list[RoninBlockchainTransactions]:
        session = get_session()
        try:
            return (
                session.query(RoninBlockchainTransactions)
                # .filter(
                #    RoninBlockchainTransactions.decoded_input_data["_receipt"].isnot(None),
                #    RoninBlockchainTransactions.decoded_input_data["_signatures"].isnot(None),
                # )
                .all()
            )
        finally:
            session.close()


class PolygonBlockchainTransactionRepository:
    def get_all() -> list[PolygonBlockchainTransactions]:
        session = get_session()
        try:
            return session.query(PolygonBlockchainTransactions).all()
        finally:
            session.close()


class AcrossBlockchainTransactionRepository:
    def get_all() -> list[AcrossBlockchainTransactions]:
        session = get_session()
        try:
            return session.query(AcrossBlockchainTransactions).all()
        finally:
            session.close()


class CCIPBlockchainTransactionRepository:
    def get_all() -> list[CCIPBlockchainTransactions]:
        session = get_session()
        try:
            return session.query(CCIPBlockchainTransactions).all()
        finally:
            session.close()


class CCTPBlockchainTransactionRepository:
    def get_all() -> list[CCTPBlockchainTransactions]:
        session = get_session()
        try:
            return session.query(CCTPBlockchainTransactions).all()
        finally:
            session.close()


class DeBridgeBlockchainTransactionRepository:
    def get_all() -> list[DeBridgeBlockchainTransactions]:
        session = get_session()
        try:
            return session.query(DeBridgeBlockchainTransactions).all()
        finally:
            session.close()


class MayanBlockchainTransactionRepository:
    def get_all() -> list[MayanBlockchainTransactions]:
        session = get_session()
        try:
            return session.query(MayanBlockchainTransactions).all()
        finally:
            session.close()


class OmnibridgeBlockchainTransactionRepository:
    def get_all() -> list[OmnibridgeBlockchainTransactions]:
        session = get_session()
        try:
            return session.query(OmnibridgeBlockchainTransactions).all()
        finally:
            session.close()
