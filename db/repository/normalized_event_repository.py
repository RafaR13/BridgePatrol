from sqlalchemy import Index, func, or_

from db.database import get_session

from .normalized_event_model import NormalizedEvent

class NormalizedEventRepository:
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

    def event_exists(raw_table: str, raw_pk: str):
        session = get_session()
        try:
            return (
                session.query(NormalizedEvent)
                .filter(
                    NormalizedEvent.raw_table == raw_table,
                    NormalizedEvent.raw_pk == raw_pk,
                )
                .first()
            )
        finally:
            session.close()

    def event_exists_in_session(session, raw_table: str, raw_pk: str) -> bool:
        return (
            session.query(NormalizedEvent)
            .filter(
                NormalizedEvent.raw_table == raw_table,
                NormalizedEvent.raw_pk == raw_pk,
            )
            .first()
            is not None
        )

    def count():
        session = get_session()
        try:
            return session.query(func.count(NormalizedEvent.id)).scalar()
        finally:
            session.close()

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

#Index("ix_normalized_events_tx_hash", NormalizedEvent.transaction_hash)
#Index("ix_normalized_events_event_type", NormalizedEvent.event_type)
#Index("ix_normalized_events_bridge", NormalizedEvent.bridge)
#Index("ix_normalized_events_blockchain", NormalizedEvent.blockchain)
#Index("ix_normalized_events_corr_id", NormalizedEvent.correlation_id)
#Index("ix_normalized_events_message_id", NormalizedEvent.message_id)
#Index("ix_normalized_events_guid", NormalizedEvent.guid)
#Index("ix_normalized_events_nonce", NormalizedEvent.nonce)
#Index("ix_normalized_events_proof_hash", NormalizedEvent.proof_hash)
#Index("ix_normalized_events_raw_source", NormalizedEvent.raw_table, NormalizedEvent.raw_pk)