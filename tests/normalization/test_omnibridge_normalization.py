from sqlalchemy import text

from db.database import get_session
from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from normalization.runners.normalize_omnibridge import normalize_omnibridge

from db.database import Base
from db.database import engine


def _count_raw_rows(session) -> int:
    bridging_initiated = session.execute(text("SELECT COUNT(*) FROM omnibridge_tokens_bridging_initiated")).scalar() or 0
    tokens_bridged = session.execute(text("SELECT COUNT(*) FROM omnibridge_tokens_bridged")).scalar() or 0
    relayed_message = session.execute(text("SELECT COUNT(*) FROM omnibridge_relayed_message")).scalar() or 0
    signed_for_user_request = session.execute(text("SELECT COUNT(*) FROM omnibridge_signed_for_user_request")).scalar() or 0
    signed_for_affirmation = session.execute(text("SELECT COUNT(*) FROM omnibridge_signed_for_affirmation")).scalar() or 0
    user_request_for_signature = session.execute(text("SELECT COUNT(*) FROM omnibridge_user_request_for_signature")).scalar() or 0
    affirmation_completed = session.execute(text("SELECT COUNT(*) FROM omnibridge_affirmation_completed")).scalar() or 0
    user_request_for_affirmation = session.execute(text("SELECT COUNT(*) FROM omnibridge_user_request_for_affirmation")).scalar() or 0

    return bridging_initiated + tokens_bridged + relayed_message + signed_for_user_request + signed_for_affirmation + user_request_for_signature + affirmation_completed + user_request_for_affirmation


def _count_normalized_rows(session) -> int:
    return (
        session.query(NormalizedEvent)
        .filter(NormalizedEvent.bridge == "omnibridge")
        .count()
    )


def test_omnibridge_normalization():
    Base.metadata.create_all(bind=engine)
    session = get_session()

    try:
        # sanity check: XChainDataGen raw tables must exist and contain data
        raw_count = _count_raw_rows(session)
        assert raw_count > 0, "No Omnibridge raw rows found in XChainDataGen tables"

        before = _count_normalized_rows(session)

        # run real normalization against the configured DB
        normalize_omnibridge()

        after = _count_normalized_rows(session)

        assert after >= before
        assert after > 0, "No normalized Omnibridge events were inserted"

        inserted_now = after - before

        # If table was already populated from previous runs, rerun should not break.
        # If this is the first run, we expect at least one new row.
        if before == 0:
            assert inserted_now > 0, "Expected new normalized events on first run"

        sample = (
            session.query(NormalizedEvent)
            .filter(NormalizedEvent.bridge == "omnibridge")
            .first()
        )

        assert sample is not None
        assert sample.raw_table in {
            "omnibridge_tokens_bridging_initiated",
            "omnibridge_tokens_bridged",
            "omnibridge_relayed_message",
            "omnibridge_signed_for_user_request",
            "omnibridge_signed_for_affirmation",
            "omnibridge_user_request_for_signature",
            "omnibridge_affirmation_completed",
            "omnibridge_user_request_for_affirmation"
        }
        assert sample.transaction_hash is not None
        assert sample.event_type is not None

    finally:
        session.close()