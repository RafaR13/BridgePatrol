from sqlalchemy import BigInteger, Boolean, Column, Float, Integer, Numeric, String

from db.repository.common_models import BlockchainTransaction
from db.database import Base


class MayanSwapAndForwarded(Base):
    __tablename__ = "mayan_swap_and_forwarded"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    # address = Column(String(128), nullable=True)
    token_in = Column(String(42), nullable=False)
    amount_in = Column(Numeric(50, 0), nullable=False)
    swap_protocol = Column(String(42), nullable=False)
    middle_token = Column(String(42), nullable=False)
    middle_amount = Column(Numeric(30, 0), nullable=False)
    mayan_protocol = Column(String(42), nullable=False)
    trader = Column(String(42), nullable=False)
    token_out = Column(String(42), nullable=False)
    min_amount_out = Column(Numeric(30, 0), nullable=False)
    gas_drop = Column(Integer, nullable=True)
    cancel_fee = Column(Integer, nullable=True)
    refund_fee = Column(Integer, nullable=True)
    deadline = Column(BigInteger, nullable=True)
    dst_addr = Column(String(42), nullable=True)
    dst_chain = Column(String(10), nullable=True)
    referrer_addr = Column(String(42), nullable=True)
    referrer_bps = Column(Integer, nullable=True)
    auction_mode = Column(Integer, nullable=True)
    random = Column(String(66), nullable=True)


class MayanForwarded(Base):
    __tablename__ = "mayan_forwarded"

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    # address = Column(String(128), nullable=True)
    token = Column(String(42), nullable=False)
    amount = Column(Numeric(50, 0), nullable=True)
    mayan_protocol = Column(String(42), nullable=False)
    trader = Column(String(42), nullable=False)
    token_out = Column(String(42), nullable=False)
    min_amount_out = Column(Numeric(30, 0), nullable=False)
    gas_drop = Column(Integer, nullable=True)
    cancel_fee = Column(Integer, nullable=True)
    refund_fee = Column(Integer, nullable=True)
    deadline = Column(BigInteger, nullable=True)
    dst_addr = Column(String(42), nullable=True)
    dst_chain = Column(String(10), nullable=True)
    referrer_addr = Column(String(42), nullable=True)
    referrer_bps = Column(Integer, nullable=True)
    auction_mode = Column(Integer, nullable=True)
    random = Column(String(66), nullable=True)


