from sqlalchemy import func

from db.database import get_session
from db.repository.bridge_tables.ronin import RoninBlockchainTransactions
from db.repository.bridge_tables.polygon import PolygonBlockchainTransactions
from db.repository.bridge_tables.across import AcrossBlockchainTransactions
from db.repository.bridge_tables.ccip import CCIPBlockchainTransactions
from db.repository.bridge_tables.cctp import CCTPBlockchainTransactions
from db.repository.bridge_tables.debridge import DeBridgeBlockchainTransactions
from db.repository.bridge_tables.mayan import MayanBlockchainTransactions
from db.repository.bridge_tables.nomad import NomadBlockchainTransactions
from db.repository.bridge_tables.omnibridge import OmnibridgeBlockchainTransactions
from db.repository.bridge_tables.manual import (
    MeterIoBlockchainTransactions,
    QubitBlockchainTransactions,
    ChainSwapBlockchainTransactions,
    ThorchainBlockchainTransactions,
    WormholeBlockchainTransactions,
)
from db.repository.bridge_tables.pnetwork import (
    PNetworkBitcoinBlockchainTransactions,
    PNetworkBscBlockchainTransactions,
)


def _time_window_query(session, model, start_ts: int | None, end_ts: int | None):
    query = session.query(model)
    if start_ts is not None:
        query = query.filter(model.timestamp >= start_ts)
    if end_ts is not None:
        query = query.filter(model.timestamp <= end_ts)
    return query


def _get_all(model):
    session = get_session()
    try:
        return session.query(model).all()
    finally:
        session.close()


def _get_by_time_window(model, start_ts: int | None = None, end_ts: int | None = None):
    session = get_session()
    try:
        return _time_window_query(session, model, start_ts, end_ts).all()
    finally:
        session.close()


def _get_latest_timestamp(model, start_ts: int | None = None) -> int | None:
    session = get_session()
    try:
        query = session.query(func.max(model.timestamp))
        if start_ts is not None:
            query = query.filter(model.timestamp >= start_ts)
        return query.scalar()
    finally:
        session.close()


