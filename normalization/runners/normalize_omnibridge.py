from normalization.source_models.omnibridge import (
    OmnibridgeTokensBridgingInitiated,
    OmnibridgeTokensBridged,
    OmnibridgeRelayedMessage,
    OmnibridgeSignedForUserRequest,
    OmnibridgeSignedForAffirmation,
    OmnibridgeUserRequestForSignature,
    OmnibridgeAffirmationCompleted,
    OmnibridgeUserRequestForAffirmation
)

from normalization.mappers.omnibridge.mapper import (
    map_tokens_bridging_initiated,
    map_tokens_bridged,
    map_relayed_message,
    map_signed_for_user_request,
    map_signed_for_affirmation,
    map_user_request_for_signature,
    map_affirmation_completed,
    map_user_request_for_affirmation
)
from .runner import normalize

def normalize_omnibridge():
    jobs = [
        (
            OmnibridgeTokensBridgingInitiated,
            "omnibridge_tokens_bridging_initiated",
            lambda row: str(row.message_id),
            map_tokens_bridging_initiated,
        ),
        (
            OmnibridgeTokensBridged,
            "omnibridge_tokens_bridged",
            lambda row: str(row.message_id),
            map_tokens_bridged,
        ),
        (
            OmnibridgeRelayedMessage,
            "omnibridge_relayed_message",
            lambda row: str(row.src_transaction_hash),
            map_relayed_message,
        ),
        (
            OmnibridgeSignedForUserRequest,
            "omnibridge_signed_for_user_request",
            lambda row: f"{row.signer}:{row.message_hash}",
            map_signed_for_user_request,
        ),
        (
            OmnibridgeSignedForAffirmation,
            "omnibridge_signed_for_affirmation",
            lambda row: f"{row.signer}:{row.message_hash or row.src_transaction_hash}",
            map_signed_for_affirmation,
        ),
        (
            OmnibridgeUserRequestForSignature,
            "omnibridge_user_request_for_signature",
            lambda row: str(row.message_id) if row.message_id else str(row.encoded_data_hash),
            map_user_request_for_signature,
        ),
        (
            OmnibridgeAffirmationCompleted,
            "omnibridge_affirmation_completed",
            lambda row: str(row.src_transaction_hash),
            map_affirmation_completed,
        ),
        (
            OmnibridgeUserRequestForAffirmation,
            "omnibridge_user_request_for_affirmation",
            lambda row: str(row.message_id) if row.message_id else str(row.transaction_hash),
            map_user_request_for_affirmation,
        )
    ]
    normalize(bridge="omnibridge", jobs=jobs)