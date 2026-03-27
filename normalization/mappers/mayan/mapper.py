from normalization.event_types import NormalizedEventType
from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from normalization.common.utils import to_json


def _tx_block_number(tx_ctx):
    return tx_ctx.block_number if tx_ctx else None


def _tx_timestamp(tx_ctx):
    return tx_ctx.timestamp if tx_ctx else None


def _tx_contract(tx_ctx):
    return tx_ctx.to_address if tx_ctx else None


def _tx_status(tx_ctx):
    return str(tx_ctx.status) if tx_ctx else None


def map_mayan_swap_and_forwarded(row, tx_ctx):
    raw_pk = str(row.id) if getattr(row, "id", None) is not None else row.transaction_hash
    correlation_id = row.random if row.random else row.transaction_hash

    return NormalizedEvent(
        bridge="mayan",
        blockchain=row.blockchain,
        raw_table="mayan_swap_and_forwarded",
        raw_pk=raw_pk,
        transaction_hash=row.transaction_hash,
        block_number=_tx_block_number(tx_ctx),
        timestamp=_tx_timestamp(tx_ctx),
        event_type=NormalizedEventType.SWAP_AND_FORWARDED,
        correlation_id=correlation_id,
        correlation_type="random" if row.random else "transaction_hash",
        src_blockchain=row.blockchain,
        dst_blockchain=row.dst_chain,
        actor_from=row.trader,
        actor_to=row.dst_addr,
        token_in=row.token_in,
        token_out=row.token_out,
        amount_in=row.amount_in,
        amount_out=row.min_amount_out,
        contract_address=_tx_contract(tx_ctx),
        status=_tx_status(tx_ctx),
        extra_data=to_json(
            {
                "swap_protocol": row.swap_protocol,
                "middle_token": row.middle_token,
                "middle_amount": str(row.middle_amount) if row.middle_amount is not None else None,
                "mayan_protocol": row.mayan_protocol,
                "gas_drop": row.gas_drop,
                "cancel_fee": row.cancel_fee,
                "refund_fee": row.refund_fee,
                "deadline": row.deadline,
                "referrer_addr": row.referrer_addr,
                "referrer_bps": row.referrer_bps,
                "auction_mode": row.auction_mode,
                "random": row.random,
            }
        ),
    )


def map_mayan_forwarded(row, tx_ctx):
    raw_pk = str(row.id) if getattr(row, "id", None) is not None else row.transaction_hash
    correlation_id = row.random if row.random else row.transaction_hash

    return NormalizedEvent(
        bridge="mayan",
        blockchain=row.blockchain,
        raw_table="mayan_forwarded",
        raw_pk=raw_pk,
        transaction_hash=row.transaction_hash,
        block_number=_tx_block_number(tx_ctx),
        timestamp=_tx_timestamp(tx_ctx),
        event_type=NormalizedEventType.FORWARDED,
        correlation_id=correlation_id,
        correlation_type="random" if row.random else "transaction_hash",
        src_blockchain=row.blockchain,
        dst_blockchain=row.dst_chain,
        actor_from=row.trader,
        actor_to=row.dst_addr,
        token_in=row.token,
        token_out=row.token_out,
        amount_in=row.amount,
        amount_out=row.min_amount_out,
        contract_address=_tx_contract(tx_ctx),
        status=_tx_status(tx_ctx),
        extra_data=to_json(
            {
                "mayan_protocol": row.mayan_protocol,
                "gas_drop": row.gas_drop,
                "cancel_fee": row.cancel_fee,
                "refund_fee": row.refund_fee,
                "deadline": row.deadline,
                "referrer_addr": row.referrer_addr,
                "referrer_bps": row.referrer_bps,
                "auction_mode": row.auction_mode,
                "random": row.random,
            }
        ),
    )


def map_mayan_order_created(row, tx_ctx):
    return NormalizedEvent(
        bridge="mayan",
        blockchain=row.blockchain,
        raw_table="mayan_order_created",
        raw_pk=row.key,
        transaction_hash=row.transaction_hash,
        block_number=_tx_block_number(tx_ctx),
        timestamp=_tx_timestamp(tx_ctx),
        event_type=NormalizedEventType.ORDER_CREATED,
        correlation_id=row.key,
        correlation_type="order_key",
        src_blockchain=row.blockchain,
        dst_blockchain=None,
        actor_from=None,
        actor_to=None,
        token_in=None,
        token_out=None,
        amount_in=None,
        amount_out=None,
        contract_address=_tx_contract(tx_ctx),
        status=_tx_status(tx_ctx),
        extra_data=to_json({"key": row.key}),
    )


