from sqlalchemy import BigInteger, Boolean, Column, Float, Integer, Numeric, String

from db.repository.common_models import BlockchainTransaction
from db.database import Base


class CCIPSendRequested(Base):
    __tablename__ = "ccip_send_requested"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    # address = Column(String(128), nullable=True)
    nonce = Column(Integer, nullable=False)
    sender = Column(String(42), nullable=False)
    receiver = Column(String(42), nullable=False)
    sequence_number = Column(Integer, nullable=False)
    gas_limit = Column(Integer, nullable=False)
    strict = Column(Boolean, nullable=False)
    fee_token = Column(String(42), nullable=False)
    fee_token_amount = Column(Numeric(30, 0), nullable=False)
    input_token = Column(String(42), nullable=True)
    output_token = Column(String(42), nullable=True)
    amount = Column(Numeric(30, 0), nullable=True)
    message_id = Column(String(66), nullable=False)


class CCIPExecutionStateChanged(Base):
    __tablename__ = "ccip_execution_state_changed"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    # address = Column(String(128), nullable=True)
    sequence_number = Column(Integer, nullable=False)
    message_id = Column(String(66), nullable=False)
    state = Column(Integer, nullable=False)
    return_data = Column(String(500), nullable=False)


class CCIPBlockchainTransactions(BlockchainTransaction):
    __tablename__ = "ccip_blockchain_transactions"


class CCIPTransfer(Base):
    __tablename__ = "ccip_transfers"

    id = Column(BigInteger, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    block_number = Column(Integer, nullable=False)
    log_index = Column(Integer, nullable=False)
    token_address = Column(String(42), nullable=False)
    from_address = Column(String(42), nullable=False)
    to_address = Column(String(42), nullable=False)
    amount = Column(Numeric(78, 0), nullable=False)
    trigger_event_topic = Column(String(66), nullable=False)
    trigger_contract_address = Column(String(42), nullable=False)


class CCIPCrossChainTransactions(Base):
    __tablename__ = "ccip_cross_chain_transactions"

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
    deposit_id = Column(BigInteger, nullable=False)
    depositor = Column(String(42), nullable=False)
    recipient = Column(String(42), nullable=False)
    src_contract_address = Column(String(42), nullable=False)
    fee_token = Column(String(42), nullable=False)
    fee_token_amount = Column(Numeric(30, 0), nullable=False)
    fee_token_amount_usd = Column(Float, nullable=True)
    amount = Column(Numeric(30, 0), nullable=False)
    amount_usd = Column(Float, nullable=True)
