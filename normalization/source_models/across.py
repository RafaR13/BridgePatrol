from sqlalchemy import BigInteger, Column, Float, Integer, Numeric, String

from db.repository.common_models import BlockchainTransaction
from db.database import Base


class AcrossRelayerRefund(Base):
    __tablename__ = "across_relayer_refund"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    root_bundle_id = Column(Integer, nullable=False)
    amount_to_return = Column(Numeric(30, 0), nullable=False)
    refund_amount = Column(Numeric(30, 0), nullable=False)
    l2_token_address = Column(String(42), nullable=False)
    refund_address = Column(String(42), nullable=False)
    caller = Column(String(42), nullable=False)


class AcrossFilledRelay(Base):
    __tablename__ = "across_filled_relay"

    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    src_chain = Column(String(10), nullable=False)
    deposit_id = Column(String(78), nullable=False, primary_key=True)
    relayer = Column(String(42), nullable=False)
    input_token = Column(String(42), nullable=False)
    output_token = Column(String(42), nullable=False)
    input_amount = Column(Numeric(30, 0), nullable=False)
    output_amount = Column(Numeric(30, 0), nullable=False)
    repayment_chain = Column(String(10), nullable=False)
    fill_deadline = Column(BigInteger, nullable=False)
    exclusivity_deadline = Column(BigInteger, nullable=False)
    exclusive_relayer = Column(String(42), nullable=False)
    depositor = Column(String(42), nullable=False)
    recipient = Column(String(42), nullable=False)
    message_hash = Column(String(64), nullable=True)
    updated_recipient = Column(String(42), nullable=False)
    updated_message_hash = Column(String(64), nullable=True)
    updated_output_amount = Column(String(30), nullable=False)
    fill_type = Column(Integer, nullable=False)


class AcrossFundsDeposited(Base):
    __tablename__ = "across_funds_deposited"

    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    destination_chain = Column(String(24), nullable=False)
    deposit_id = Column(String(78), nullable=False, primary_key=True)
    depositor = Column(String(42), nullable=False)
    input_token = Column(String(42), nullable=False)
    output_token = Column(String(42), nullable=False)
    input_amount = Column(Numeric(30, 0), nullable=False)
    output_amount = Column(Numeric(30, 0), nullable=False)
    quote_timestamp = Column(BigInteger, nullable=False)
    fill_deadline = Column(BigInteger, nullable=False)
    exclusivity_deadline = Column(BigInteger, nullable=False)
    recipient = Column(String(42), nullable=False)
    exclusive_relayer = Column(String(42), nullable=False)
    message = Column(String, nullable=True)


class AcrossBlockchainTransaction(BlockchainTransaction):
    __tablename__ = "across_blockchain_transactions"