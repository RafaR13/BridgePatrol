from sqlalchemy import BigInteger, Column, Float, Numeric, String

from db.database import Base
from db.repository.common_models import BlockchainTransaction


class ManualCrossChainTransactionMixin:
    id = Column(BigInteger, nullable=False, autoincrement=True, primary_key=True)

    cctx_id = Column(String(128), nullable=False, unique=True)

    src_blockchain = Column(String(16), nullable=True)
    src_transaction_hash = Column(String(128), nullable=True)
    src_from_address = Column(String(128), nullable=True)
    src_to_address = Column(String(128), nullable=True)
    src_fee = Column(Numeric(50, 18), nullable=True)
    src_fee_usd = Column(Float, nullable=True)
    src_value = Column(Numeric(50, 18), nullable=True)
    src_timestamp = Column(BigInteger, nullable=True)

    dst_blockchain = Column(String(16), nullable=True)
    dst_transaction_hash = Column(String(128), nullable=True)
    dst_from_address = Column(String(128), nullable=True)
    dst_to_address = Column(String(128), nullable=True)
    dst_fee = Column(Numeric(50, 18), nullable=True)
    dst_fee_usd = Column(Float, nullable=True)
    dst_value = Column(Numeric(50, 18), nullable=True)
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


class MeterIoBlockchainTransactions(BlockchainTransaction):
    __tablename__ = "meterio_blockchain_transactions"


class MeterIoCrossChainTransactions(ManualCrossChainTransactionMixin, Base):
    __tablename__ = "meterio_cross_chain_transactions"


class QubitBlockchainTransactions(BlockchainTransaction):
    __tablename__ = "qubit_blockchain_transactions"


class QubitCrossChainTransactions(ManualCrossChainTransactionMixin, Base):
    __tablename__ = "qubit_cross_chain_transactions"


class ThorchainBlockchainTransactions(BlockchainTransaction):
    __tablename__ = "thorchain_blockchain_transactions"


class ThorchainCrossChainTransactions(ManualCrossChainTransactionMixin, Base):
    __tablename__ = "thorchain_cross_chain_transactions"


class WormholeBlockchainTransactions(BlockchainTransaction):
    __tablename__ = "wormhole_blockchain_transactions"


class WormholeCrossChainTransactions(ManualCrossChainTransactionMixin, Base):
    __tablename__ = "wormhole_cross_chain_transactions"
