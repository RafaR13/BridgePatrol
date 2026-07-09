from sqlalchemy import text

from db.database import get_session
from db.repository.normalized_event.normalized_event_model import get_normalized_event_model
from normalization.runners.runner import run_normalization_for_bridge

from db.database import Base
from db.database import engine


def _count_raw_across_rows(session) -> int:
    funds = session.execute(text("SELECT COUNT(*) FROM across_funds_deposited")).scalar() or 0
    fills = session.execute(text("SELECT COUNT(*) FROM across_filled_relay")).scalar() or 0
    refunds = session.execute(text("SELECT COUNT(*) FROM across_relayer_refund")).scalar() or 0
    return funds + fills + refunds


def _count_normalized_across_rows(session) -> int:
    model = get_normalized_event_model("across")
    return (
        session.query(model)
        .filter(model.bridge == "across")
        .count()
    )


def test_across_normalization():
    Base.metadata.create_all(bind=engine)
    session = get_session()

    try:
        # sanity check: XChainDataGen raw tables must exist and contain data
        raw_count = _count_raw_across_rows(session)
        assert raw_count > 0, "No Across raw rows found in XChainDataGen tables"

        before = _count_normalized_across_rows(session)

        # run real normalization against the configured DB
        run_normalization_for_bridge("across")

        after = _count_normalized_across_rows(session)

        assert after >= before
        assert after > 0, "No normalized Across events were inserted"

        inserted_now = after - before

        # If table was already populated from previous runs, rerun should not break.
        # If this is the first run, we expect at least one new row.
        if before == 0:
            assert inserted_now > 0, "Expected new normalized events on first run"

        model = get_normalized_event_model("across")
        sample = session.query(model).filter(model.bridge == "across").first()

        assert sample is not None
        assert sample.raw_table in {
            "across_funds_deposited",
            "across_filled_relay",
            "across_relayer_refund",
        }
        assert sample.transaction_hash is not None
        assert sample.event_type is not None

    finally:
        session.close()
