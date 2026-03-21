from normalization.event_types import NormalizedEventType
from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from normalization.common.utils import to_json, to_str


def map_filled_relay(row, tx_ctx):
    return NormalizedEvent(
        bridge="across",
        blockchain=row.blockchain,
        raw_table="across_filled_relay",
        raw_pk=str(row.deposit_id),
        transaction_hash=row.transaction_hash,
        block_number=tx_ctx.block_number if tx_ctx else None,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        event_type=NormalizedEventType.FILL_EXECUTED,
        correlation_id=str(row.deposit_id),
        correlation_type="deposit_id",
        src_blockchain=row.src_chain,
        dst_blockchain=row.blockchain,
        actor_from=row.depositor,
        actor_to=row.recipient,
        relayer=row.relayer,
        token_in=row.input_token,
        token_out=row.output_token,
        amount_in=row.input_amount,
        amount_out=row.output_amount,
        message_hash=to_str(row.message_hash),
        contract_address=tx_ctx.to_address if tx_ctx else None,
        status=str(tx_ctx.status) if tx_ctx else None,
        extra_data=to_json(
            {
                "repayment_chain": row.repayment_chain,
                "fill_deadline": row.fill_deadline,
                "exclusivity_deadline": row.exclusivity_deadline,
                "exclusive_relayer": row.exclusive_relayer,
                "updated_recipient": row.updated_recipient,
                "updated_message_hash": row.updated_message_hash,
                "updated_output_amount": row.updated_output_amount,
                "fill_type": row.fill_type,
            }
        ),
    )