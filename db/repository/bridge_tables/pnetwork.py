from sqlalchemy import BigInteger, Column, Float, Numeric, String

from db.database import Base
from db.repository.common_models import BlockchainTransaction


class BscBlockchainTransactions(BlockchainTransaction):
    __tablename__ = "bsc_blockchain_transactions"


class BitcoinBlockchainTransactions(BlockchainTransaction):
    __tablename__ = "bitcoin_blockchain_transactions"


class PNetworkCrossChainTransactions(Base):
    __tablename__ = "pnetwork_cross_chain_transactions"

    id = Column(BigInteger, nullable=False, autoincrement=True, primary_key=True)
    cctx_id = Column(String(128), nullable=False, unique=True)

    src_blockchain = Column(String(16), nullable=False)
    src_transaction_hash = Column(String(128), nullable=False)
    src_from_address = Column(String(128), nullable=True)
    src_to_address = Column(String(128), nullable=True)
    src_fee = Column(Numeric(50, 0), nullable=True)
    src_fee_usd = Column(Float, nullable=True)
    src_value = Column(Numeric(50, 0), nullable=True)
    src_timestamp = Column(BigInteger, nullable=False)

    dst_blockchain = Column(String(16), nullable=True)
    dst_transaction_hash = Column(String(128), nullable=True)
    dst_from_address = Column(String(128), nullable=True)
    dst_to_address = Column(String(128), nullable=True)
    dst_fee = Column(Numeric(50, 0), nullable=True)
    dst_fee_usd = Column(Float, nullable=True)
    dst_value = Column(Numeric(50, 0), nullable=True)
    dst_timestamp = Column(BigInteger, nullable=True)

    correlation_id = Column(String(128), nullable=True)
    depositor = Column(String(128), nullable=True)
    recipient = Column(String(128), nullable=True)
    src_contract_address = Column(String(128), nullable=True)
    dst_contract_address = Column(String(128), nullable=True)
    token_in = Column(String(128), nullable=True)
    token_out = Column(String(128), nullable=True)
    amount_in = Column(Numeric(50, 0), nullable=True)
    amount_out = Column(Numeric(50, 0), nullable=True)
    amount_usd = Column(Float, nullable=True)
