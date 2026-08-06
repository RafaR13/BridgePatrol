from sqlalchemy import or_

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
    ChainSwapCrossChainTransactions,
    ThorchainCrossChainTransactions,
    WormholeCrossChainTransactions,
)
from db.repository.bridge_tables.pnetwork import PNetworkCrossChainTransactions


def _get_all(model):
    session = get_session()
    try:
        return session.query(model).all()
    finally:
        session.close()


def _time_window_filters(model, start_ts: int | None, end_ts: int | None):
    filters = []
    for field in ("src_timestamp", "dst_timestamp", "refund_timestamp"):
        if not hasattr(model, field):
            continue
        column = getattr(model, field)
        field_filters = []
        if start_ts is not None:
            field_filters.append(column >= start_ts)
        if end_ts is not None:
            field_filters.append(column <= end_ts)
        if not field_filters:
            continue
        query_filter = field_filters[0]
        for extra_filter in field_filters[1:]:
            query_filter = query_filter & extra_filter
        filters.append(query_filter)
    return filters


def _get_by_time_window(model, start_ts: int | None = None, end_ts: int | None = None):
    session = get_session()
    try:
        query = session.query(model)
        filters = _time_window_filters(model, start_ts, end_ts)
        if filters:
            query = query.filter(or_(*filters))
        return query.all()
    finally:
        session.close()


class RoninCrossChainTransactionRepository:
    def get_all() -> list[RoninCrossChainTransactions]:
        # This method should return all cross-chain transactions for the Ronin bridge
        return _get_all(RoninCrossChainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[RoninCrossChainTransactions]:
        return _get_by_time_window(RoninCrossChainTransactions, start_ts, end_ts)

class PolygonCrossChainTransactionRepository:
    def get_all() -> list[PolygonCrossChainTransactions]:
        return _get_all(PolygonCrossChainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[PolygonCrossChainTransactions]:
        return _get_by_time_window(PolygonCrossChainTransactions, start_ts, end_ts)

class AcrossCrossChainTransactionRepository:
    def get_all() -> list[AcrossCrossChainTransactions]:
        return _get_all(AcrossCrossChainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[AcrossCrossChainTransactions]:
        return _get_by_time_window(AcrossCrossChainTransactions, start_ts, end_ts)

class CCIPCrossChainTransactionRepository:
    def get_all() -> list[CCIPCrossChainTransactions]:
        return _get_all(CCIPCrossChainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[CCIPCrossChainTransactions]:
        return _get_by_time_window(CCIPCrossChainTransactions, start_ts, end_ts)

class CCTPCrossChainTransactionRepository:
    def get_all() -> list[CCTPCrossChainTransactions]:
        return _get_all(CCTPCrossChainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[CCTPCrossChainTransactions]:
        return _get_by_time_window(CCTPCrossChainTransactions, start_ts, end_ts)

class DeBridgeCrossChainTransactionRepository:
    def get_all() -> list[DeBridgeCrossChainTransactions]:
        return _get_all(DeBridgeCrossChainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[DeBridgeCrossChainTransactions]:
        return _get_by_time_window(DeBridgeCrossChainTransactions, start_ts, end_ts)


class MayanCrossChainTransactionRepository:
    def get_all() -> list[MayanCrossChainTransactions]:
        return _get_all(MayanCrossChainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[MayanCrossChainTransactions]:
        return _get_by_time_window(MayanCrossChainTransactions, start_ts, end_ts)


class OmnibridgeCrossChainTransactionRepository:
    def get_all() -> list[OmnibridgeCrossChainTransactions]:
        return _get_all(OmnibridgeCrossChainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[OmnibridgeCrossChainTransactions]:
        return _get_by_time_window(OmnibridgeCrossChainTransactions, start_ts, end_ts)


class MeterIoCrossChainTransactionRepository:
    def get_all() -> list[MeterIoCrossChainTransactions]:
        return _get_all(MeterIoCrossChainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[MeterIoCrossChainTransactions]:
        return _get_by_time_window(MeterIoCrossChainTransactions, start_ts, end_ts)


class QubitCrossChainTransactionRepository:
    def get_all() -> list[QubitCrossChainTransactions]:
        return _get_all(QubitCrossChainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[QubitCrossChainTransactions]:
        return _get_by_time_window(QubitCrossChainTransactions, start_ts, end_ts)


class ChainSwapCrossChainTransactionRepository:
    def get_all() -> list[ChainSwapCrossChainTransactions]:
        return _get_all(ChainSwapCrossChainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[ChainSwapCrossChainTransactions]:
        return _get_by_time_window(ChainSwapCrossChainTransactions, start_ts, end_ts)


class ThorchainCrossChainTransactionRepository:
    def get_all() -> list[ThorchainCrossChainTransactions]:
        return _get_all(ThorchainCrossChainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[ThorchainCrossChainTransactions]:
        return _get_by_time_window(ThorchainCrossChainTransactions, start_ts, end_ts)


class WormholeCrossChainTransactionRepository:
    def get_all() -> list[WormholeCrossChainTransactions]:
        return _get_all(WormholeCrossChainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[WormholeCrossChainTransactions]:
        return _get_by_time_window(WormholeCrossChainTransactions, start_ts, end_ts)


class PNetworkCrossChainTransactionRepository:
    def get_all() -> list[PNetworkCrossChainTransactions]:
        return _get_all(PNetworkCrossChainTransactions)

    def get_by_time_window(
        start_ts: int | None = None, end_ts: int | None = None
    ) -> list[PNetworkCrossChainTransactions]:
        return _get_by_time_window(PNetworkCrossChainTransactions, start_ts, end_ts)
