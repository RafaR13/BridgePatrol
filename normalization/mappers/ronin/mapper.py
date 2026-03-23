from normalization.event_types import NormalizedEventType
from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from normalization.common.utils import to_json, to_str


def map_deposit_requested(row, tx_ctx):
    return NormalizedEvent(
        bridge="ronin",
        blockchain=row.blockchain,
        raw_table="ronin_deposit_requested",
        raw_pk=str(row.deposit_id),
        transaction_hash=row.transaction_hash,
        block_number=tx_ctx.block_number if tx_ctx else None,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        event_type=NormalizedEventType.LOCK_REQUESTED,
        correlation_id=str(row.deposit_id),
        correlation_type="deposit_id",
        src_blockchain=row.blockchain,
        dst_blockchain=row.dst_blockchain,
        actor_from=row.depositor,
        actor_to=row.recipient,
        token_in=row.input_token,
        token_out=row.output_token,
        amount_in=row.amount,
        amount_out=row.amount,
        contract_address=tx_ctx.to_address if tx_ctx else None,
        status=str(tx_ctx.status) if tx_ctx else None,
        extra_data=to_json(
            {
                "kind": row.kind,
                "token_standard": row.token_standard,
            }
        ),
    )


def map_token_deposited(row, tx_ctx):
    return NormalizedEvent(bridge="ronin",blockchain=row.blockchain,
        raw_table="ronin_token_deposited",
        raw_pk=str(row.deposit_id),
        transaction_hash=row.transaction_hash,
        block_number=tx_ctx.block_number if tx_ctx else None,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        event_type=NormalizedEventType.MINT_EXECUTED,
        correlation_id=str(row.deposit_id),
        correlation_type="deposit_id",
        src_blockchain=row.src_blockchain,
        dst_blockchain=row.blockchain,
        actor_from=row.depositor,
        actor_to=row.recipient,
        token_in=row.input_token,
        token_out=row.output_token,
        amount_in=row.amount,
        amount_out=row.amount,
        contract_address=tx_ctx.to_address if tx_ctx else None,
        status=str(tx_ctx.status) if tx_ctx else None,
        extra_data=to_json(
            {
                "kind": row.kind,
                "token_standard": row.token_standard,
            }
        ),
    )


def map_withdrawal_requested(row, tx_ctx):
    return NormalizedEvent(
        bridge="ronin",
        blockchain=row.blockchain,
        raw_table="ronin_withdrawal_requested",
        raw_pk=str(row.withdrawal_id),
        transaction_hash=row.transaction_hash,
        block_number=tx_ctx.block_number if tx_ctx else None,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        event_type=NormalizedEventType.BURN_REQUESTED,
        correlation_id=str(row.withdrawal_id),
        correlation_type="withdrawal_id",
        src_blockchain=row.blockchain,
        dst_blockchain=row.dst_blockchain,
        actor_from=row.withdrawer,
        actor_to=row.recipient,
        token_in=row.input_token,
        token_out=row.output_token,
        amount_in=row.amount,
        amount_out=row.amount,
        contract_address=tx_ctx.to_address if tx_ctx else None,
        status=str(tx_ctx.status) if tx_ctx else None,
        extra_data=to_json(
            {
                "kind": row.kind,
                "token_standard": row.token_standard,
            }
        ),
    )


def map_token_withdrew(row, tx_ctx):
    return NormalizedEvent(
        bridge="ronin",
        blockchain=row.blockchain,
        raw_table="ronin_token_withdrew",
        raw_pk=str(row.withdrawal_id),
        transaction_hash=row.transaction_hash,
        block_number=tx_ctx.block_number if tx_ctx else None,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        event_type=NormalizedEventType.RELEASE_EXECUTED,
        correlation_id=str(row.withdrawal_id),
        correlation_type="withdrawal_id",
        src_blockchain=row.src_blockchain,
        dst_blockchain=row.blockchain,
        actor_from=row.withdrawer,
        actor_to=row.recipient,
        token_in=row.input_token,
        token_out=row.output_token,
        amount_in=row.amount,
        amount_out=row.amount,
        contract_address=tx_ctx.to_address if tx_ctx else None,
        status=str(tx_ctx.status) if tx_ctx else None,
        extra_data=to_json(
            {
                "kind": row.kind,
                "token_standard": row.token_standard,
            }
        ),
    )