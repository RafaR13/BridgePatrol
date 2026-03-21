from normalization.event_types import NormalizedEventType
from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from normalization.common.utils import to_json


def map_funds_deposited(row, tx_ctx):
    return NormalizedEvent(
        bridge="across",
        blockchain=row.blockchain,
        raw_table="across_funds_deposited",
        raw_pk=str(row.deposit_id),
        transaction_hash=row.transaction_hash,
        block_number=tx_ctx.block_number if tx_ctx else None,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        event_type=NormalizedEventType.DEPOSIT_INTENT,
        correlation_id=str(row.deposit_id),
        correlation_type="deposit_id",
        src_blockchain=row.blockchain,
        dst_blockchain=row.destination_chain,
        actor_from=row.depositor,
        actor_to=row.recipient,
        relayer=row.exclusive_relayer,
        token_in=row.input_token,
        token_out=row.output_token,
        amount_in=row.input_amount,
        amount_out=row.output_amount,
        contract_address=tx_ctx.to_address if tx_ctx else None,
        status=str(tx_ctx.status) if tx_ctx else None,
        extra_data=to_json(
            {
                "quote_timestamp": row.quote_timestamp,
                "fill_deadline": row.fill_deadline,
                "exclusivity_deadline": row.exclusivity_deadline,
                "message": row.message,
            }
        ),
    )