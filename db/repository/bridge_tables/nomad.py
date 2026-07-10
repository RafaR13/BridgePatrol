from sqlalchemy import BigInteger, Column, Float, Integer, Numeric, String

from db.database import Base
from db.repository.common_models import BlockchainTransaction


class NomadRouterSend(Base):
    __tablename__ = "nomad_router_send"

    id = Column(Integer, primary_key=True, autoincrement=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    input_token = Column(String(42), nullable=False)
    depositor = Column(String(42), nullable=False)
    dst_blockchain = Column(String(10), nullable=False)
    recipient = Column(String(42), nullable=False)
    amount = Column(Numeric(30, 0), nullable=False)
    to_hook = Column(Integer)
    fast_liquidity_enabled = Column(Integer)


class NomadRouterReceive(Base):
    __tablename__ = "nomad_router_receive"

    id = Column(Integer, primary_key=True, autoincrement=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    src_blockchain = Column(String(10), nullable=False)
    nonce = Column(BigInteger, nullable=False)
    output_token = Column(String(42), nullable=False)
    recipient = Column(String(42), nullable=False)
    liquidity_provider = Column(String(42), nullable=True)
    amount = Column(Numeric(30, 0), nullable=False)


class NomadEthHelperSend(Base):
    __tablename__ = "nomad_eth_helper_send"

    id = Column(Integer, primary_key=True, autoincrement=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    from_address = Column(String(42), nullable=False)


class NomadReplicaProcess(Base):
    __tablename__ = "nomad_replica_process"

    id = Column(Integer, primary_key=True, autoincrement=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    message_hash = Column(String(66), nullable=False)
    success = Column(Integer, nullable=False)
    return_data = Column(String, nullable=True)


class NomadHomeDispatch(Base):
    __tablename__ = "nomad_home_dispatch"

    id = Column(Integer, primary_key=True, autoincrement=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    message_hash = Column(String(66), nullable=False)
    leaf_index = Column(BigInteger, nullable=False)
    nonce = Column(BigInteger, nullable=False)
    committed_root = Column(String(66), nullable=False)
    src_blockchain = Column(String(10), nullable=False)
    src_router = Column(String(42), nullable=False)
    dst_blockchain = Column(String(10), nullable=False)
    dst_router = Column(String(42), nullable=False)
    token_blockchain = Column(String(10), nullable=False)
    token_address = Column(String(42), nullable=False)
    action_type = Column(Integer, nullable=False)
    recipient = Column(String(42), nullable=False)
    amount = Column(Numeric(30, 0), nullable=False)
    details_hash = Column(String(66), nullable=False)


class NomadBlockchainTransactions(BlockchainTransaction):
    __tablename__ = "nomad_blockchain_transactions"


class NomadCrossChainTransactions(Base):
    __tablename__ = "nomad_cross_chain_transactions"

    id = Column(BigInteger, primary_key=True)
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
    deposit_hash = Column(String(66), nullable=False)
    depositor = Column(String(42), nullable=True)
    recipient = Column(String(42), nullable=False)
    src_contract_address = Column(String(42), nullable=False)
    dst_contract_address = Column(String(42), nullable=False)
    amount = Column(Numeric(30, 0), nullable=False)
    amount_usd = Column(Float, nullable=True)
