from db.database import get_session
from sqlalchemy import or_

from db.repository.normalized_event.normalized_event_model import (
    cast_normalized_event_for_bridge,
    get_normalized_event_model,
)
from db.repository.bridge_tables.across import AcrossCrossChainTransactions
from db.repository.bridge_tables.ccip import CCIPCrossChainTransactions
from db.repository.bridge_tables.cctp import CCTPCrossChainTransactions
from db.repository.bridge_tables.debridge import DeBridgeCrossChainTransactions
from db.repository.bridge_tables.mayan import MayanCrossChainTransactions
from db.repository.bridge_tables.omnibridge import OmnibridgeCrossChainTransactions
from db.repository.bridge_tables.polygon import PolygonCrossChainTransactions
from db.repository.bridge_tables.ronin import RoninCrossChainTransactions
from normalization.common.transaction_context import get_tx_context
from .jobs import NormalizationJob, get_jobs_for_bridge


CCTX_MODELS = {
    "across": (AcrossCrossChainTransactions, "intent_id"),
    "ccip": (CCIPCrossChainTransactions, "id"),
    "cctp": (CCTPCrossChainTransactions, "id"),
    "debridge": (DeBridgeCrossChainTransactions, "intent_id"),
    "mayan": (MayanCrossChainTransactions, "intent_id"),
    "omnibridge": (OmnibridgeCrossChainTransactions, "id"),
    "polygon": (PolygonCrossChainTransactions, "id"),
    "ronin": (RoninCrossChainTransactions, "id"),
}


def get_cctx_id(session, bridge: str, transaction_hash: str) -> str | None:
    model, id_field = CCTX_MODELS[bridge]

    filters = [
        getattr(model, field) == transaction_hash
        for field in (
            "src_transaction_hash",
            "dst_transaction_hash",
            "refund_transaction_hash",
        )
        if hasattr(model, field)
    ]

    if not filters:
        return None

    cctx = session.query(model).filter(or_(*filters)).first()

    if cctx is None:
        return None

    cctx_id = getattr(cctx, id_field, None)
    return str(cctx_id) if cctx_id is not None else None


def normalize_table(session, bridge: str, job: NormalizationJob):
    inserted = 0
    skipped = 0

    rows = session.query(job.model).all()

    for row in rows:
        raw_pk = job.raw_pk_fn(row)

        model = get_normalized_event_model(bridge)
        existing_event = (
            session.query(model)
            .filter(
                model.raw_table == job.raw_table,
                model.raw_pk == raw_pk,
            )
            .first()
        )
        cctx_id = get_cctx_id(session, bridge, row.transaction_hash)

        if existing_event is not None:
            if existing_event.cctx_id is None and cctx_id is not None:
                existing_event.cctx_id = cctx_id
            skipped += 1
            continue

        tx_ctx = get_tx_context(session, row.transaction_hash, bridge)
        event = cast_normalized_event_for_bridge(job.mapper_fn(row, tx_ctx, cctx_id), bridge)
        session.add(event)
        inserted += 1

    session.commit()
    return inserted, skipped


def normalize(bridge: str, jobs: tuple[NormalizationJob, ...]):
    session = get_session()

    try:
        total_inserted = 0
        total_skipped = 0

        for job in jobs:
            inserted, skipped = normalize_table(
                session=session,
                bridge=bridge,
                job=job,
            )
            total_inserted += inserted
            total_skipped += skipped
            print(f"{job.raw_table}: inserted={inserted}, skipped={skipped}")

        print(
            f"{bridge} normalization complete: inserted={total_inserted}, skipped={total_skipped}"
        )

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def normalize_bridge(bridge: str):
    jobs = get_jobs_for_bridge(bridge)
    normalize(bridge=bridge, jobs=jobs)


def run_normalization_for_bridge(bridge: str):
    normalize_bridge(bridge)
