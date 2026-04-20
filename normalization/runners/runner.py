from db.database import get_session

from db.repository.normalized_event.normalized_event_repository import NormalizedEventRepository
from normalization.common.transaction_context import get_tx_context
from .jobs import NormalizationJob, get_jobs_for_bridge


def normalize_table(session, bridge: str, job: NormalizationJob):
    inserted = 0
    skipped = 0

    rows = session.query(job.model).all()

    for row in rows:
        raw_pk = job.raw_pk_fn(row)

        if NormalizedEventRepository.event_exists_in_session(session, job.raw_table, raw_pk):
            skipped += 1
            continue

        tx_ctx = get_tx_context(session, row.transaction_hash, bridge)
        event = job.mapper_fn(row, tx_ctx)
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
