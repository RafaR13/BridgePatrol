from normalization.event_types import NormalizedEventType
from db.repository.normalized_event.normalized_event_model import NormalizedEvent
from normalization.common.utils import to_json


def _tx_block_number(tx_ctx):
    return tx_ctx.block_number if tx_ctx else None


def _tx_timestamp(tx_ctx):
    return tx_ctx.timestamp if tx_ctx else None


def _tx_contract(tx_ctx):
    return tx_ctx.to_address if tx_ctx else None


def _tx_status(tx_ctx):
    return str(tx_ctx.status) if tx_ctx else None


def map_tokens_bridging_initiated(row, tx_ctx):
    raw_pk = str(row.id) if getattr(row, "id", None) is not None else row.transaction_hash

    return NormalizedEvent(
        bridge="omnibridge",
        blockchain=row.blockchain,
        raw_table="omnibridge_tokens_bridging_initiated",
        raw_pk=raw_pk,
        transaction_hash=row.transaction_hash,
        block_number=_tx_block_number(tx_ctx),
        timestamp=_tx_timestamp(tx_ctx),
        event_type=NormalizedEventType.BRIDGING_INITIATED,
        correlation_id=row.message_id,
        correlation_type="message_id",
        src_blockchain=row.blockchain,
        dst_blockchain=None,
        actor_from=row.sender,
        actor_to=None,
        token_in=row.token,
        token_out=row.token,
        amount_in=row.value,
        amount_out=row.value,
        contract_address=_tx_contract(tx_ctx),
        status=_tx_status(tx_ctx),
        extra_data=to_json(
            {
                "message_id": row.message_id,
                "sender": row.sender,
                "token": row.token,
                "value": str(row.value) if row.value is not None else None,
            }
        ),
    )


def map_tokens_bridged(row, tx_ctx):
    raw_pk = str(row.id) if getattr(row, "id", None) is not None else row.transaction_hash

    return NormalizedEvent(
        bridge="omnibridge",
        blockchain=row.blockchain,
        raw_table="omnibridge_tokens_bridged",
        raw_pk=raw_pk,
        transaction_hash=row.transaction_hash,
        block_number=_tx_block_number(tx_ctx),
        timestamp=_tx_timestamp(tx_ctx),
        event_type=NormalizedEventType.TOKENS_BRIDGED,
        correlation_id=row.message_id,
        correlation_type="message_id",
        src_blockchain=None,
        dst_blockchain=row.blockchain,
        actor_from=None,
        actor_to=row.recipient,
        token_in=row.token,
        token_out=row.token,
        amount_in=row.value,
        amount_out=row.value,
        contract_address=_tx_contract(tx_ctx),
        status=_tx_status(tx_ctx),
        extra_data=to_json(
            {
                "message_id": row.message_id,
                "recipient": row.recipient,
                "token": row.token,
                "value": str(row.value) if row.value is not None else None,
            }
        ),
    )


def map_relayed_message(row, tx_ctx):
    raw_pk = str(row.id) if getattr(row, "id", None) is not None else row.transaction_hash

    return NormalizedEvent(
        bridge="omnibridge",
        blockchain=row.blockchain,
        raw_table="omnibridge_relayed_message",
        raw_pk=raw_pk,
        transaction_hash=row.transaction_hash,
        block_number=_tx_block_number(tx_ctx),
        timestamp=_tx_timestamp(tx_ctx),
        event_type=NormalizedEventType.RELAYED_MESSAGE,
        correlation_id=row.src_transaction_hash,
        correlation_type="src_transaction_hash",
        src_blockchain=None,
        dst_blockchain=row.blockchain,
        actor_from=None,
        actor_to=row.recipient,
        token_in=None,
        token_out=None,
        amount_in=row.value,
        amount_out=row.value,
        contract_address=_tx_contract(tx_ctx),
        status=_tx_status(tx_ctx),
        extra_data=to_json(
            {
                "recipient": row.recipient,
                "value": str(row.value) if row.value is not None else None,
                "src_transaction_hash": row.src_transaction_hash,
            }
        ),
    )


def map_signed_for_user_request(row, tx_ctx):
    raw_pk = str(row.id) if getattr(row, "id", None) is not None else f"{row.signer}:{row.message_hash}"

    return NormalizedEvent(
        bridge="omnibridge",
        blockchain=row.blockchain,
        raw_table="omnibridge_signed_for_user_request",
        raw_pk=raw_pk,
        transaction_hash=row.transaction_hash,
        block_number=_tx_block_number(tx_ctx),
        timestamp=_tx_timestamp(tx_ctx),
        event_type=NormalizedEventType.SIGNED_FOR_USER_REQUEST,
        correlation_id=row.message_hash,
        correlation_type="message_hash",
        src_blockchain=row.blockchain,
        dst_blockchain=None,
        actor_from=row.signer,
        actor_to=None,
        token_in=None,
        token_out=None,
        amount_in=None,
        amount_out=None,
        contract_address=_tx_contract(tx_ctx),
        status=_tx_status(tx_ctx),
        extra_data=to_json(
            {
                "signer": row.signer,
                "message_hash": row.message_hash,
            }
        ),
    )


