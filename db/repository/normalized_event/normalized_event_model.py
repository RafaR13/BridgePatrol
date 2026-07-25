from sqlalchemy import BigInteger, Column, Integer, Numeric, String

from db.database import Base

class NormalizedEvent(Base):
    __abstract__ = True

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # provenance
    bridge = Column(String(32), nullable=False)
    blockchain = Column(String(16), nullable=False)
    raw_table = Column(String(128), nullable=False)
    raw_pk = Column(String(256), nullable=False)

    # tx / block context
    transaction_hash = Column(String(88), nullable=False)
    cctx_id = Column(String(128), nullable=True)
    block_number = Column(BigInteger, nullable=True)
    timestamp = Column(BigInteger, nullable=True)
    log_index = Column(Integer, nullable=True)

    # normalized semantics
    event_type = Column(String(64), nullable=False)

    # correlation
    correlation_id = Column(String(128), nullable=True)

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
        cctx_id=None,
        block_number=None,
        timestamp=None,
        log_index=None,
        correlation_id=None,
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
        self.cctx_id = cctx_id
        self.event_type = event_type
        self.block_number = block_number
        self.timestamp = timestamp
        self.log_index = log_index
        self.correlation_id = correlation_id
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
            f"correlation_id={self.correlation_id})>"
        )

class RoninNormalizedEvent(NormalizedEvent):
    __tablename__ = "ronin_normalized_event"

class PolygonNormalizedEvent(NormalizedEvent):
    __tablename__ = "polygon_normalized_event"

class OmnibridgeNormalizedEvent(NormalizedEvent):
    __tablename__ = "omnibridge_normalized_event"

class MayanNormalizedEvent(NormalizedEvent):
    __tablename__ = "mayan_normalized_event"

class NomadNormalizedEvent(NormalizedEvent):
    __tablename__ = "nomad_normalized_event"

class DebridgeNormalizedEvent(NormalizedEvent):
    __tablename__ = "debridge_normalized_event"

class CctpNormalizedEvent(NormalizedEvent):
    __tablename__ = "cctp_normalized_event"

class CcipNormalizedEvent(NormalizedEvent):
    __tablename__ = "ccip_normalized_event"

class AcrossNormalizedEvent(NormalizedEvent):
    __tablename__ = "across_normalized_event"

class ThorchainNormalizedEvent(NormalizedEvent):
    __tablename__ = "thorchain_normalized_event"

class MeterIoNormalizedEvent(NormalizedEvent):
    __tablename__ = "meter_io_normalized_event"

class QubitNormalizedEvent(NormalizedEvent):
    __tablename__ = "qubit_normalized_event"

class PNetworkNormalizedEvent(NormalizedEvent):
    __tablename__ = "pnetwork_normalized_event"


BscNormalizedEvent = PNetworkNormalizedEvent


BRIDGE_NORMALIZED_EVENT_MODELS = {
    "across": AcrossNormalizedEvent,
    "ccip": CcipNormalizedEvent,
    "cctp": CctpNormalizedEvent,
    "debridge": DebridgeNormalizedEvent,
    "mayan": MayanNormalizedEvent,
    "nomad": NomadNormalizedEvent,
    "omnibridge": OmnibridgeNormalizedEvent,
    "polygon": PolygonNormalizedEvent,
    "ronin": RoninNormalizedEvent,
    "thorchain": ThorchainNormalizedEvent,
    "meter.io": MeterIoNormalizedEvent,
    "qubit": QubitNormalizedEvent,
    "pnetwork": PNetworkNormalizedEvent,
}


NORMALIZED_EVENT_FIELDS = (
    "bridge",
    "blockchain",
    "raw_table",
    "raw_pk",
    "transaction_hash",
    "cctx_id",
    "event_type",
    "block_number",
    "timestamp",
    "log_index",
    "correlation_id",
    "src_blockchain",
    "dst_blockchain",
    "actor_from",
    "actor_to",
    "signer",
    "relayer",
    "token_in",
    "token_out",
    "amount_in",
    "amount_out",
    "nonce",
    "message_id",
    "message_hash",
    "payload_hash",
    "proof_hash",
    "guid",
    "contract_address",
    "status",
    "extra_data",
)


def get_normalized_event_model(bridge: str) -> type[NormalizedEvent]:
    try:
        return BRIDGE_NORMALIZED_EVENT_MODELS[bridge]
    except KeyError as exc:
        raise ValueError(f"Unsupported bridge for normalized events: {bridge}") from exc


def cast_normalized_event_for_bridge(
    event: NormalizedEvent,
    bridge: str,
) -> NormalizedEvent:
    model = get_normalized_event_model(bridge)
    if isinstance(event, model):
        return event

    payload = {
        field: getattr(event, field)
        for field in NORMALIZED_EVENT_FIELDS
    }
    return model(**payload)
