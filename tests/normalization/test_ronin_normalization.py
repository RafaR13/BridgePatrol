from sqlalchemy import text

from db.database import get_session
from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from normalization.runners.normalize_ronin import normalize_ronin

from db.database import Base
from db.database import engine


def _count_raw_rows(session) -> int:
    deposit_requests = session.execute(text("SELECT COUNT(*) FROM ronin_deposit_requested")).scalar() or 0
    token_deposits = session.execute(text("SELECT COUNT(*) FROM ronin_token_deposited")).scalar() or 0
    withdrawal_requests = session.execute(text("SELECT COUNT(*) FROM ronin_withdrawal_requested")).scalar() or 0
    withdrew_tokens = session.execute(text("SELECT COUNT(*) FROM ronin_token_withdrew")).scalar() or 0

    return deposit_requests + token_deposits + withdrawal_requests + withdrew_tokens


def _count_normalized_rows(session) -> int:
    return (
        session.query(NormalizedEvent)
        .filter(NormalizedEvent.bridge == "ronin")
        .count()
    )


def test_ronin_normalization():
    Base.metadata.create_all(bind=engine)
    session = get_session()

    try:
        # sanity check: XChainDataGen raw tables must exist and contain data
        raw_count = _count_raw_rows(session)
        assert raw_count > 0, "No Ronin raw rows found in XChainDataGen tables"

        before = _count_normalized_rows(session)

        # run real normalization against the configured DB
        normalize_ronin()

        after = _count_normalized_rows(session)

        assert after >= before
        assert after > 0, "No normalized Ronin events were inserted"

        inserted_now = after - before

        # If table was already populated from previous runs, rerun should not break.
        # If this is the first run, we expect at least one new row.
        if before == 0:
            assert inserted_now > 0, "Expected new normalized events on first run"

        sample = (
            session.query(NormalizedEvent)
            .filter(NormalizedEvent.bridge == "ronin")
            .first()
        )

        assert sample is not None
        assert sample.raw_table in {
            "ronin_deposit_requested",
            "ronin_token_deposited",
            "ronin_withdrawal_requested",
            "ronin_token_withdrew",
        }
        assert sample.transaction_hash is not None
        assert sample.event_type is not None

    finally:
        session.close()