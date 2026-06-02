from sqlalchemy import JSON, Column, String, Integer, BigInteger, Numeric
from db.database import Base


class BlockchainTransaction(Base):
    __abstract__ = True

    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(88), nullable=False, primary_key=True)
    block_number = Column(Integer, nullable=False)
    timestamp = Column(BigInteger, nullable=False)
    from_address = Column(String(44), nullable=True)
    to_address = Column(String(44), nullable=True)
    status = Column(Integer, nullable=False)
    value = Column(Numeric(30, 0), nullable=True)
    input_data = Column(String(35000), nullable=True)
    # decoded_input_data = Column(JSON, nullable=True)
    calls = Column(JSON, nullable=True)
    fee = Column(Numeric(30, 0), nullable=False)
