from sqlalchemy import text

from db.database import get_session
from db.repository.normalized_event.normalized_event_model import get_normalized_event_model
from normalization.runners.runner import run_normalization_for_bridge

from db.database import Base
from db.database import engine


def _count_raw_rows(session) -> int:
    deposit_for_burn = session.execute(text("SELECT COUNT(*) FROM cctp_deposit_for_burn")).scalar() or 0
    message_received = session.execute(text("SELECT COUNT(*) FROM cctp_message_received")).scalar() or 0

    return deposit_for_burn + message_received


def _count_normalized_rows(session) -> int:
    model = get_normalized_event_model("cctp")
    return (
        session.query(model)
        .filter(model.bridge == "cctp")
        .count()
    )


def test_cctp_normalization():
    Base.metadata.create_all(bind=engine)
    session = get_session()

    try:
        # sanity check: XChainDataGen raw tables must exist and contain data
        raw_count = _count_raw_rows(session)
        assert raw_count > 0, "No CCTP raw rows found in XChainDataGen tables"

        before = _count_normalized_rows(session)

        # run real normalization against the configured DB
        run_normalization_for_bridge("cctp")

        after = _count_normalized_rows(session)

        assert after >= before
        assert after > 0, "No normalized CCTP events were inserted"

        inserted_now = after - before

        # If table was already populated from previous runs, rerun should not break.
        # If this is the first run, we expect at least one new row.
        if before == 0:
            assert inserted_now > 0, "Expected new normalized events on first run"

        model = get_normalized_event_model("cctp")
        sample = session.query(model).filter(model.bridge == "cctp").first()

        assert sample is not None
        assert sample.raw_table in {
            "cctp_deposit_for_burn",
            "cctp_message_received",
        }
        assert sample.transaction_hash is not None
        assert sample.event_type is not None

    finally:
        session.close()
