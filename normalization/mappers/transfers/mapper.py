from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from normalization.common.utils import to_json
from normalization.event_types import NormalizedEventType


def map_transfer(row, tx_ctx, cctx_id=None, *, bridge: str, raw_table: str):
    return NormalizedEvent(
        bridge=bridge,
        blockchain=row.blockchain,
        raw_table=raw_table,
        raw_pk=str(row.id),
        transaction_hash=row.transaction_hash,
        cctx_id=cctx_id,
        block_number=row.block_number,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        log_index=row.log_index,
        event_type=NormalizedEventType.TRANSFER,
        correlation_id=cctx_id or row.transaction_hash,
        actor_from=row.from_address,
        actor_to=row.to_address,
        token_in=row.token_address,
        token_out=row.token_address,
        amount_in=row.amount,
        amount_out=row.amount,
        contract_address=row.token_address,
        status=str(tx_ctx.status) if tx_ctx else None,
        extra_data=to_json(
            {
                "trigger_event_topic": row.trigger_event_topic,
                "trigger_contract_address": row.trigger_contract_address,
            }
        ),
    )
