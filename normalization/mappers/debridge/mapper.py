from normalization.event_types import NormalizedEventType
from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from normalization.common.utils import to_json


def map_debridge_created_order(row, tx_ctx):
    return NormalizedEvent(
        bridge="debridge",
        blockchain=row.blockchain,
        raw_table="debridge_created_order",
        raw_pk=str(row.id),
        transaction_hash=row.transaction_hash,
        block_number=tx_ctx.block_number if tx_ctx else None,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        event_type=NormalizedEventType.ORDER_CREATED,
        correlation_id=row.order_id,
        src_blockchain=row.src_blockchain,
        dst_blockchain=row.dst_blockchain,
        actor_from=row.maker_src,
        actor_to=row.receiver_dst,
        token_in=row.give_token_address,
        token_out=row.take_token_address,
        amount_in=row.give_amount,
        amount_out=row.take_amount,
        contract_address=tx_ctx.to_address if tx_ctx else None,
        status=str(tx_ctx.status) if tx_ctx else None,
        extra_data=to_json(
            {
                "give_patch_authority_src": row.give_patch_authority_src,
                "order_authority_address_dst": row.order_authority_address_dst,
                "allowed_taker_dst": row.allowed_taker_dst,
                "allowed_cancel_beneficiary_src": row.allowed_cancel_beneficiary_src,
                "external_call": row.external_call,
                "affiliate_fee": row.affiliate_fee,
                "native_fix_fee": str(row.native_fix_fee) if row.native_fix_fee is not None else None,
                "percent_fee": str(row.percent_fee) if row.percent_fee is not None else None,
                "referral_code": row.referral_code,
                "metadata": row._metadata,
                "original_token": row.original_token,
                "original_amount": str(row.original_amount) if row.original_amount is not None else None,
                "nonce": str(row.maker_order_nonce),
            }
        ),
    )


def map_debridge_fulfilled_order(row, tx_ctx):
        return NormalizedEvent(
        bridge="debridge",
        blockchain=row.blockchain,
        raw_table="debridge_fulfilled_order",
        raw_pk=str(row.order_id),
        transaction_hash=row.transaction_hash,
        block_number=tx_ctx.block_number if tx_ctx else None,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        event_type=NormalizedEventType.ORDER_FULFILLED,
        correlation_id=row.order_id,
        src_blockchain=row.src_blockchain,
        dst_blockchain=row.dst_blockchain,
        actor_from=row.sender,
        actor_to=row.receiver_dst,
        token_in=row.give_token_address,
        token_out=row.take_token_address,
        amount_in=row.give_amount,
        amount_out=row.take_amount,
        contract_address=tx_ctx.to_address if tx_ctx else None,
        status=str(tx_ctx.status) if tx_ctx else None,
        extra_data=to_json(
            {
                "taker": row.taker,
                "unlock_authority": row.unlock_authority,
                "give_patch_authority_src": row.give_patch_authority_src,
                "order_authority_address_dst": row.order_authority_address_dst,
                "allowed_taker_dst": row.allowed_taker_dst,
                "allowed_cancel_beneficiary_src": row.allowed_cancel_beneficiary_src,
                "external_call": row.external_call,
                "middle_dst_token": row.middle_dst_token,
                "middle_dst_amount": str(row.middle_dst_amount) if row.middle_dst_amount is not None else None,
                "nonce": str(row.maker_order_nonce),
            }
        ),
    )


def map_debridge_claimed_unlock(row, tx_ctx):
    return NormalizedEvent(
        bridge="debridge",
        blockchain=row.blockchain,
        raw_table="debridge_claimed_unlock",
        raw_pk=str(row.order_id),
        transaction_hash=row.transaction_hash,
        block_number=tx_ctx.block_number if tx_ctx else None,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        event_type=NormalizedEventType.CLAIMED_UNLOCK,
        correlation_id=row.order_id,
        src_blockchain=None,
        dst_blockchain=row.blockchain,
        actor_from=None,
        actor_to=row.beneficiary,
        token_in=row.give_token_address,
        token_out=row.give_token_address,
        amount_in=row.give_amount,
        amount_out=row.give_amount,
        contract_address=tx_ctx.to_address if tx_ctx else None,
        status=str(tx_ctx.status) if tx_ctx else None,
        extra_data=to_json(
            {
                "fee": str(row.fee) if row.fee is not None else None,
            }
        ),
    )
