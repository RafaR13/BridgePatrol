from normalization.event_types import NormalizedEventType
from db.repository.normalized_event.normalized_event_model import NormalizedEvent


def map_deposit_for_burn(row, tx_ctx):
    return NormalizedEvent(
        bridge="cctp",
        blockchain=row.blockchain,
        raw_table="cctp_deposit_for_burn",
        raw_pk=str(row.id),
        transaction_hash=row.transaction_hash,
        block_number=tx_ctx.block_number if tx_ctx else None,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        event_type=NormalizedEventType.DEPOSIT_FOR_BURN,
        correlation_id=str(row.nonce),
        src_blockchain=row.blockchain,
        dst_blockchain=row.dst_blockchain,
        actor_from=row.depositor,
        actor_to=row.recipient,
        token_in=row.burn_token,
        token_out=row.burn_token,
        amount_in=row.amount,
        amount_out=row.amount,
        contract_address=tx_ctx.to_address if tx_ctx else None,
        status=str(tx_ctx.status) if tx_ctx else None,
        extra_data=None,
    )


def map_message_received(row, tx_ctx):
    return NormalizedEvent(
        bridge="cctp",
        blockchain=row.blockchain,
        raw_table="cctp_message_received",
        raw_pk=str(row.id),
        transaction_hash=row.transaction_hash,
        block_number=tx_ctx.block_number if tx_ctx else None,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        event_type=NormalizedEventType.MESSAGE_RECEIVED,
        correlation_id=str(row.nonce),
        src_blockchain=row.src_blockchain,
        dst_blockchain=row.blockchain,
        actor_from=row.depositor,
        actor_to=row.recipient,
        token_in=row.input_token,
        token_out=row.input_token,
        amount_in=row.amount,
        amount_out=row.amount,
        contract_address=tx_ctx.to_address if tx_ctx else None,
        status=str(tx_ctx.status) if tx_ctx else None,
        extra_data=None,
    )
