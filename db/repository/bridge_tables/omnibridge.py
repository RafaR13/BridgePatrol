from sqlalchemy import BigInteger, Column, Float, Integer, Numeric, String

from db.repository.common_models import BlockchainTransaction
from db.database import Base

class OmnibridgeTokensBridgingInitiated(Base):
    __tablename__ = "omnibridge_tokens_bridging_initiated"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    token = Column(String(42), nullable=False)
    sender = Column(String(42), nullable=False)
    value = Column(Numeric(30, 0), nullable=False)
    message_id = Column(String(66), nullable=False)


# TokensBridged (index_topic_1 address token, index_topic_2 address recipient, uint256 value,
# index_topic_3 bytes32 messageId)
class OmnibridgeTokensBridged(Base):
    __tablename__ = "omnibridge_tokens_bridged"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    token = Column(String(42), nullable=False)
    recipient = Column(String(42), nullable=False)
    value = Column(Numeric(30, 0), nullable=False)
    message_id = Column(String(66), nullable=False)


class OmnibridgeRelayedMessage(Base):
    __tablename__ = "omnibridge_relayed_message"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    recipient = Column(String(42), nullable=False)
    value = Column(Numeric(30, 0), nullable=False)
    src_transaction_hash = Column(String(66), nullable=False)


# SignedForUserRequest (index_topic_1 address signer, bytes32 messageHash)
class OmnibridgeSignedForUserRequest(Base):
    __tablename__ = "omnibridge_signed_for_user_request"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    signer = Column(String(42), nullable=False)
    message_hash = Column(String(66), nullable=False)


# SignedForAffirmation (index_topic_1 address signer, bytes32 messageHash)
# SignedForAffirmation (index_topic_1 address signer, bytes32 transactionHash)
class OmnibridgeSignedForAffirmation(Base):
    __tablename__ = "omnibridge_signed_for_affirmation"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    signer = Column(String(42), nullable=False)
    message_hash = Column(String(66), nullable=True)
    src_transaction_hash = Column(String(66), nullable=True)


# UserRequestForSignature (address recipient, uint256 value)
# UserRequestForSignature (index_topic_1 bytes32 messageId, bytes encodedData)
class OmnibridgeUserRequestForSignature(Base):
    __tablename__ = "omnibridge_user_request_for_signature"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    message_id = Column(String(66), nullable=True)
    encoded_data = Column(String(1000), nullable=True)
    encoded_data_hash = Column(String(66), nullable=True)
    recipient = Column(String(42), nullable=True)
    value = Column(Numeric(30, 0), nullable=True)


# AffirmationCompleted (address recipient, uint256 value, bytes32 transactionHash)
class OmnibridgeAffirmationCompleted(Base):
    __tablename__ = "omnibridge_affirmation_completed"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    recipient = Column(String(42), nullable=False)
    value = Column(Numeric(30, 0), nullable=False)
    src_transaction_hash = Column(String(66), nullable=False)


# UserRequestForAffirmation (index_topic_1 bytes32 messageId, bytes encodedData)
# UserRequestForAffirmation (address recipient, uint256 value)
class OmnibridgeUserRequestForAffirmation(Base):
    __tablename__ = "omnibridge_user_request_for_affirmation"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    message_id = Column(String(66), nullable=True)
    encoded_data = Column(String(1000), nullable=True)
    recipient = Column(String(42), nullable=True)
    value = Column(Numeric(30, 0), nullable=True)


class OmnibridgeBlockchainTransactions(BlockchainTransaction):
    __tablename__ = "omnibridge_blockchain_transaction"


########## Processed Data ##########


class OmnibridgeCrossChainTransactions(Base):
    __tablename__ = "omnibridge_cross_chain_transactions"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
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
    message_id = Column(String(66), nullable=True)
    depositor = Column(String(42), nullable=False)
    recipient = Column(String(42), nullable=False)
    src_contract_address = Column(String(42), nullable=False)
    dst_contract_address = Column(String(42), nullable=False)
    amount = Column(Numeric(30, 0), nullable=False)
    amount_usd = Column(Float, nullable=True)


class OmnibridgeOperatorTransactions(Base):
    __tablename__ = "omnibridge_operator_transactions"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    from_address = Column(String(42), nullable=False)
    to_address = Column(String(42), nullable=False)
    signer = Column(String(42), nullable=False)
    fee = Column(Numeric(30, 0), nullable=False)
    fee_usd = Column(Float, nullable=True)
    timestamp = Column(BigInteger, nullable=False)
    status = Column(Integer, nullable=False)
