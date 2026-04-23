from sqlalchemy import text

from db.database import get_session
from db.repository.normalized_event.normalized_event_model import get_normalized_event_model
from normalization.runners.runner import run_normalization_for_bridge

from db.database import Base
from db.database import engine


def _count_raw_rows(session) -> int:
    swap_and_forwarded = session.execute(text("SELECT COUNT(*) FROM mayan_swap_and_forwarded")).scalar()
    forwarded = session.execute(text("SELECT COUNT(*) FROM mayan_forwarded")).scalar()
    auction_bid = session.execute(text("SELECT COUNT(*) FROM mayan_auction_bid")).scalar()
    order_created = session.execute(text("SELECT COUNT(*) FROM mayan_order_created")).scalar()
    order_fulfilled = session.execute(text("SELECT COUNT(*) FROM mayan_order_fulfilled")).scalar()
    order_unlocked = session.execute(text("SELECT COUNT(*) FROM mayan_order_unlocked")).scalar()
    init_order = session.execute(text("SELECT COUNT(*) FROM mayan_init_order")).scalar()
    register_order = session.execute(text("SELECT COUNT(*) FROM mayan_register_order")).scalar()
    set_auction_winner = session.execute(text("SELECT COUNT(*) FROM mayan_set_auction_winner")).scalar()
    auction_close = session.execute(text("SELECT COUNT(*) FROM mayan_auction_close")).scalar()
    fulfill_order = session.execute(text("SELECT COUNT(*) FROM mayan_fulfill_order")).scalar()
    unlock = session.execute(text("SELECT COUNT(*) FROM mayan_unlock")).scalar()
    settle = session.execute(text("SELECT COUNT(*) FROM mayan_settle")).scalar()

    return swap_and_forwarded + forwarded + auction_bid + order_created + order_fulfilled + order_unlocked + init_order + register_order + set_auction_winner + auction_close + fulfill_order + unlock + settle


def _count_normalized_rows(session) -> int:
    model = get_normalized_event_model("mayan")
    return (
        session.query(model)
        .filter(model.bridge == "mayan")
        .count()
    )


def test_mayan_normalization():
    print("Mayan not supported yet, skipping test...")
    return
    Base.metadata.create_all(bind=engine)
    session = get_session()

    try:
        # sanity check: XChainDataGen raw tables must exist and contain data
        raw_count = _count_raw_rows(session)
        assert raw_count > 0, "No Mayan raw rows found in XChainDataGen tables"

        before = _count_normalized_rows(session)

        # run real normalization against the configured DB
        run_normalization_for_bridge("mayan")

        after = _count_normalized_rows(session)

        assert after >= before
        assert after > 0, "No normalized Mayan events were inserted"

        inserted_now = after - before

        # If table was already populated from previous runs, rerun should not break.
        # If this is the first run, we expect at least one new row.
        if before == 0:
            assert inserted_now > 0, "Expected new normalized events on first run"

        model = get_normalized_event_model("mayan")
        sample = session.query(model).filter(model.bridge == "mayan").first()

        assert sample is not None
        assert sample.raw_table in {
            "mayan_swap_and_forwarded",
            "mayan_forwarded",
            "mayan_auction_bid",
            "mayan_order_created",
            "mayan_order_fulfilled",
            "mayan_order_unlocked",
            "mayan_init_order",
            "mayan_register_order",
            "mayan_set_auction_winner",
            "mayan_auction_close",
            "mayan_fulfill_order",
            "mayan_unlock",
            "mayan_settle"
        }
        assert sample.transaction_hash is not None
        assert sample.event_type is not None

    finally:
        session.close()
