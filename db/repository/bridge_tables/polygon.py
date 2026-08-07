from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    Numeric,
    String,
)

from db.repository.common_models import BlockchainTransaction
from db.database import Base


class PolygonStateSynced(Base):
    __tablename__ = "polygon_state_synced"

    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    state_id = Column(Integer, nullable=False, primary_key=True)
    contract_address = Column(String(42), nullable=False)
    # address = Column(String(128), nullable=True)
    data = Column(String(10000), nullable=False)


class PolygonStateCommitted(Base):
    __tablename__ = "polygon_state_committed"

    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    # address = Column(String(128), nullable=True)
    state_id = Column(Integer, nullable=False, primary_key=True)
    success = Column(Boolean, nullable=False)


class PolygonLockedToken(Base):
    __tablename__ = "polygon_locked_token"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    # address = Column(String(128), nullable=True)
    depositor = Column(String(42), nullable=False)
    deposit_receiver = Column(String(42), nullable=False)
    root_token = Column(String(42), nullable=False)
    amount = Column(Numeric(30, 0), nullable=False)


class PolygonExitedToken(Base):
    __tablename__ = "polygon_exited_token"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    # address = Column(String(128), nullable=True)
    exitor = Column(String(42), nullable=False)
    root_token = Column(String(42), nullable=False)
    amount = Column(Numeric(30, 0), nullable=False)


class PolygonTokenDeposited(Base):
    __tablename__ = "polygon_token_deposited"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    # address = Column(String(128), nullable=True)
    root_token = Column(String(42), nullable=False)
    child_token = Column(String(42), nullable=False)
    user = Column(String(42), nullable=False)
    amount = Column(Numeric(30, 0), nullable=False)
    deposit_count = Column(BigInteger, nullable=False)


class PolygonPOLWithdraw(Base):
    __tablename__ = "polygon_pol_withdraw"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    # address = Column(String(128), nullable=True)
    token = Column(String(42), nullable=False)
    from_address = Column(String(42), nullable=False)
    amount = Column(Numeric(30, 0), nullable=False)
    input1 = Column(String(100), nullable=True)
    output1 = Column(String(100), nullable=True)


class PolygonBridgeWithdraw(Base):
    __tablename__ = "polygon_bridge_withdraw"

    id = Column(BigInteger, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    # address = Column(String(128), nullable=True)
    exit_id = Column(String(48), nullable=False)
    user = Column(String(42), nullable=False)
    token = Column(String(42), nullable=False)
    amount = Column(Numeric(30, 0), nullable=False)


class PolygonNewDepositBlock(Base):
    __tablename__ = "polygon_new_deposit_block"

    id = Column(BigInteger, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    # address = Column(String(128), nullable=True)
    owner = Column(String(42), nullable=False)
    token = Column(String(42), nullable=False)
    amount = Column(Numeric(30, 0), nullable=False)
    deposit_block_id = Column(BigInteger, nullable=False)


class PolygonChildTokenBurn(Base):
    __tablename__ = "polygon_child_token_burn"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    # address = Column(String(128), nullable=True)
    log_index = Column(Integer, nullable=False)
    child_token = Column(String(42), nullable=False)
    from_address = Column(String(42), nullable=False)
    amount = Column(Numeric(30, 0), nullable=False)
    root_token = Column(String(42), nullable=False)


class PolygonTokenMapping(Base):
    __tablename__ = "polygon_token_mappings"

    root_token = Column(String(42), nullable=False, primary_key=True)
    child_token = Column(String(42), nullable=True)
    checked_at = Column(DateTime(timezone=True), nullable=True)


class PolygonBlockchainTransactions(BlockchainTransaction):
    __tablename__ = "polygon_blockchain_transactions"


class PolygonCrossChainTransactions(Base):
    __tablename__ = "polygon_cross_chain_transactions"

    id = Column(BigInteger, nullable=False, autoincrement=True, primary_key=True)
    src_blockchain = Column(String(10), nullable=False)
    src_transaction_hash = Column(String(66), nullable=False)
    src_from_address = Column(String(42), nullable=False)
    src_to_address = Column(String(42), nullable=False)
    src_fee = Column(Numeric(30, 0), nullable=False)
    src_fee_usd = Column(Float, nullable=True)
    src_timestamp = Column(BigInteger, nullable=False)
    dst_blockchain = Column(String(10), nullable=False)
    dst_transaction_hash = Column(String(66), nullable=False)
    dst_from_address = Column(String(42), nullable=False)
    dst_to_address = Column(String(42), nullable=False)
    dst_fee = Column(Numeric(30, 0), nullable=False)
    dst_fee_usd = Column(Float, nullable=True)
    dst_timestamp = Column(BigInteger, nullable=False)
    deposit_id = Column(String(48), nullable=False)
    depositor = Column(String(42), nullable=False)
    recipient = Column(String(42), nullable=False)
    src_contract_address = Column(String(42), nullable=False)
    amount = Column(Numeric(30, 0), nullable=False)
    amount_usd = Column(Float, nullable=True)
