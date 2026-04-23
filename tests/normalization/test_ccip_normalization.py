from sqlalchemy import text

from db.database import get_session
from db.repository.normalized_event.normalized_event_model import get_normalized_event_model
from normalization.runners.runner import run_normalization_for_bridge

from db.database import Base
from db.database import engine


def _count_raw_rows(session) -> int:
    send_requests = session.execute(text("SELECT COUNT(*) FROM ccip_send_requested")).scalar() or 0
    execution_state_changed = session.execute(text("SELECT COUNT(*) FROM ccip_execution_state_changed")).scalar() or 0

    return send_requests + execution_state_changed


def _count_normalized_rows(session) -> int:
    model = get_normalized_event_model("ccip")
    return (
        session.query(model)
        .filter(model.bridge == "ccip")
        .count()
    )


def test_ccip_normalization():
    Base.metadata.create_all(bind=engine)
    session = get_session()

    try:
        # sanity check: XChainDataGen raw tables must exist and contain data
        raw_count = _count_raw_rows(session)
        assert raw_count > 0, "No CCIP raw rows found in XChainDataGen tables"

        before = _count_normalized_rows(session)

        # run real normalization against the configured DB
        run_normalization_for_bridge("ccip")

        after = _count_normalized_rows(session)

        assert after >= before
        assert after > 0, "No normalized CCIP events were inserted"

        inserted_now = after - before

        # If table was already populated from previous runs, rerun should not break.
        # If this is the first run, we expect at least one new row.
        if before == 0:
            assert inserted_now > 0, "Expected new normalized events on first run"

        model = get_normalized_event_model("ccip")
        sample = session.query(model).filter(model.bridge == "ccip").first()

        assert sample is not None
        assert sample.raw_table in {
            "ccip_send_requested",
            "ccip_execution_state_changed",
        }
        assert sample.transaction_hash is not None
        assert sample.event_type is not None

    finally:
        session.close()