class RoninBlockchainTransactionRepository:
    def get_all() -> list[RoninBlockchainTransactions]:
        return _get_all(RoninBlockchainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[RoninBlockchainTransactions]:
        return _get_by_time_window(RoninBlockchainTransactions, start_ts, end_ts)

    def get_latest_timestamp(start_ts: int | None = None) -> int | None:
        return _get_latest_timestamp(RoninBlockchainTransactions, start_ts)

    def get_transactions_with_receipt_with_signatures(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[RoninBlockchainTransactions]:
        session = get_session()
        try:
            return (
                _time_window_query(
                    session,
                    RoninBlockchainTransactions,
                    start_ts,
                    end_ts,
                )
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
        return _get_all(PolygonBlockchainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[PolygonBlockchainTransactions]:
        return _get_by_time_window(PolygonBlockchainTransactions, start_ts, end_ts)

    def get_latest_timestamp(start_ts: int | None = None) -> int | None:
        return _get_latest_timestamp(PolygonBlockchainTransactions, start_ts)


class AcrossBlockchainTransactionRepository:
    def get_all() -> list[AcrossBlockchainTransactions]:
        return _get_all(AcrossBlockchainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[AcrossBlockchainTransactions]:
        return _get_by_time_window(AcrossBlockchainTransactions, start_ts, end_ts)

    def get_latest_timestamp(start_ts: int | None = None) -> int | None:
        return _get_latest_timestamp(AcrossBlockchainTransactions, start_ts)


class CCIPBlockchainTransactionRepository:
    def get_all() -> list[CCIPBlockchainTransactions]:
        return _get_all(CCIPBlockchainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[CCIPBlockchainTransactions]:
        return _get_by_time_window(CCIPBlockchainTransactions, start_ts, end_ts)

    def get_latest_timestamp(start_ts: int | None = None) -> int | None:
        return _get_latest_timestamp(CCIPBlockchainTransactions, start_ts)


class CCTPBlockchainTransactionRepository:
    def get_all() -> list[CCTPBlockchainTransactions]:
        return _get_all(CCTPBlockchainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[CCTPBlockchainTransactions]:
        return _get_by_time_window(CCTPBlockchainTransactions, start_ts, end_ts)

    def get_latest_timestamp(start_ts: int | None = None) -> int | None:
        return _get_latest_timestamp(CCTPBlockchainTransactions, start_ts)


class DeBridgeBlockchainTransactionRepository:
    def get_all() -> list[DeBridgeBlockchainTransactions]:
        return _get_all(DeBridgeBlockchainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[DeBridgeBlockchainTransactions]:
        return _get_by_time_window(DeBridgeBlockchainTransactions, start_ts, end_ts)

    def get_latest_timestamp(start_ts: int | None = None) -> int | None:
        return _get_latest_timestamp(DeBridgeBlockchainTransactions, start_ts)


class MayanBlockchainTransactionRepository:
    def get_all() -> list[MayanBlockchainTransactions]:
        return _get_all(MayanBlockchainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[MayanBlockchainTransactions]:
        return _get_by_time_window(MayanBlockchainTransactions, start_ts, end_ts)

    def get_latest_timestamp(start_ts: int | None = None) -> int | None:
        return _get_latest_timestamp(MayanBlockchainTransactions, start_ts)


class NomadBlockchainTransactionRepository:
    def get_all() -> list[NomadBlockchainTransactions]:
        return _get_all(NomadBlockchainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[NomadBlockchainTransactions]:
        return _get_by_time_window(NomadBlockchainTransactions, start_ts, end_ts)

    def get_latest_timestamp(start_ts: int | None = None) -> int | None:
        return _get_latest_timestamp(NomadBlockchainTransactions, start_ts)


class OmnibridgeBlockchainTransactionRepository:
    def get_all() -> list[OmnibridgeBlockchainTransactions]:
        return _get_all(OmnibridgeBlockchainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[OmnibridgeBlockchainTransactions]:
        return _get_by_time_window(OmnibridgeBlockchainTransactions, start_ts, end_ts)

    def get_latest_timestamp(start_ts: int | None = None) -> int | None:
        return _get_latest_timestamp(OmnibridgeBlockchainTransactions, start_ts)


class MeterIoBlockchainTransactionRepository:
    def get_all() -> list[MeterIoBlockchainTransactions]:
        return _get_all(MeterIoBlockchainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[MeterIoBlockchainTransactions]:
        return _get_by_time_window(MeterIoBlockchainTransactions, start_ts, end_ts)

    def get_latest_timestamp(start_ts: int | None = None) -> int | None:
        return _get_latest_timestamp(MeterIoBlockchainTransactions, start_ts)


class QubitBlockchainTransactionRepository:
    def get_all() -> list[QubitBlockchainTransactions]:
        return _get_all(QubitBlockchainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[QubitBlockchainTransactions]:
        return _get_by_time_window(QubitBlockchainTransactions, start_ts, end_ts)

    def get_latest_timestamp(start_ts: int | None = None) -> int | None:
        return _get_latest_timestamp(QubitBlockchainTransactions, start_ts)


class ChainSwapBlockchainTransactionRepository:
    def get_all() -> list[ChainSwapBlockchainTransactions]:
        return _get_all(ChainSwapBlockchainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[ChainSwapBlockchainTransactions]:
        return _get_by_time_window(ChainSwapBlockchainTransactions, start_ts, end_ts)

    def get_latest_timestamp(start_ts: int | None = None) -> int | None:
        return _get_latest_timestamp(ChainSwapBlockchainTransactions, start_ts)


class ThorchainBlockchainTransactionRepository:
    def get_all() -> list[ThorchainBlockchainTransactions]:
        return _get_all(ThorchainBlockchainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[ThorchainBlockchainTransactions]:
        return _get_by_time_window(ThorchainBlockchainTransactions, start_ts, end_ts)

    def get_latest_timestamp(start_ts: int | None = None) -> int | None:
        return _get_latest_timestamp(ThorchainBlockchainTransactions, start_ts)


class WormholeBlockchainTransactionRepository:
    def get_all() -> list[WormholeBlockchainTransactions]:
        return _get_all(WormholeBlockchainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[WormholeBlockchainTransactions]:
        return _get_by_time_window(WormholeBlockchainTransactions, start_ts, end_ts)

    def get_latest_timestamp(start_ts: int | None = None) -> int | None:
        return _get_latest_timestamp(WormholeBlockchainTransactions, start_ts)


class PNetworkBlockchainTransactionRepository:
    def get_all() -> list[
        PNetworkBscBlockchainTransactions | PNetworkBitcoinBlockchainTransactions
    ]:
        return [
            *_get_all(PNetworkBscBlockchainTransactions),
            *_get_all(PNetworkBitcoinBlockchainTransactions),
        ]

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[PNetworkBscBlockchainTransactions | PNetworkBitcoinBlockchainTransactions]:
        return [
            *_get_by_time_window(PNetworkBscBlockchainTransactions, start_ts, end_ts),
            *_get_by_time_window(PNetworkBitcoinBlockchainTransactions, start_ts, end_ts),
        ]

    def get_latest_timestamp(start_ts: int | None = None) -> int | None:
        timestamps = [
            timestamp
            for timestamp in (
                _get_latest_timestamp(PNetworkBscBlockchainTransactions, start_ts),
                _get_latest_timestamp(PNetworkBitcoinBlockchainTransactions, start_ts),
            )
            if timestamp is not None
        ]
        return max(timestamps) if timestamps else None
