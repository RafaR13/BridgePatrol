from normalization.event_types import NormalizedEventType
from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from normalization.common.utils import to_json


def map_relayer_refund(row, tx_ctx):
    raw_pk = f"{row.transaction_hash}:{row.root_bundle_id}:{row.refund_address}"

    return NormalizedEvent(
        bridge="across",
        blockchain=row.blockchain,
        raw_table="across_relayer_refund",
        raw_pk=raw_pk,
        transaction_hash=row.transaction_hash,
        block_number=tx_ctx.block_number if tx_ctx else None,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        event_type=NormalizedEventType.REFUND_EXECUTED,
        correlation_id=str(row.root_bundle_id),
        correlation_type="root_bundle_id",
        actor_from=row.caller,
        actor_to=row.refund_address,
        token_in=row.l2_token_address,
        token_out=row.l2_token_address,
        amount_in=row.amount_to_return,
        amount_out=row.refund_amount,
        contract_address=tx_ctx.to_address if tx_ctx else None,
        status=str(tx_ctx.status) if tx_ctx else None,
        extra_data=to_json(
            {
                "root_bundle_id": row.root_bundle_id,
                "amount_to_return": row.amount_to_return,
            }
        ),
    )