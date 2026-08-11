from sqlalchemy import text

from db.database import Base
from db.database import engine
from db.database import get_session
from db.repository.normalized_event.normalized_event_model import get_normalized_event_model
from normalization.runners.runner import run_normalization_for_bridge


NOMAD_RAW_TABLES = {
    "nomad_router_send",
    "nomad_router_receive",
    "nomad_eth_helper_send",
    "nomad_replica_process",
    "nomad_home_dispatch",
}


def _count_raw_nomad_rows(session) -> int:
    return sum(
        session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar() or 0
        for table in NOMAD_RAW_TABLES
    )


def _count_normalized_nomad_rows(session) -> int:
    model = get_normalized_event_model("nomad")
    return session.query(model).filter(model.bridge == "nomad").count()


def test_nomad_normalization():
    Base.metadata.create_all(bind=engine)
    session = get_session()

    try:
        raw_count = _count_raw_nomad_rows(session)
        assert raw_count > 0, "No Nomad raw rows found in XChainDataGen tables"

        before = _count_normalized_nomad_rows(session)

        run_normalization_for_bridge("nomad")

        after = _count_normalized_nomad_rows(session)

        assert after >= before
        assert after > 0, "No normalized Nomad events were inserted"

        inserted_now = after - before

        if before == 0:
            assert inserted_now > 0, "Expected new normalized events on first run"

        model = get_normalized_event_model("nomad")
        sample = session.query(model).filter(model.bridge == "nomad").first()

        assert sample is not None
        assert sample.raw_table in NOMAD_RAW_TABLES
        assert sample.transaction_hash is not None
        assert sample.event_type is not None

    finally:
        session.close()
