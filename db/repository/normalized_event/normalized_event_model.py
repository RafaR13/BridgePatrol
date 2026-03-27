from sqlalchemy import BigInteger, Column, Enum as SAEnum, Index, Integer, Numeric, String

from normalization.event_types import NormalizedEventType
from db.database import Base


class NormalizedEvent(Base):
    __tablename__ = "normalized_events"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # provenance
    bridge = Column(String(32), nullable=False)
    blockchain = Column(String(16), nullable=False)
    raw_table = Column(String(128), nullable=False)
    raw_pk = Column(String(256), nullable=False)

    # tx / block context
    transaction_hash = Column(String(88), nullable=False)
    block_number = Column(BigInteger, nullable=True)
    timestamp = Column(BigInteger, nullable=True)
    log_index = Column(Integer, nullable=True)

    # normalized semantics
    event_type = Column(String(64), nullable=False)

    # correlation
    correlation_id = Column(String(128), nullable=True)
    correlation_type = Column(String(32), nullable=True)

    # cross-chain context
    src_blockchain = Column(String(16), nullable=True)
    dst_blockchain = Column(String(16), nullable=True)

    # actors
    actor_from = Column(String(128), nullable=True)
    actor_to = Column(String(128), nullable=True)
    signer = Column(String(128), nullable=True)
    relayer = Column(String(128), nullable=True)

    # assets
    token_in = Column(String(128), nullable=True)
    token_out = Column(String(128), nullable=True)
    amount_in = Column(Numeric(50, 0), nullable=True)
    amount_out = Column(Numeric(50, 0), nullable=True)

    # messaging / proof identifiers
    nonce = Column(String(128), nullable=True)
    message_id = Column(String(128), nullable=True)
    message_hash = Column(String(128), nullable=True)
    payload_hash = Column(String(128), nullable=True)
    proof_hash = Column(String(128), nullable=True)
    guid = Column(String(128), nullable=True)

    # contracts / status
    contract_address = Column(String(128), nullable=True)
    status = Column(String(32), nullable=True)

    # bridge-specific leftovers
    extra_data = Column(String(20000), nullable=True)

    def __init__(
        self,
        bridge,
        blockchain,
        raw_table,
        raw_pk,
        transaction_hash,
        event_type,
        block_number=None,
        timestamp=None,
        log_index=None,
        correlation_id=None,
        correlation_type=None,
        src_blockchain=None,
        dst_blockchain=None,
        actor_from=None,
        actor_to=None,
        signer=None,
        relayer=None,
        token_in=None,
        token_out=None,
        amount_in=None,
        amount_out=None,
        nonce=None,
        message_id=None,
        message_hash=None,
        payload_hash=None,
        proof_hash=None,
        guid=None,
        contract_address=None,
        status=None,
        extra_data=None,
    ):
        self.bridge = bridge
        self.blockchain = blockchain
        self.raw_table = raw_table
        self.raw_pk = raw_pk
        self.transaction_hash = transaction_hash
        self.event_type = event_type
        self.block_number = block_number
        self.timestamp = timestamp
        self.log_index = log_index
        self.correlation_id = correlation_id
        self.correlation_type = correlation_type
        self.src_blockchain = src_blockchain
        self.dst_blockchain = dst_blockchain
        self.actor_from = actor_from
        self.actor_to = actor_to
        self.signer = signer
        self.relayer = relayer
        self.token_in = token_in
        self.token_out = token_out
        self.amount_in = amount_in
        self.amount_out = amount_out
        self.nonce = nonce
        self.message_id = message_id
        self.message_hash = message_hash
        self.payload_hash = payload_hash
        self.proof_hash = proof_hash
        self.guid = guid
        self.contract_address = contract_address
        self.status = status
        self.extra_data = extra_data

    def __repr__(self):
        return (
            f"<NormalizedEvent(id={self.id}, "
            f"bridge={self.bridge}, "
            f"blockchain={self.blockchain}, "
            f"transaction_hash={self.transaction_hash}, "
            f"event_type={self.event_type}, "
            f"correlation_type={self.correlation_type}, "
            f"correlation_id={self.correlation_id})>"
        )


Index("ix_normalized_events_bridge", NormalizedEvent.bridge)
Index("ix_normalized_events_blockchain", NormalizedEvent.blockchain)
Index("ix_normalized_events_tx_hash", NormalizedEvent.transaction_hash)
Index("ix_normalized_events_event_type", NormalizedEvent.event_type)
Index("ix_normalized_events_corr", NormalizedEvent.correlation_type, NormalizedEvent.correlation_id)
Index("ix_normalized_events_message_id", NormalizedEvent.message_id)
Index("ix_normalized_events_guid", NormalizedEvent.guid)
Index("ix_normalized_events_nonce", NormalizedEvent.nonce)
Index("ix_normalized_events_proof_hash", NormalizedEvent.proof_hash)
Index("ix_normalized_events_payload_hash", NormalizedEvent.payload_hash)