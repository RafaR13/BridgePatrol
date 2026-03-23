from db.database import get_session

from db.repository.normalized_event.normalized_event_repository import NormalizedEventRepository
from normalization.source_models.across import (
    AcrossFundsDeposited,
    AcrossFilledRelay,
    AcrossRelayerRefund,
)
from normalization.common.transaction_context import get_tx_context
from normalization.mappers.across.mapper import map_funds_deposited, map_filled_relay, map_relayer_refund

def normalize_table(session, model, bridge: str, raw_table: str, raw_pk_fn, mapper_fn):
    inserted = 0
    skipped = 0

    rows = session.query(model).all()

    for row in rows:
        raw_pk = raw_pk_fn(row)

        if NormalizedEventRepository.event_exists_in_session(session, raw_table, raw_pk):
            skipped += 1
            continue

        tx_ctx = get_tx_context(session, row.transaction_hash, bridge)
        event = mapper_fn(row, tx_ctx)
        session.add(event)
        inserted += 1

    session.commit()
    return inserted, skipped


def normalize(bridge: str, jobs: list[tuple]):
    session = get_session()

    try:
        total_inserted = 0
        total_skipped = 0

        for model, raw_table, raw_pk_fn, mapper_fn in jobs:
            inserted, skipped = normalize_table(
                session=session,
                model=model,
                bridge=bridge,
                raw_table=raw_table,
                raw_pk_fn=raw_pk_fn,
                mapper_fn=mapper_fn,
            )
            total_inserted += inserted
            total_skipped += skipped
            print(f"{raw_table}: inserted={inserted}, skipped={skipped}")

        print(
            f"{bridge} normalization complete: inserted={total_inserted}, skipped={total_skipped}"
        )

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()