from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from normalization.common.utils import event_contract_address, to_json
from normalization.event_types import NormalizedEventType


def _nomad_message_correlation(src_blockchain, dst_blockchain, nonce):
    if src_blockchain is None or dst_blockchain is None or nonce is None:
        return None
    return f"{src_blockchain}:{dst_blockchain}:{nonce}"


def map_nomad_router_send(row, tx_ctx, cctx_id=None):
    return NormalizedEvent(
        bridge="nomad",
        blockchain=row.blockchain,
        raw_table="nomad_router_send",
        raw_pk=str(row.id),
        transaction_hash=row.transaction_hash,
        cctx_id=cctx_id,
        block_number=tx_ctx.block_number if tx_ctx else None,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        event_type=NormalizedEventType.NOMAD_ROUTER_SEND,
        correlation_id=f"{row.blockchain}:{row.dst_blockchain}:{row.transaction_hash}",
        src_blockchain=row.blockchain,
        dst_blockchain=row.dst_blockchain,
        actor_from=row.depositor,
        actor_to=row.recipient,
        token_in=row.input_token,
        amount_in=row.amount,
        amount_out=row.amount,
        contract_address=event_contract_address(row, tx_ctx),
        status=str(tx_ctx.status) if tx_ctx else None,
        extra_data=to_json(
            {
                "to_hook": row.to_hook,
                "fast_liquidity_enabled": row.fast_liquidity_enabled,
            }
        ),
    )


def map_nomad_router_receive(row, tx_ctx, cctx_id=None):
    return NormalizedEvent(
        bridge="nomad",
        blockchain=row.blockchain,
        raw_table="nomad_router_receive",
        raw_pk=str(row.id),
        transaction_hash=row.transaction_hash,
        cctx_id=cctx_id,
        block_number=tx_ctx.block_number if tx_ctx else None,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        event_type=NormalizedEventType.NOMAD_ROUTER_RECEIVE,
        correlation_id=_nomad_message_correlation(row.src_blockchain, row.blockchain, row.nonce),
        src_blockchain=row.src_blockchain,
        dst_blockchain=row.blockchain,
        actor_to=row.recipient,
        relayer=row.liquidity_provider,
        token_out=row.output_token,
        amount_out=row.amount,
        nonce=str(row.nonce),
        contract_address=event_contract_address(row, tx_ctx),
        status=str(tx_ctx.status) if tx_ctx else None,
    )


def map_nomad_eth_helper_send(row, tx_ctx, cctx_id=None):
    return NormalizedEvent(
        bridge="nomad",
        blockchain=row.blockchain,
        raw_table="nomad_eth_helper_send",
        raw_pk=str(row.id),
        transaction_hash=row.transaction_hash,
        cctx_id=cctx_id,
        block_number=tx_ctx.block_number if tx_ctx else None,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        event_type=NormalizedEventType.NOMAD_ETH_HELPER_SEND,
        correlation_id=row.transaction_hash,
        src_blockchain=row.blockchain,
        actor_from=row.from_address,
        contract_address=event_contract_address(row, tx_ctx),
        status=str(tx_ctx.status) if tx_ctx else None,
    )


def map_nomad_replica_process(row, tx_ctx, cctx_id=None):
    return NormalizedEvent(
        bridge="nomad",
        blockchain=row.blockchain,
        raw_table="nomad_replica_process",
        raw_pk=str(row.id),
        transaction_hash=row.transaction_hash,
        cctx_id=cctx_id,
        block_number=tx_ctx.block_number if tx_ctx else None,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        event_type=NormalizedEventType.NOMAD_REPLICA_PROCESS,
        correlation_id=row.message_hash,
        dst_blockchain=row.blockchain,
        message_hash=row.message_hash,
        contract_address=event_contract_address(row, tx_ctx),
        status=str(tx_ctx.status) if tx_ctx else None,
        extra_data=to_json(
            {
                "success": row.success,
                "return_data": row.return_data,
            }
        ),
    )


def map_nomad_home_dispatch(row, tx_ctx, cctx_id=None):
    return NormalizedEvent(
        bridge="nomad",
        blockchain=row.blockchain,
        raw_table="nomad_home_dispatch",
        raw_pk=str(row.id),
        transaction_hash=row.transaction_hash,
        cctx_id=cctx_id,
        block_number=tx_ctx.block_number if tx_ctx else None,
        timestamp=tx_ctx.timestamp if tx_ctx else None,
        event_type=NormalizedEventType.NOMAD_HOME_DISPATCH,
        correlation_id=_nomad_message_correlation(row.src_blockchain, row.dst_blockchain, row.nonce),
        src_blockchain=row.src_blockchain,
        dst_blockchain=row.dst_blockchain,
        actor_from=tx_ctx.from_address if tx_ctx else None,
        actor_to=row.recipient,
        token_in=row.token_address,
        token_out=row.token_address,
        amount_in=row.amount,
        amount_out=row.amount,
        nonce=str(row.nonce),
        message_id=row.message_hash,
        message_hash=row.message_hash,
        payload_hash=row.details_hash,
        contract_address=event_contract_address(row, tx_ctx),
        status=str(tx_ctx.status) if tx_ctx else None,
        extra_data=to_json(
            {
                "leaf_index": row.leaf_index,
                "committed_root": row.committed_root,
                "src_router": row.src_router,
                "dst_router": row.dst_router,
                "token_blockchain": row.token_blockchain,
                "action_type": row.action_type,
                "details_hash": row.details_hash,
            }
        ),
    )
