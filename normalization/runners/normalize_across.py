from db.database import get_session

#from db.repository.normalized_event_model import NormalizedEvent
from db.repository.normalized_event_repository import NormalizedEventRepository
from normalization.source_models.across import (
    AcrossFundsDeposited,
    AcrossFilledRelay,
    AcrossRelayerRefund,
)
from normalization.common.transaction_context import get_across_tx_context
from normalization.mappers.across.funds_deposited import map_funds_deposited
from normalization.mappers.across.filled_relay import map_filled_relay
from normalization.mappers.across.relayer_refund import map_relayer_refund

def normalize_table(session, model, raw_table: str, raw_pk_fn, mapper_fn):
    inserted = 0
    skipped = 0

    rows = session.query(model).all()

    for row in rows:
        raw_pk = raw_pk_fn(row)

        if NormalizedEventRepository.event_exists_in_session(session, raw_table, raw_pk):
            skipped += 1
            continue

        tx_ctx = get_across_tx_context(session, row.transaction_hash)
        event = mapper_fn(row, tx_ctx)
        session.add(event)
        inserted += 1

    session.commit()
    return inserted, skipped


def normalize_across():
    session = get_session()

    try:
        total_inserted = 0
        total_skipped = 0

        jobs = [
            (
                AcrossFundsDeposited,
                "across_funds_deposited",
                lambda row: str(row.deposit_id),
                map_funds_deposited,
            ),
            (
                AcrossFilledRelay,
                "across_filled_relay",
                lambda row: str(row.deposit_id),
                map_filled_relay,
            ),
            (
                AcrossRelayerRefund,
                "across_relayer_refund",
                lambda row: f"{row.transaction_hash}:{row.root_bundle_id}:{row.refund_address}",
                map_relayer_refund,
            ),
        ]

        for model, raw_table, raw_pk_fn, mapper_fn in jobs:
            inserted, skipped = normalize_table(
                session=session,
                model=model,
                raw_table=raw_table,
                raw_pk_fn=raw_pk_fn,
                mapper_fn=mapper_fn,
            )
            total_inserted += inserted
            total_skipped += skipped
            print(f"{raw_table}: inserted={inserted}, skipped={skipped}")

        print(
            f"Across normalization complete: inserted={total_inserted}, skipped={total_skipped}"
        )

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    normalize_across()