def map_mayan_order_fulfilled(row, tx_ctx):
    return NormalizedEvent(
        bridge="mayan",
        blockchain=row.blockchain,
        raw_table="mayan_order_fulfilled",
        raw_pk=row.key,
        transaction_hash=row.transaction_hash,
        block_number=_tx_block_number(tx_ctx),
        timestamp=_tx_timestamp(tx_ctx),
        event_type=NormalizedEventType.ORDER_FULFILLED,
        correlation_id=row.key,
        correlation_type="order_key",
        src_blockchain=None,
        dst_blockchain=row.blockchain,
        actor_from=None,
        actor_to=None,
        token_in=row.middle_dst_token if row.middle_dst_token else None,
        token_out=row.middle_dst_token if row.middle_dst_token else None,
        amount_in=row.middle_dst_amount if row.middle_dst_amount is not None else row.net_amount,
        amount_out=row.net_amount,
        contract_address=_tx_contract(tx_ctx),
        status=_tx_status(tx_ctx),
        extra_data=to_json(
            {
                "key": row.key,
                "sequence": row.sequence,
                "net_amount": str(row.net_amount) if row.net_amount is not None else None,
                "middle_dst_token": row.middle_dst_token,
                "middle_dst_amount": str(row.middle_dst_amount) if row.middle_dst_amount is not None else None,
            }
        ),
    )


def map_mayan_order_unlocked(row, tx_ctx):
    return NormalizedEvent(
        bridge="mayan",
        blockchain=row.blockchain,
        raw_table="mayan_order_unlocked",
        raw_pk=row.key,
        transaction_hash=row.transaction_hash,
        block_number=_tx_block_number(tx_ctx),
        timestamp=_tx_timestamp(tx_ctx),
        event_type=NormalizedEventType.UNLOCK_CLAIMED,
        correlation_id=row.key,
        correlation_type="order_key",
        src_blockchain=None,
        dst_blockchain=row.blockchain,
        actor_from=None,
        actor_to=None,
        token_in=None,
        token_out=None,
        amount_in=None,
        amount_out=None,
        contract_address=_tx_contract(tx_ctx),
        status=_tx_status(tx_ctx),
        extra_data=to_json({"key": row.key}),
    )


def map_mayan_init_order(row, tx_ctx):
    return NormalizedEvent(
        bridge="mayan",
        blockchain="solana",
        raw_table="mayan_init_order",
        raw_pk=row.order_hash,
        transaction_hash=row.signature,
        block_number=_tx_block_number(tx_ctx),
        timestamp=_tx_timestamp(tx_ctx),
        event_type=NormalizedEventType.INIT_ORDER,
        correlation_id=row.order_hash,
        correlation_type="order_hash",
        src_blockchain="solana",
        dst_blockchain=row.chain_dest,
        actor_from=row.trader,
        actor_to=row.addr_dest,
        token_in=row.original_src_token,
        token_out=row.token_out,
        amount_in=row.original_src_amount,
        amount_out=row.amount_out_min,
        contract_address=row.state,
        status=_tx_status(tx_ctx),
        extra_data=to_json(
            {
                "signature": row.signature,
                "relayer": row.relayer,
                "state": row.state,
                "state_from_acc": row.state_from_acc,
                "relayer_fee_acc": row.relayer_fee_acc,
                "middle_src_token": row.middle_src_token,
                "middle_src_amount_min": str(row.middle_src_amount_min) if row.middle_src_amount_min is not None else None,
                "middle_src_amount": str(row.middle_src_amount) if row.middle_src_amount is not None else None,
                "native_input": row.native_input,
                "fee_submit": str(row.fee_submit) if row.fee_submit is not None else None,
                "gas_drop": str(row.gas_drop) if row.gas_drop is not None else None,
                "fee_cancel": str(row.fee_cancel) if row.fee_cancel is not None else None,
                "fee_refund": str(row.fee_refund) if row.fee_refund is not None else None,
                "deadline": row.deadline,
                "addr_ref": row.addr_ref,
                "fee_rate_ref": row.fee_rate_ref,
                "fee_rate_mayan": row.fee_rate_mayan,
                "auction_mode": row.auction_mode,
                "key_rnd": row.key_rnd,
                "amm": row.amm,
            }
        ),
    )


