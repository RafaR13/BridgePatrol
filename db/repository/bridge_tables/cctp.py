from sqlalchemy import BigInteger, Column, Float, Integer, Numeric, String

from db.repository.common_models import BlockchainTransaction
from db.database import Base


class CCTPDepositForBurn(Base):
    __tablename__ = "cctp_deposit_for_burn"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    address = Column(String(128), nullable=True)
    nonce = Column(Integer, nullable=False)
    depositor = Column(String(42), nullable=False)
    burn_token = Column(String(42), nullable=False)
    recipient = Column(String(42), nullable=False)
    dst_blockchain = Column(String(10), nullable=False)
    amount = Column(Numeric(30, 0), nullable=False)


class CCTPMessageReceived(Base):
    __tablename__ = "cctp_message_received"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    address = Column(String(128), nullable=True)
    nonce = Column(Integer, nullable=False)
    src_blockchain = Column(String(10), nullable=False)
    input_token = Column(String(42), nullable=False)
    depositor = Column(String(42), nullable=False)
    recipient = Column(String(42), nullable=False)
    amount = Column(Numeric(30, 0), nullable=False)


class CCTPBlockchainTransactions(BlockchainTransaction):
    __tablename__ = "cctp_blockchain_transactions"


class CCTPTransfer(Base):
    __tablename__ = "cctp_transfers"

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


class CCTPCrossChainTransactions(Base):
    __tablename__ = "cctp_cross_chain_transactions"

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
    amount = Column(Numeric(30, 0), nullable=False)
    amount_usd = Column(Float, nullable=True)
