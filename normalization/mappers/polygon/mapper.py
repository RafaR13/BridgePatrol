from normalization.event_types import NormalizedEventType
from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from normalization.common.utils import to_json


def map_locked_token(row, tx_ctx):
    return NormalizedEvent(
        bridge="polygon",
        blockchain=row.blockchain,
        raw_table="polygon_locked_token",
        raw_pk=row.id,
        transaction_hash=row.transaction_hash,
        block_number=tx_ctx.block_number if tx_ctx else None,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        event_type=NormalizedEventType.LOCKED_TOKEN,
        correlation_id=row.transaction_hash,
        src_blockchain=row.blockchain,
        actor_from=row.depositor,
        actor_to=row.deposit_receiver,
        token_in=row.root_token,
        token_out=row.root_token,
        amount_in=row.amount,
        amount_out=row.amount,
        contract_address=tx_ctx.to_address if tx_ctx else None,
        status=str(tx_ctx.status) if tx_ctx else None,
        extra_data=to_json(
            {
                "deposit_receiver": row.deposit_receiver,
                "root_token": row.root_token,
            }
        ),
    )


def map_state_synced(row, tx_ctx):
    return NormalizedEvent(
        bridge="polygon",
        blockchain=row.blockchain,
        raw_table="polygon_state_synced",
        raw_pk=str(row.state_id),
        transaction_hash=row.transaction_hash,
        block_number=tx_ctx.block_number if tx_ctx else None,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        event_type=NormalizedEventType.STATE_SYNCED,
        correlation_id=str(row.state_id),
        actor_from=None,
        actor_to=row.contract_address,
        contract_address=row.contract_address,
        status=str(tx_ctx.status) if tx_ctx else None,
        extra_data=to_json(
            {
                "data": row.data,
            }
        ),
    )


def map_state_committed(row, tx_ctx):
    return NormalizedEvent(
        bridge="polygon",
        blockchain=row.blockchain,
        raw_table="polygon_state_committed",
        raw_pk=str(row.state_id),
        transaction_hash=row.transaction_hash,
        block_number=tx_ctx.block_number if tx_ctx else None,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        event_type=NormalizedEventType.STATE_COMMITTED,
        correlation_id=str(row.state_id),
        actor_from=tx_ctx.from_address if tx_ctx else None,
        actor_to=tx_ctx.to_address if tx_ctx else None,
        contract_address=tx_ctx.to_address if tx_ctx else None,
        status=str(tx_ctx.status) if tx_ctx else None,
        extra_data=to_json(
            {
                "state_id": row.state_id,
                "success": row.success,
            }
        ),
    )


def map_token_deposited(row, tx_ctx):
        return NormalizedEvent(
        bridge="polygon",
        blockchain=row.blockchain,
        raw_table="polygon_token_deposited",
        raw_pk=str(row.id),
        transaction_hash=row.transaction_hash,
        block_number=tx_ctx.block_number if tx_ctx else None,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        event_type=NormalizedEventType.TOKEN_DEPOSITED,
        correlation_id=str(row.transaction_hash),
        dst_blockchain=row.blockchain,
        actor_from=None,
        actor_to=row.user,
        token_in=row.root_token,
        token_out=row.child_token,
        amount_in=row.amount,
        amount_out=row.amount,
        contract_address=tx_ctx.to_address if tx_ctx else None,
        status=str(tx_ctx.status) if tx_ctx else None,
        extra_data=to_json(
            {
                "deposit_count": row.deposit_count,
            }
        ),
    )


def map_pol_withdraw(row, tx_ctx):
        return NormalizedEvent(
        bridge="polygon",
        blockchain=row.blockchain,
        raw_table="polygon_pol_withdraw",
        raw_pk=str(row.id),
        transaction_hash=row.transaction_hash,
        block_number=tx_ctx.block_number if tx_ctx else None,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        event_type=NormalizedEventType.POL_WITHDRAW,
        correlation_id=row.transaction_hash,
        src_blockchain=row.blockchain,
        actor_from=row.from_address,
        actor_to=None,
        token_in=row.token,
        token_out=row.token,
        amount_in=row.amount,
        amount_out=row.amount,
        contract_address=tx_ctx.to_address if tx_ctx else None,
        status=str(tx_ctx.status) if tx_ctx else None,
        extra_data=to_json(
            {
                "input1": row.input1,
                "output1": row.output1,
            }
        ),
    )


def map_bridge_withdraw(row, tx_ctx):
    return NormalizedEvent(
        bridge="polygon",
        blockchain=row.blockchain,
        raw_table="polygon_bridge_withdraw",
        raw_pk=str(row.id),
        transaction_hash=row.transaction_hash,
        block_number=tx_ctx.block_number if tx_ctx else None,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        event_type=NormalizedEventType.BRIDGE_WITHDRAWAL,
        correlation_id=str(row.exit_id),
        actor_from=row.user,
        actor_to=tx_ctx.to_address if tx_ctx else None,
        token_in=row.token,
        token_out=row.token,
        amount_in=row.amount,
        amount_out=row.amount,
        contract_address=tx_ctx.to_address if tx_ctx else None,
        status=str(tx_ctx.status) if tx_ctx else None,
        extra_data=None,
    )


def map_exited_token(row, tx_ctx):
    return NormalizedEvent(
        bridge="polygon",
        blockchain=row.blockchain,
        raw_table="polygon_exited_token",
        raw_pk=str(row.id),
        transaction_hash=row.transaction_hash,
        block_number=tx_ctx.block_number if tx_ctx else None,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        event_type=NormalizedEventType.EXITED_TOKEN,
        correlation_id=row.transaction_hash,
        dst_blockchain=row.blockchain,
        actor_from=None,
        actor_to=row.exitor,
        token_in=row.root_token,
        token_out=row.root_token,
        amount_in=row.amount,
        amount_out=row.amount,
        contract_address=tx_ctx.to_address if tx_ctx else None,
        status=str(tx_ctx.status) if tx_ctx else None,
        extra_data=None,
    )