def map_mayan_register_order(row, tx_ctx):
    return NormalizedEvent(
        bridge="mayan",
        blockchain="solana",
        raw_table="mayan_register_order",
        raw_pk=row.order_hash,
        transaction_hash=row.signature,
        block_number=_tx_block_number(tx_ctx),
        timestamp=_tx_timestamp(tx_ctx),
        event_type=NormalizedEventType.REGISTER_ORDER,
        correlation_id=row.order_hash,
        correlation_type="order_hash",
        src_blockchain=row.chain_source,
        dst_blockchain=row.chain_dest,
        actor_from=row.trader,
        actor_to=row.addr_dest,
        token_in=row.token_in,
        token_out=row.token_out,
        amount_in=None,
        amount_out=row.amount_out_min,
        contract_address=row.state,
        status=_tx_status(tx_ctx),
        extra_data=to_json(
            {
                "signature": row.signature,
                "relayer": row.relayer,
                "system_program": row.system_program,
                "gas_drop": str(row.gas_drop) if row.gas_drop is not None else None,
                "fee_cancel": str(row.fee_cancel) if row.fee_cancel is not None else None,
                "fee_refund": str(row.fee_refund) if row.fee_refund is not None else None,
                "deadline": row.deadline,
                "addr_ref": row.addr_ref,
                "fee_rate_ref": row.fee_rate_ref,
                "fee_rate_mayan": row.fee_rate_mayan,
                "auction_mode": row.auction_mode,
                "key_rnd": row.key_rnd,
            }
        ),
    )


def map_mayan_auction_bid(row, tx_ctx):
    return NormalizedEvent(
        bridge="mayan",
        blockchain="solana",
        raw_table="mayan_auction_bid",
        raw_pk=f"{row.order_hash}:{row.signature}",
        transaction_hash=row.signature,
        block_number=_tx_block_number(tx_ctx),
        timestamp=_tx_timestamp(tx_ctx),
        event_type=NormalizedEventType.AUCTION_BID,
        correlation_id=row.order_hash,
        correlation_type="order_hash",
        src_blockchain=row.chain_source,
        dst_blockchain=row.chain_dest,
        actor_from=row.driver,
        actor_to=row.addr_dest,
        token_in=row.token_in,
        token_out=row.token_out,
        amount_in=None,
        amount_out=row.amount_bid,
        contract_address=row.auction_state,
        status=_tx_status(tx_ctx),
        extra_data=to_json(
            {
                "signature": row.signature,
                "config": row.config,
                "auction_state": row.auction_state,
                "trader": row.trader,
                "amount_out_min": str(row.amount_out_min) if row.amount_out_min is not None else None,
                "amount_bid": str(row.amount_bid) if row.amount_bid is not None else None,
                "gas_drop": str(row.gas_drop) if row.gas_drop is not None else None,
                "fee_cancel": str(row.fee_cancel) if row.fee_cancel is not None else None,
                "fee_refund": str(row.fee_refund) if row.fee_refund is not None else None,
                "deadline": row.deadline,
                "addr_ref": row.addr_ref,
                "fee_rate_ref": row.fee_rate_ref,
                "fee_rate_mayan": row.fee_rate_mayan,
                "auction_mode": row.auction_mode,
                "key_rnd": row.key_rnd,
            }
        ),
    )


def map_mayan_set_auction_winner(row, tx_ctx):
    raw_pk = str(row.id) if getattr(row, "id", None) is not None else row.signature

    return NormalizedEvent(
        bridge="mayan",
        blockchain="solana",
        raw_table="mayan_set_auction_winner",
        raw_pk=raw_pk,
        transaction_hash=row.signature,
        block_number=_tx_block_number(tx_ctx),
        timestamp=_tx_timestamp(tx_ctx),
        event_type=NormalizedEventType.AUCTION_WINNER_SET,
        correlation_id=row.state,
        correlation_type="state",
        src_blockchain=None,
        dst_blockchain=None,
        actor_from=None,
        actor_to=row.expected_winner,
        token_in=None,
        token_out=None,
        amount_in=None,
        amount_out=None,
        contract_address=row.auction,
        status=_tx_status(tx_ctx),
        extra_data=to_json(
            {
                "state": row.state,
                "auction": row.auction,
                "expected_winner": row.expected_winner,
            }
        ),
    )


