from sqlalchemy import func

from db.database import get_session

from .normalized_event_model import NormalizedEvent, get_normalized_event_model

class NormalizedEventRepository:

    def insert(event: NormalizedEvent):
        session = get_session()
        try:
            session.add(event)
            session.commit()
            session.refresh(event)
            return event
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def insert_many(events: list[NormalizedEvent]):
        session = get_session()
        try:
            session.add_all(events)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def event_exists(raw_table: str, raw_pk: str, bridge: str):
        model = get_normalized_event_model(bridge)
        session = get_session()
        try:
            return (
                session.query(model)
                .filter(
                    model.raw_table == raw_table,
                    model.raw_pk == raw_pk,
                )
                .first()
            )
        finally:
            session.close()

    def event_exists_in_session(session, raw_table: str, raw_pk: str, bridge: str) -> bool:
        model = get_normalized_event_model(bridge)
        return (
            session.query(model)
            .filter(
                model.raw_table == raw_table,
                model.raw_pk == raw_pk,
            )
            .first()
            is not None
        )

    def count(bridge: str):
        model = get_normalized_event_model(bridge)
        session = get_session()
        try:
            return session.query(func.count(model.id)).scalar()
        finally:
            session.close()

    def get_events_by_bridge(bridge: str) -> list[NormalizedEvent]:
        model = get_normalized_event_model(bridge)
        session = get_session()
        try:
            return (
                session.query(model)
                .filter(model.bridge == bridge)
                .all()
            )
        finally:
            session.close()

    def get_events_by_event_type(event_type: str, bridge_name: str) -> list[NormalizedEvent]:
        model = get_normalized_event_model(bridge_name)
        session = get_session()
        try:
            return (
                session.query(model)
                .filter(
                    model.event_type == event_type,
                    model.bridge == bridge_name,
                )
                .all()
            )
        finally:
            session.close()

    def get_latest_block_number_by_bridge(bridge_name: str) -> int | None:
        model = get_normalized_event_model(bridge_name)
        session = get_session()
        try:
            return (
                session.query(func.max(model.block_number))
                .filter(model.bridge == bridge_name)
                .scalar()
            )
        finally:
            session.close()

    # UNCOMMENT IF NEEDED IN THE FUTURE
    """
    def get_replay_candidates():
        session = get_session()
        try:
            return (
                session.query(NormalizedEvent)
                .filter(
                    or_(
                        NormalizedEvent.proof_hash.isnot(None),
                        NormalizedEvent.guid.isnot(None),
                        NormalizedEvent.message_id.isnot(None),
                        NormalizedEvent.nonce.isnot(None),
                    )
                )
                .all()
            )
        finally:
            session.close()
    
    def get_by_id(event_id: int):
            session = get_session()
            try:
                return session.get(NormalizedEvent, event_id)
            finally:
                session.close()

    def get_by_tx_hash(transaction_hash: str):
        session = get_session()
        try:
            return (
                session.query(NormalizedEvent)
                .filter(NormalizedEvent.transaction_hash == transaction_hash)
                .all()
            )
        finally:
            session.close()

    def get_by_event_type(event_type):
        session = get_session()
        try:
            return (
                session.query(NormalizedEvent)
                .filter(NormalizedEvent.event_type == event_type)
                .all()
            )
        finally:
            session.close()

    def get_by_correlation_id(correlation_id: str):
        session = get_session()
        try:
            return (
                session.query(NormalizedEvent)
                .filter(NormalizedEvent.correlation_id == correlation_id)
                .all()
            )
        finally:
            session.close()

    def get_by_message_id(message_id: str):
        session = get_session()
        try:
            return (
                session.query(NormalizedEvent)
                .filter(NormalizedEvent.message_id == message_id)
                .all()
            )
        finally:
            session.close()

    def get_by_guid(guid: str):
        session = get_session()
        try:
            return (
                session.query(NormalizedEvent)
                .filter(NormalizedEvent.guid == guid)
                .all()
            )
        finally:
            session.close()

    def get_by_nonce(nonce: str):
        session = get_session()
        try:
            return (
                session.query(NormalizedEvent)
                .filter(NormalizedEvent.nonce == nonce)
                .all()
            )
        finally:
            session.close()

    def get_by_proof_hash(proof_hash: str):
        session = get_session()
        try:
            return (
                session.query(NormalizedEvent)
                .filter(NormalizedEvent.proof_hash == proof_hash)
                .all()
            )
        finally:
            session.close()

            
"""
