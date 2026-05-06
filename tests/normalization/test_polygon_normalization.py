from sqlalchemy import text

from db.database import get_session
from db.repository.normalized_event.normalized_event_model import get_normalized_event_model
from normalization.runners.runner import run_normalization_for_bridge

from db.database import Base
from db.database import engine


def _count_raw_rows(session) -> int:

    locked_tokens = session.execute(text("SELECT COUNT(*) FROM polygon_locked_token")).scalar() or 0
    state_synced = session.execute(text("SELECT COUNT(*) FROM polygon_state_synced")).scalar() or 0
    state_committed = session.execute(text("SELECT COUNT(*) FROM polygon_state_committed")).scalar() or 0
    token_deposited = session.execute(text("SELECT COUNT(*) FROM polygon_token_deposited")).scalar() or 0
    pol_withdraw = session.execute(text("SELECT COUNT(*) FROM polygon_pol_withdraw")).scalar() or 0
    bridge_withdraw = session.execute(text("SELECT COUNT(*) FROM polygon_bridge_withdraw")).scalar() or 0
    exited_tokens = session.execute(text("SELECT COUNT(*) FROM polygon_exited_token")).scalar() or 0
    child_token_burns = (
        session.execute(text("SELECT COUNT(*) FROM polygon_child_token_burn")).scalar() or 0
    )

    return (
        locked_tokens
        + state_synced
        + state_committed
        + token_deposited
        + pol_withdraw
        + bridge_withdraw
        + exited_tokens
        + child_token_burns
    )


def _count_normalized_rows(session) -> int:
    model = get_normalized_event_model("polygon")
    return (
        session.query(model)
        .filter(model.bridge == "polygon")
        .count()
    )


def test_polygon_normalization():
    Base.metadata.create_all(bind=engine)
    session = get_session()

    try:
        # sanity check: XChainDataGen raw tables must exist and contain data
        raw_count = _count_raw_rows(session)
        assert raw_count > 0, "No Polygon raw rows found in XChainDataGen tables"

        before = _count_normalized_rows(session)

        # run real normalization against the configured DB
        run_normalization_for_bridge("polygon")

        after = _count_normalized_rows(session)

        assert after >= before
        assert after > 0, "No normalized Polygon events were inserted"

        inserted_now = after - before

        # If table was already populated from previous runs, rerun should not break.
        # If this is the first run, we expect at least one new row.
        if before == 0:
            assert inserted_now > 0, "Expected new normalized events on first run"

        model = get_normalized_event_model("polygon")
        sample = session.query(model).filter(model.bridge == "polygon").first()

        assert sample is not None
        assert sample.raw_table in {
            "polygon_locked_token",
            "polygon_state_synced",
            "polygon_state_committed",
            "polygon_token_deposited",
            "polygon_pol_withdraw",
            "polygon_bridge_withdraw",
            "polygon_exited_token",
            "polygon_child_token_burn",
        }
        assert sample.transaction_hash is not None
        assert sample.event_type is not None

    finally:
        session.close()
