from normalization.event_types import NormalizedEventType
from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from normalization.common.utils import event_contract_address, to_json


def _ccip_correlation_id(message_id, sequence_number):
    if message_id is None or sequence_number is None:
        return None
    return f"{message_id}|{sequence_number}"


def map_ccip_send_requested(row, tx_ctx, cctx_id=None):
    return NormalizedEvent(
        bridge="ccip",
        blockchain=row.blockchain,
        raw_table="ccip_send_requested",
        raw_pk=str(row.id),
        transaction_hash=row.transaction_hash,
        cctx_id=cctx_id,
        block_number=tx_ctx.block_number if tx_ctx else None,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        event_type=NormalizedEventType.MESSAGE_SENT,
        correlation_id=_ccip_correlation_id(row.message_id, row.sequence_number),
        src_blockchain=row.blockchain,
        dst_blockchain=None,
        actor_from=row.sender,
        actor_to=row.receiver,
        token_in=row.input_token,
        token_out=row.output_token,
        amount_in=row.amount,
        amount_out=row.amount,
        nonce=str(row.nonce),
        message_id=row.message_id,
        contract_address=event_contract_address(row, tx_ctx),
        status=str(tx_ctx.status) if tx_ctx else None,
        extra_data=to_json(
            {
                "sequence_number": row.sequence_number,
                "gas_limit": row.gas_limit,
                "strict": row.strict,
                "fee_token": row.fee_token,
                "fee_token_amount": row.fee_token_amount,
            }
        ),
    )


def map_ccip_execution_state_changed(row, tx_ctx, cctx_id=None):
    return NormalizedEvent(
        bridge="ccip",
        blockchain=row.blockchain,
        raw_table="ccip_execution_state_changed",
        raw_pk=str(row.id),
        transaction_hash=row.transaction_hash,
        cctx_id=cctx_id,
        block_number=tx_ctx.block_number if tx_ctx else None,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        event_type=NormalizedEventType.MESSAGE_EXECUTION_STATE_CHANGED,
        correlation_id=_ccip_correlation_id(row.message_id, row.sequence_number),
        src_blockchain=None,
        dst_blockchain=row.blockchain,
        actor_from=None,
        actor_to=None,
        token_in=None,
        token_out=None,
        amount_in=None,
        amount_out=None,
        nonce=None,
        message_id=row.message_id,
        contract_address=event_contract_address(row, tx_ctx),
        status=str(tx_ctx.status) if tx_ctx else None,
        extra_data=to_json(
            {
                "sequence_number": row.sequence_number,
                "state": row.state,
                "return_data": row.return_data,
            }
        ),
    )