def map_signed_for_affirmation(row, tx_ctx):
    raw_pk = str(row.id) if getattr(row, "id", None) is not None else row.transaction_hash
    correlation_id = row.src_transaction_hash if row.src_transaction_hash else row.message_hash
    correlation_type = "src_transaction_hash" if row.src_transaction_hash else "message_hash"

    return NormalizedEvent(
        bridge="omnibridge",
        blockchain=row.blockchain,
        raw_table="omnibridge_signed_for_affirmation",
        raw_pk=raw_pk,
        transaction_hash=row.transaction_hash,
        block_number=_tx_block_number(tx_ctx),
        timestamp=_tx_timestamp(tx_ctx),
        event_type=NormalizedEventType.SIGNED_FOR_AFFIRMATION,
        correlation_id=correlation_id,
        correlation_type=correlation_type,
        src_blockchain=None,
        dst_blockchain=row.blockchain,
        actor_from=row.signer,
        actor_to=None,
        token_in=None,
        token_out=None,
        amount_in=None,
        amount_out=None,
        contract_address=_tx_contract(tx_ctx),
        status=_tx_status(tx_ctx),
        extra_data=to_json(
            {
                "signer": row.signer,
                "message_hash": row.message_hash,
                "src_transaction_hash": row.src_transaction_hash,
            }
        ),
    )


def map_user_request_for_signature(row, tx_ctx):
    raw_pk = str(row.id) if getattr(row, "id", None) is not None else row.transaction_hash
    correlation_id = row.message_id if row.message_id else row.encoded_data_hash
    correlation_type = "message_id" if row.message_id else "encoded_data_hash"

    return NormalizedEvent(
        bridge="omnibridge",
        blockchain=row.blockchain,
        raw_table="omnibridge_user_request_for_signature",
        raw_pk=raw_pk,
        transaction_hash=row.transaction_hash,
        block_number=_tx_block_number(tx_ctx),
        timestamp=_tx_timestamp(tx_ctx),
        event_type=NormalizedEventType.USER_REQUEST_FOR_SIGNATURE,
        correlation_id=correlation_id,
        correlation_type=correlation_type,
        src_blockchain=row.blockchain,
        dst_blockchain=None,
        actor_from=None,
        actor_to=row.recipient,
        token_in=None,
        token_out=None,
        amount_in=row.value,
        amount_out=row.value,
        contract_address=_tx_contract(tx_ctx),
        status=_tx_status(tx_ctx),
        extra_data=to_json(
            {
                "message_id": row.message_id,
                "encoded_data": row.encoded_data,
                "encoded_data_hash": row.encoded_data_hash,
                "recipient": row.recipient,
                "value": str(row.value) if row.value is not None else None,
            }
        ),
    )


def map_affirmation_completed(row, tx_ctx):
    raw_pk = str(row.id) if getattr(row, "id", None) is not None else row.transaction_hash

    return NormalizedEvent(
        bridge="omnibridge",
        blockchain=row.blockchain,
        raw_table="omnibridge_affirmation_completed",
        raw_pk=raw_pk,
        transaction_hash=row.transaction_hash,
        block_number=_tx_block_number(tx_ctx),
        timestamp=_tx_timestamp(tx_ctx),
        event_type=NormalizedEventType.AFFIRMATION_COMPLETED,
        correlation_id=row.src_transaction_hash,
        correlation_type="src_transaction_hash",
        src_blockchain=None,
        dst_blockchain=row.blockchain,
        actor_from=None,
        actor_to=row.recipient,
        token_in=None,
        token_out=None,
        amount_in=row.value,
        amount_out=row.value,
        contract_address=_tx_contract(tx_ctx),
        status=_tx_status(tx_ctx),
        extra_data=to_json(
            {
                "recipient": row.recipient,
                "value": str(row.value) if row.value is not None else None,
                "src_transaction_hash": row.src_transaction_hash,
            }
        ),
    )


def map_user_request_for_affirmation(row, tx_ctx):
    raw_pk = str(row.id) if getattr(row, "id", None) is not None else row.transaction_hash

    return NormalizedEvent(
        bridge="omnibridge",
        blockchain=row.blockchain,
        raw_table="omnibridge_user_request_for_affirmation",
        raw_pk=raw_pk,
        transaction_hash=row.transaction_hash,
        block_number=_tx_block_number(tx_ctx),
        timestamp=_tx_timestamp(tx_ctx),
        event_type=NormalizedEventType.USER_REQUEST_FOR_AFFIRMATION,
        correlation_id=row.message_id if row.message_id else row.transaction_hash,
        correlation_type="message_id" if row.message_id else "transaction_hash",
        src_blockchain=row.blockchain,
        dst_blockchain=None,
        actor_from=None,
        actor_to=row.recipient,
        token_in=None,
        token_out=None,
        amount_in=row.value,
        amount_out=row.value,
        contract_address=_tx_contract(tx_ctx),
        status=_tx_status(tx_ctx),
        extra_data=to_json(
            {
                "message_id": row.message_id,
                "encoded_data": row.encoded_data,
                "recipient": row.recipient,
                "value": str(row.value) if row.value is not None else None,
            }
        ),
    )


def map_operator_transactions(row, tx_ctx=None):
    raw_pk = str(row.id) if getattr(row, "id", None) is not None else row.transaction_hash

    return NormalizedEvent(
        bridge="omnibridge",
        blockchain=row.blockchain,
        raw_table="omnibridge_operator_transactions",
        raw_pk=raw_pk,
        transaction_hash=row.transaction_hash,
        block_number=None,
        timestamp=row.timestamp if getattr(row, "timestamp", None) is not None else None,
        event_type=NormalizedEventType.OPERATOR_TX,
        correlation_id=row.signer,
        correlation_type="signer",
        src_blockchain=row.blockchain,
        dst_blockchain=None,
        actor_from=row.from_address,
        actor_to=row.to_address,
        token_in=None,
        token_out=None,
        amount_in=None,
        amount_out=None,
        contract_address=row.to_address,
        status=str(row.status) if getattr(row, "status", None) is not None else None,
        extra_data=to_json(
            {
                "signer": row.signer,
                "fee": str(row.fee) if row.fee is not None else None,
                "fee_usd": row.fee_usd,
                "timestamp": row.timestamp,
            }
        ),
    )
