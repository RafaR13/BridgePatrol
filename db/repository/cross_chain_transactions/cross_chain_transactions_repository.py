from db.database import get_session
from db.repository.bridge_tables.ronin import RoninCrossChainTransactions
from db.repository.bridge_tables.polygon import PolygonCrossChainTransactions
from db.repository.bridge_tables.across import AcrossCrossChainTransactions
from db.repository.bridge_tables.ccip import CCIPCrossChainTransactions
from db.repository.bridge_tables.cctp import CCTPCrossChainTransactions
from db.repository.bridge_tables.debridge import DeBridgeCrossChainTransactions
from db.repository.bridge_tables.mayan import MayanCrossChainTransactions
from db.repository.bridge_tables.omnibridge import OmnibridgeCrossChainTransactions
from db.repository.bridge_tables.manual import (
    MeterIoCrossChainTransactions,
    QubitCrossChainTransactions,
    ThorchainCrossChainTransactions,
    WormholeCrossChainTransactions,
)
from db.repository.bridge_tables.pnetwork import PNetworkCrossChainTransactions

class RoninCrossChainTransactionRepository:
    def get_all() -> list[RoninCrossChainTransactions]:
        # This method should return all cross-chain transactions for the Ronin bridge
        session = get_session()
        try:
            return (
                session.query(RoninCrossChainTransactions)
                .all()
            )
        finally:
            session.close()

class PolygonCrossChainTransactionRepository:
    def get_all() -> list[PolygonCrossChainTransactions]:
        session = get_session()
        try:
            return (
                session.query(PolygonCrossChainTransactions)
                .all()
            )
        finally:
            session.close()

class AcrossCrossChainTransactionRepository:
    def get_all() -> list[AcrossCrossChainTransactions]:
        session = get_session()
        try:
            return (
                session.query(AcrossCrossChainTransactions)
                .all()
            )
        finally:
            session.close()

class CCIPCrossChainTransactionRepository:
    def get_all() -> list[CCIPCrossChainTransactions]:
        session = get_session()
        try:
            return (
                session.query(CCIPCrossChainTransactions)
                .all()
            )
        finally:
            session.close()

class CCTPCrossChainTransactionRepository:
    def get_all() -> list[CCTPCrossChainTransactions]:
        session = get_session()
        try:
            return (
                session.query(CCTPCrossChainTransactions)
                .all()
            )
        finally:
            session.close()

class DeBridgeCrossChainTransactionRepository:
    def get_all() -> list[DeBridgeCrossChainTransactions]:
        session = get_session()
        try:
            return (
                session.query(DeBridgeCrossChainTransactions)
                .all()
            )
        finally:
            session.close()


class MayanCrossChainTransactionRepository:
    def get_all() -> list[MayanCrossChainTransactions]:
        session = get_session()
        try:
            return (
                session.query(MayanCrossChainTransactions)
                .all()
            )
        finally:
            session.close()


class OmnibridgeCrossChainTransactionRepository:
    def get_all() -> list[OmnibridgeCrossChainTransactions]:
        session = get_session()
        try:
            return (
                session.query(OmnibridgeCrossChainTransactions)
                .all()
            )
        finally:
            session.close()


class MeterIoCrossChainTransactionRepository:
    def get_all() -> list[MeterIoCrossChainTransactions]:
        session = get_session()
        try:
            return session.query(MeterIoCrossChainTransactions).all()
        finally:
            session.close()


class QubitCrossChainTransactionRepository:
    def get_all() -> list[QubitCrossChainTransactions]:
        session = get_session()
        try:
            return session.query(QubitCrossChainTransactions).all()
        finally:
            session.close()


class ThorchainCrossChainTransactionRepository:
    def get_all() -> list[ThorchainCrossChainTransactions]:
        session = get_session()
        try:
            return session.query(ThorchainCrossChainTransactions).all()
        finally:
            session.close()


class WormholeCrossChainTransactionRepository:
    def get_all() -> list[WormholeCrossChainTransactions]:
        session = get_session()
        try:
            return session.query(WormholeCrossChainTransactions).all()
        finally:
            session.close()


class PNetworkCrossChainTransactionRepository:
    def get_all() -> list[PNetworkCrossChainTransactions]:
        session = get_session()
        try:
            return session.query(PNetworkCrossChainTransactions).all()
        finally:
            session.close()