def map_mayan_auction_close(row, tx_ctx):
    return NormalizedEvent(
        bridge="mayan",
        blockchain="solana",
        raw_table="mayan_auction_close",
        raw_pk=row.auction,
        transaction_hash=row.signature,
        block_number=_tx_block_number(tx_ctx),
        timestamp=_tx_timestamp(tx_ctx),
        event_type=NormalizedEventType.AUCTION_CLOSED,
        correlation_id=row.auction,
        correlation_type="auction",
        src_blockchain=None,
        dst_blockchain=None,
        actor_from=row.initializer,
        actor_to=None,
        token_in=None,
        token_out=None,
        amount_in=None,
        amount_out=None,
        contract_address=row.auction,
        status=_tx_status(tx_ctx),
        extra_data=to_json(
            {
                "auction": row.auction,
                "initializer": row.initializer,
            }
        ),
    )


def map_mayan_fulfill_order(row, tx_ctx):
    raw_pk = str(row.id) if getattr(row, "id", None) is not None else row.signature

    return NormalizedEvent(
        bridge="mayan",
        blockchain="solana",
        raw_table="mayan_fulfill_order",
        raw_pk=raw_pk,
        transaction_hash=row.signature,
        block_number=_tx_block_number(tx_ctx),
        timestamp=_tx_timestamp(tx_ctx),
        event_type=NormalizedEventType.INTENT_FULFILLED,
        correlation_id=row.state,
        correlation_type="state",
        src_blockchain=None,
        dst_blockchain="solana",
        actor_from=row.driver,
        actor_to=row.dest,
        token_in=row.middle_dst_token if row.middle_dst_token else row.mint_to,
        token_out=row.mint_to,
        amount_in=row.middle_dst_amount if row.middle_dst_amount is not None else row.amount,
        amount_out=row.amount,
        contract_address=row.state,
        status=_tx_status(tx_ctx),
        extra_data=to_json(
            {
                "state_to_acc": row.state_to_acc,
                "addr_unlocker": row.addr_unlocker,
                "middle_dst_token": row.middle_dst_token,
                "middle_dst_amount": str(row.middle_dst_amount) if row.middle_dst_amount is not None else None,
                "amm": row.amm,
            }
        ),
    )


def map_mayan_unlock(row, tx_ctx):
    raw_pk = str(row.id) if getattr(row, "id", None) is not None else row.signature

    return NormalizedEvent(
        bridge="mayan",
        blockchain="solana",
        raw_table="mayan_unlock",
        raw_pk=raw_pk,
        transaction_hash=row.signature,
        block_number=_tx_block_number(tx_ctx),
        timestamp=_tx_timestamp(tx_ctx),
        event_type=NormalizedEventType.UNLOCK_CLAIMED,
        correlation_id=row.state,
        correlation_type="state",
        src_blockchain=None,
        dst_blockchain="solana",
        actor_from=row.driver,
        actor_to=row.driver_acc,
        token_in=row.mint_from,
        token_out=row.mint_from,
        amount_in=row.amount,
        amount_out=row.amount,
        contract_address=row.state,
        status=_tx_status(tx_ctx),
        extra_data=to_json(
            {
                "vaa_unlock": row.vaa_unlock,
                "state_from_acc": row.state_from_acc,
                "driver_acc": row.driver_acc,
                "token_program": row.token_program,
                "system_program": row.system_program,
            }
        ),
    )


def map_mayan_settle(row, tx_ctx):
    raw_pk = str(row.id) if getattr(row, "id", None) is not None else row.signature

    return NormalizedEvent(
        bridge="mayan",
        blockchain="solana",
        raw_table="mayan_settle",
        raw_pk=raw_pk,
        transaction_hash=row.signature,
        block_number=_tx_block_number(tx_ctx),
        timestamp=_tx_timestamp(tx_ctx),
        event_type=NormalizedEventType.SETTLED,
        correlation_id=row.state,
        correlation_type="state",
        src_blockchain=None,
        dst_blockchain="solana",
        actor_from=row.relayer,
        actor_to=row.dest,
        token_in=row.mint_to,
        token_out=row.mint_to,
        amount_in=None,
        amount_out=None,
        contract_address=row.state,
        status=_tx_status(tx_ctx),
        extra_data=to_json(
            {
                "state_to_acc": row.state_to_acc,
                "referrer": row.referrer,
                "fee_collector": row.fee_collector,
                "referrer_fee_acc": row.referrer_fee_acc,
                "mayan_fee_acc": row.mayan_fee_acc,
                "dest_acc": row.dest_acc,
                "token_program": row.token_program,
                "system_program": row.system_program,
                "associated_token_program": row.associated_token_program,
            }
        ),
    )
