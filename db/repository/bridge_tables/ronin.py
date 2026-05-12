from sqlalchemy import BigInteger, Column, Float, Integer, Numeric, String

from db.repository.common_models import BlockchainTransaction
from db.database import Base


class RoninDepositRequested(Base):
    __tablename__ = "ronin_deposit_requested"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    address = Column(String(128), nullable=True)
    deposit_id = Column(Integer, nullable=False)
    kind = Column(String(10), nullable=False)
    depositor = Column(String(42), nullable=False)
    input_token = Column(String(42), nullable=False)
    recipient = Column(String(42), nullable=False)
    output_token = Column(String(42), nullable=False)
    dst_blockchain = Column(String(10), nullable=False)
    token_standard = Column(String(10), nullable=False)
    amount = Column(Numeric(30, 0), nullable=False)


class RoninTokenDeposited(Base):
    __tablename__ = "ronin_token_deposited"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    address = Column(String(128), nullable=True)
    deposit_id = Column(Integer, nullable=False)
    kind = Column(String(10), nullable=False)
    src_blockchain = Column(String(10), nullable=False)
    depositor = Column(String(42), nullable=False)
    input_token = Column(String(42), nullable=False)
    recipient = Column(String(42), nullable=False)
    output_token = Column(String(42), nullable=False)
    token_standard = Column(String(10), nullable=False)
    amount = Column(Numeric(30, 0), nullable=False)


class RoninWithdrawalRequested(Base):
    __tablename__ = "ronin_withdrawal_requested"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    address = Column(String(128), nullable=True)
    withdrawal_id = Column(Integer, nullable=False)
    kind = Column(String(10), nullable=False)
    withdrawer = Column(String(42), nullable=False)
    input_token = Column(String(42), nullable=False)
    recipient = Column(String(42), nullable=False)
    dst_blockchain = Column(String(10), nullable=False)
    output_token = Column(String(42), nullable=False)
    token_standard = Column(String(10), nullable=False)
    amount = Column(Numeric(30, 0), nullable=False)


class RoninTokenWithdrew(Base):
    __tablename__ = "ronin_token_withdrew"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    address = Column(String(128), nullable=True)
    withdrawal_id = Column(Integer, nullable=False)
    kind = Column(String(10), nullable=False)
    src_blockchain = Column(String(10), nullable=False)
    withdrawer = Column(String(42), nullable=False)
    input_token = Column(String(42), nullable=False)
    recipient = Column(String(42), nullable=False)
    output_token = Column(String(42), nullable=False)
    token_standard = Column(String(10), nullable=False)
    amount = Column(Numeric(30, 0), nullable=False)


class RoninBlockchainTransactions(BlockchainTransaction):
    __tablename__ = "ronin_blockchain_transactions"


class RoninCrossChainTransactions(Base):
    __tablename__ = "ronin_cross_chain_transactions"

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
    dst_contract_address = Column(String(42), nullable=False)
    amount = Column(Numeric(30, 0), nullable=False)
    amount_usd = Column(Float, nullable=True)