class MayanOrderCreated(Base):
    __tablename__ = "mayan_order_created"

    key = Column(String(64), nullable=False, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    # address = Column(String(128), nullable=True)


class MayanOrderFulfilled(Base):
    __tablename__ = "mayan_order_fulfilled"

    key = Column(String(64), nullable=False, primary_key=True)
    sequence = Column(Integer, nullable=False)
    net_amount = Column(Numeric(50, 0), nullable=False)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    # address = Column(String(128), nullable=True)
    middle_dst_token = Column(String(44), nullable=True)
    middle_dst_amount = Column(Numeric(50, 0), nullable=True)


class MayanOrderUnlocked(Base):
    __tablename__ = "mayan_order_unlocked"

    key = Column(String(64), nullable=False, primary_key=True)
    blockchain = Column(String(10), nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    # address = Column(String(128), nullable=True)


### SOLANA SPECIFIC MODELS ###


class MayanInitOrder(Base):
    __tablename__ = "mayan_init_order"

    order_hash = Column(String(64), primary_key=True, nullable=False)
    signature = Column(String(88), nullable=False)
    trader = Column(String(44), nullable=False)
    relayer = Column(String(44), nullable=False)
    state = Column(String(44), nullable=False)
    state_from_acc = Column(String(44), nullable=False)
    relayer_fee_acc = Column(String(44), nullable=False)
    middle_src_token = Column(String(44), nullable=True)
    fee_manager_program = Column(String(44), nullable=False)
    token_program = Column(String(44), nullable=False)
    system_program = Column(String(44), nullable=False)
    middle_src_amount_min = Column(Numeric(50, 0), nullable=True)
    middle_src_amount = Column(Numeric(50, 0), nullable=True)
    native_input = Column(Boolean, nullable=False)
    fee_submit = Column(Numeric(30, 0), nullable=False)
    addr_dest = Column(String(128), nullable=False)
    chain_dest = Column(String(10), nullable=False)
    token_out = Column(String(128), nullable=False)
    amount_out_min = Column(Numeric(50, 0), nullable=False)
    gas_drop = Column(Numeric(30, 0), nullable=False)
    fee_cancel = Column(Numeric(30, 0), nullable=False)
    fee_refund = Column(Numeric(30, 0), nullable=False)
    deadline = Column(BigInteger, nullable=False)
    addr_ref = Column(String(128), nullable=False)
    fee_rate_ref = Column(Integer, nullable=False)
    fee_rate_mayan = Column(Integer, nullable=False)
    auction_mode = Column(Integer, nullable=False)
    key_rnd = Column(String(128), nullable=False)
    original_src_token = Column(String(44), nullable=False)
    original_src_amount = Column(Numeric(50, 0), nullable=False)
    amm = Column(String(44), nullable=True)


class MayanUnlock(Base):
    __tablename__ = "mayan_unlock"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    signature = Column(String(88), nullable=False)
    vaa_unlock = Column(String(44), nullable=False)
    state = Column(String(44), nullable=False)
    state_from_acc = Column(String(44), nullable=False)
    mint_from = Column(String(44), nullable=False)
    driver = Column(String(44), nullable=False)
    driver_acc = Column(String(44), nullable=False)
    token_program = Column(String(44), nullable=False)
    system_program = Column(String(44), nullable=False)
    amount = Column(Numeric(50, 0), nullable=False)


class MayanFulfillOrder(Base):
    __tablename__ = "mayan_fulfill_order"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    signature = Column(String(88), nullable=False)
    state = Column(String(44), nullable=False)
    driver = Column(String(44), nullable=False)
    state_to_acc = Column(String(44), nullable=False)
    mint_to = Column(String(44), nullable=False)
    dest = Column(String(44), nullable=False)
    system_program = Column(String(44), nullable=False)
    addr_unlocker = Column(String(64), nullable=True)
    amount = Column(Numeric(30, 0), nullable=False)
    middle_dst_token = Column(String(44), nullable=True)
    middle_dst_amount = Column(Numeric(30, 0), nullable=True)
    amm = Column(String(44), nullable=True)


class MayanSettle(Base):
    __tablename__ = "mayan_settle"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    signature = Column(String(88), nullable=False)
    state = Column(String(44), nullable=False)
    state_to_acc = Column(String(44), nullable=False)
    relayer = Column(String(44), nullable=False)
    mint_to = Column(String(44), nullable=False)
    dest = Column(String(44), nullable=False)
    referrer = Column(String(44), nullable=False)
    fee_collector = Column(String(44), nullable=False)
    referrer_fee_acc = Column(String(44), nullable=False)
    mayan_fee_acc = Column(String(44), nullable=False)
    dest_acc = Column(String(44), nullable=False)
    token_program = Column(String(44), nullable=False)
    system_program = Column(String(44), nullable=False)
    associated_token_program = Column(String(44), nullable=False)


class MayanSetAuctionWinner(Base):
    __tablename__ = "mayan_set_auction_winner"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    signature = Column(String(88), nullable=False)
    state = Column(String(44), nullable=False)
    auction = Column(String(44), nullable=False)
    expected_winner = Column(String(64), nullable=False)


class MayanRegisterOrder(Base):
    __tablename__ = "mayan_register_order"

    order_hash = Column(String(64), primary_key=True, nullable=False)
    signature = Column(String(88), nullable=False)
    relayer = Column(String(44), nullable=False)
    state = Column(String(44), nullable=False)
    system_program = Column(String(44), nullable=False)
    trader = Column(String(128), nullable=False)
    chain_source = Column(String(10), nullable=False)
    token_in = Column(String(128), nullable=False)
    addr_dest = Column(String(128), nullable=False)
    chain_dest = Column(String(10), nullable=False)
    token_out = Column(String(128), nullable=False)
    amount_out_min = Column(Numeric(30, 0), nullable=False)
    gas_drop = Column(Numeric(30, 0), nullable=False)
    fee_cancel = Column(Numeric(30, 0), nullable=False)
    fee_refund = Column(Numeric(30, 0), nullable=False)
    deadline = Column(BigInteger, nullable=False)
    addr_ref = Column(String(128), nullable=False)
    fee_rate_ref = Column(Integer, nullable=False)
    fee_rate_mayan = Column(Integer, nullable=False)
    auction_mode = Column(Integer, nullable=False)
    key_rnd = Column(String(128), nullable=False)


class MayanAuctionBid(Base):
    __tablename__ = "mayan_auction_bid"

    signature = Column(String(88), primary_key=True, nullable=False)
    config = Column(String(128), nullable=False)
    driver = Column(String(44), nullable=False)
    auction_state = Column(String(44), nullable=False)
    system_program = Column(String(44), nullable=False)
    trader = Column(String(128), nullable=False)
    chain_source = Column(String(10), nullable=False)
    token_in = Column(String(128), nullable=False)
    addr_dest = Column(String(128), nullable=False)
    chain_dest = Column(String(10), nullable=False)
    token_out = Column(String(128), nullable=False)
    amount_out_min = Column(Numeric(30, 0), nullable=False)
    gas_drop = Column(Numeric(30, 0), nullable=False)
    fee_cancel = Column(Numeric(30, 0), nullable=False)
    fee_refund = Column(Numeric(30, 0), nullable=False)
    deadline = Column(BigInteger, nullable=False)
    addr_ref = Column(String(128), nullable=False)
    fee_rate_ref = Column(Integer, nullable=False)
    fee_rate_mayan = Column(Integer, nullable=False)
    auction_mode = Column(Integer, nullable=False)
    key_rnd = Column(String(128), nullable=False)
    amount_bid = Column(Numeric(30, 0), nullable=False)
    order_hash = Column(String(64), primary_key=True, nullable=False)


class MayanAuctionClose(Base):
    __tablename__ = "mayan_auction_close"

    signature = Column(String(88), nullable=False)
    auction = Column(String(44), primary_key=True, nullable=False)
    initializer = Column(String(44), nullable=False)


class MayanBlockchainTransactions(BlockchainTransaction):
    __tablename__ = "mayan_blockchain_transactions"


class MayanCrossChainTransactions(Base):
    __tablename__ = "mayan_cross_chain_transactions"

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
    refund_value = Column(Numeric(30, 0), nullable=True)
    refund_fee_usd = Column(Float, nullable=True)
    refund_timestamp = Column(BigInteger, nullable=True)
    intent_id = Column(String(64), nullable=False, primary_key=True)
    depositor = Column(String(44), nullable=False)
    recipient = Column(String(44), nullable=False)
    src_contract_address = Column(String(44), nullable=False)
    dst_contract_address = Column(String(44), nullable=False)
    input_amount = Column(Numeric(50, 0), nullable=False)
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
    auction_id = Column(String(64), nullable=True)
    auction_first_bid_timestamp = Column(BigInteger, nullable=True)
    auction_last_bid_timestamp = Column(BigInteger, nullable=True)
    auction_number_of_bids = Column(Integer, nullable=True)
    native_fix_fee = Column(Numeric(30, 0), nullable=False)
    native_fix_fee_usd = Column(Float, nullable=True)
    percent_fee = Column(Numeric(30, 0), nullable=False)
    percent_fee_usd = Column(Float, nullable=True)
