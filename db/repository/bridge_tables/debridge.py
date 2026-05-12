from sqlalchemy import BigInteger, Column, Float, Integer, Numeric, String

from db.repository.common_models import BlockchainTransaction
from db.database import Base


class DeBridgeCreatedOrder(Base):
    __tablename__ = "debridge_created_order"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(88), nullable=False)
    address = Column(String(128), nullable=True)
    maker_order_nonce = Column(Numeric(30, 0), nullable=False)
    maker_src = Column(String(44), nullable=False)
    src_blockchain = Column(String(10), nullable=False)
    give_token_address = Column(String(44), nullable=False)
    give_amount = Column(Numeric(30, 0), nullable=False)
    dst_blockchain = Column(String(10), nullable=False)
    take_token_address = Column(String(44), nullable=False)
    take_amount = Column(Numeric(50, 0), nullable=False)
    receiver_dst = Column(String(44), nullable=False)
    give_patch_authority_src = Column(String(44), nullable=False)
    order_authority_address_dst = Column(String(44), nullable=False)
    allowed_taker_dst = Column(String(44), nullable=True)
    allowed_cancel_beneficiary_src = Column(String(44), nullable=True)
    external_call = Column(String, nullable=True)
    order_id = Column(String(66), nullable=True)
    affiliate_fee = Column(String, nullable=True)
    native_fix_fee = Column(Numeric(30, 0), nullable=True)
    percent_fee = Column(Numeric(30, 0), nullable=True)
    referral_code = Column(Integer, nullable=True)
    _metadata = Column(
        String, nullable=True
    )  # we added the underscore to avoid conflicts with the metadata column in the base class
    original_token = Column(String(44), nullable=True)
    original_amount = Column(Numeric(50, 0), nullable=True)


class DeBridgeFulfilledOrder(Base):
    __tablename__ = "debridge_fulfilled_order"

    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(88), nullable=False)
    address = Column(String(128), nullable=True)
    maker_order_nonce = Column(Numeric(30, 0), nullable=False)
    maker_src = Column(String(44), nullable=False)
    src_blockchain = Column(String(10), nullable=False)
    give_token_address = Column(String(44), nullable=False)
    give_amount = Column(Numeric(30, 0), nullable=False)
    dst_blockchain = Column(String(10), nullable=False)
    take_token_address = Column(String(44), nullable=False)
    take_amount = Column(Numeric(50, 0), nullable=False)
    receiver_dst = Column(String(44), nullable=False)
    give_patch_authority_src = Column(String(44), nullable=False)
    order_authority_address_dst = Column(String(44), nullable=False)
    allowed_taker_dst = Column(String(44), nullable=True)
    allowed_cancel_beneficiary_src = Column(String(44), nullable=True)
    external_call = Column(String, nullable=True)
    order_id = Column(String(66), nullable=False, primary_key=True)
    sender = Column(String(44), nullable=True)
    unlock_authority = Column(String(44), nullable=False)
    taker = Column(String(44), nullable=True)
    middle_dst_token = Column(String(44), nullable=True)
    middle_dst_amount = Column(Numeric(50, 0), nullable=True)


class DeBridgeClaimedUnlock(Base):
    __tablename__ = "debridge_claimed_unlock"

    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(88), nullable=False)
    address = Column(String(128), nullable=True)
    order_id = Column(String(66), nullable=False, primary_key=True)
    beneficiary = Column(String(44), nullable=False)
    give_amount = Column(Numeric(30, 0), nullable=False)
    give_token_address = Column(String(44), nullable=False)
    fee = Column(Numeric(30, 0), nullable=True)


class DeBridgeBlockchainTransactions(BlockchainTransaction):
    __tablename__ = "debridge_blockchain_transactions"


class DeBridgeCrossChainTransactions(Base):
    __tablename__ = "debridge_cross_chain_transactions"

    src_blockchain = Column(String(10), nullable=False)
    src_transaction_hash = Column(String(88), nullable=False)
    src_from_address = Column(String(44), nullable=False)
    src_to_address = Column(String(44), nullable=False)
    src_fee = Column(Numeric(30, 0), nullable=False)
    src_value = Column(Numeric(30, 0), nullable=True)
    src_fee_usd = Column(Float, nullable=True)
    src_timestamp = Column(BigInteger, nullable=False)
    dst_blockchain = Column(String(10), nullable=False)
    dst_transaction_hash = Column(String(88), nullable=False)
    dst_from_address = Column(String(44), nullable=False)
    dst_to_address = Column(String(44), nullable=False)
    dst_fee = Column(Numeric(30, 0), nullable=False)
    dst_value = Column(Numeric(30, 0), nullable=True)
    dst_fee_usd = Column(Float, nullable=True)
    dst_timestamp = Column(BigInteger, nullable=False)
    refund_blockchain = Column(String(10), nullable=True)
    refund_transaction_hash = Column(String(88), nullable=True)
    refund_from_address = Column(String(44), nullable=True)
    refund_to_address = Column(String(44), nullable=True)
    refund_fee = Column(Numeric(30, 0), nullable=True)
    refund_value = Column(Numeric(50, 0), nullable=True)
    refund_fee_usd = Column(Float, nullable=True)
    refund_timestamp = Column(BigInteger, nullable=True)
    intent_id = Column(String(64), nullable=False, primary_key=True)
    depositor = Column(String(44), nullable=False)
    recipient = Column(String(44), nullable=False)
    src_contract_address = Column(String(44), nullable=True)
    dst_contract_address = Column(String(44), nullable=True)
    input_amount = Column(Numeric(50, 0), nullable=True)
    input_amount_usd = Column(Float, nullable=True)
    middle_src_token = Column(String(44), nullable=True)
    middle_src_amount = Column(Numeric(50, 0), nullable=True)
    middle_src_amount_usd = Column(Float, nullable=True)
    middle_dst_token = Column(String(44), nullable=True)
    middle_dst_amount = Column(Numeric(50, 0), nullable=True)
    middle_dst_amount_usd = Column(Float, nullable=True)
    output_amount = Column(Numeric(50, 0), nullable=False)
    output_amount_usd = Column(Float, nullable=True)
    refund_amount = Column(Numeric(50, 0), nullable=True)
    refund_amount_usd = Column(Float, nullable=True)
    refund_token = Column(String(44), nullable=True)
    native_fix_fee = Column(Numeric(30, 0), nullable=False)
    native_fix_fee_usd = Column(Float, nullable=True)
    percent_fee = Column(Numeric(30, 0), nullable=False)
    percent_fee_usd = Column(Float, nullable=True)
