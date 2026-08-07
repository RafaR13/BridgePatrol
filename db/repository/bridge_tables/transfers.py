from sqlalchemy import BigInteger, Column, Integer, Numeric, String

from db.database import Base


class TransferTableMixin:
    id = Column(BigInteger, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(88), nullable=False)
    block_number = Column(Integer, nullable=False)
    log_index = Column(Integer, nullable=False)
    token_address = Column(String(42), nullable=False)
    from_address = Column(String(42), nullable=False)
    to_address = Column(String(42), nullable=False)
    amount = Column(Numeric(78, 0), nullable=False)
    trigger_event_topic = Column(String(66), nullable=False)
    trigger_contract_address = Column(String(42), nullable=False)


class AcrossTransfer(TransferTableMixin, Base):
    __tablename__ = "across_transfers"


class CCIPTransfer(TransferTableMixin, Base):
    __tablename__ = "ccip_transfers"


class CCTPTransfer(TransferTableMixin, Base):
    __tablename__ = "cctp_transfers"


class DeBridgeTransfer(TransferTableMixin, Base):
    __tablename__ = "debridge_transfers"


class MayanTransfer(TransferTableMixin, Base):
    __tablename__ = "mayan_transfers"


class MeterIoTransfer(TransferTableMixin, Base):
    __tablename__ = "meter_io_transfers"


class OmnibridgeTransfer(TransferTableMixin, Base):
    __tablename__ = "omnibridge_transfers"


class PolygonTransfer(TransferTableMixin, Base):
    __tablename__ = "polygon_transfers"


class RoninTransfer(TransferTableMixin, Base):
    __tablename__ = "ronin_transfers"
