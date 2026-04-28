from dataclasses import dataclass
from typing import Callable

from db.repository.bridge_tables.across import (
    AcrossFilledRelay,
    AcrossFundsDeposited,
    AcrossRelayerRefund,
)
from db.repository.bridge_tables.ccip import (
    CCIPExecutionStateChanged,
    CCIPSendRequested,
)
from db.repository.bridge_tables.cctp import (
    CCTPDepositForBurn,
    CCTPMessageReceived,
)
from db.repository.bridge_tables.debridge import (
    DeBridgeClaimedUnlock,
    DeBridgeCreatedOrder,
    DeBridgeFulfilledOrder,
)
from db.repository.bridge_tables.omnibridge import (
    OmnibridgeAffirmationCompleted,
    OmnibridgeRelayedMessage,
    OmnibridgeSignedForAffirmation,
    OmnibridgeSignedForUserRequest,
    OmnibridgeTokensBridged,
    OmnibridgeTokensBridgingInitiated,
    OmnibridgeUserRequestForAffirmation,
    OmnibridgeUserRequestForSignature,
)
from db.repository.bridge_tables.polygon import (
    PolygonBridgeWithdraw,
    PolygonExitedToken,
    PolygonLockedToken,
    PolygonPOLWithdraw,
    PolygonStateCommitted,
    PolygonStateSynced,
    PolygonTokenDeposited,
)
from db.repository.bridge_tables.ronin import (
    RoninDepositRequested,
    RoninTokenDeposited,
    RoninTokenWithdrew,
    RoninWithdrawalRequested,
)
from normalization.mappers.across.mapper import (
    map_filled_relay,
    map_funds_deposited,
    map_relayer_refund,
)
from normalization.mappers.ccip.mapper import (
    map_ccip_execution_state_changed,
    map_ccip_send_requested,
)
from normalization.mappers.cctp.mapper import (
    map_deposit_for_burn,
    map_message_received,
)
from normalization.mappers.debridge.mapper import (
    map_debridge_claimed_unlock,
    map_debridge_created_order,
    map_debridge_fulfilled_order,
)
from normalization.mappers.omnibridge.mapper import (
    map_affirmation_completed,
    map_relayed_message,
    map_signed_for_affirmation,
    map_signed_for_user_request,
    map_tokens_bridged,
    map_tokens_bridging_initiated,
    map_user_request_for_affirmation,
    map_user_request_for_signature,
)
from normalization.mappers.polygon.mapper import (
    map_bridge_withdraw,
    map_exited_token,
    map_locked_token,
    map_pol_withdraw,
    map_state_committed,
    map_state_synced,
    map_token_deposited,
)
from normalization.mappers.ronin.mapper import (
    map_deposit_requested,
    map_token_deposited,
    map_token_withdrew,
    map_withdrawal_requested,
)


@dataclass(frozen=True)
class NormalizationJob:
    model: type
    raw_table: str
    raw_pk_fn: Callable
    mapper_fn: Callable


def _id_or_fallback(*fallback_fields: str) -> Callable:
    def build_pk(row) -> str:
        row_id = getattr(row, "id", None)
        if row_id is not None:
            return str(row_id)
        return ":".join(str(getattr(row, field)) for field in fallback_fields)

    return build_pk


BRIDGE_JOBS: dict[str, tuple[NormalizationJob, ...]] = {
    "across": (
        NormalizationJob(
            AcrossFundsDeposited,
            "across_funds_deposited",
            lambda row: str(row.deposit_id),
            map_funds_deposited,
        ),
        NormalizationJob(
            AcrossFilledRelay,
            "across_filled_relay",
            lambda row: str(row.deposit_id),
            map_filled_relay,
        ),
        NormalizationJob(
            AcrossRelayerRefund,
            "across_relayer_refund",
            lambda row: str(row.id),
            map_relayer_refund,
        ),
    ),
    "ccip": (
        NormalizationJob(
            CCIPSendRequested,
            "ccip_send_requested",
            lambda row: str(row.id),
            map_ccip_send_requested,
        ),
        NormalizationJob(
            CCIPExecutionStateChanged,
            "ccip_execution_state_changed",
            lambda row: str(row.id),
            map_ccip_execution_state_changed,
        ),
    ),
    "cctp": (
        NormalizationJob(
            CCTPDepositForBurn,
            "cctp_deposit_for_burn",
            lambda row: str(row.id) if getattr(row, "id", None) is not None else row.transaction_hash,
            map_deposit_for_burn,
        ),
        NormalizationJob(
            CCTPMessageReceived,
            "cctp_message_received",
            lambda row: str(row.id) if getattr(row, "id", None) is not None else row.transaction_hash,
            map_message_received,
        ),
    ),
    "debridge": (
        NormalizationJob(
            DeBridgeCreatedOrder,
            "debridge_created_order",
            lambda row: str(row.order_id),
            map_debridge_created_order,
        ),
        NormalizationJob(
            DeBridgeFulfilledOrder,
            "debridge_fulfilled_order",
            lambda row: str(row.order_id),
            map_debridge_fulfilled_order,
        ),
        NormalizationJob(
            DeBridgeClaimedUnlock,
            "debridge_claimed_unlock",
            lambda row: str(row.order_id),
            map_debridge_claimed_unlock,
        ),
    ),
    "mayan": (),
    "omnibridge": (
        NormalizationJob(
            OmnibridgeTokensBridgingInitiated,
            "omnibridge_tokens_bridging_initiated",
            lambda row: str(row.message_id),
            map_tokens_bridging_initiated,
        ),
        NormalizationJob(
            OmnibridgeTokensBridged,
            "omnibridge_tokens_bridged",
            lambda row: str(row.message_id),
            map_tokens_bridged,
        ),
        NormalizationJob(
            OmnibridgeRelayedMessage,
            "omnibridge_relayed_message",
            lambda row: str(row.src_transaction_hash),
            map_relayed_message,
        ),
        NormalizationJob(
            OmnibridgeSignedForUserRequest,
            "omnibridge_signed_for_user_request",
            lambda row: f"{row.signer}:{row.message_hash}",
            map_signed_for_user_request,
        ),
        NormalizationJob(
            OmnibridgeSignedForAffirmation,
            "omnibridge_signed_for_affirmation",
            lambda row: f"{row.signer}:{row.message_hash or row.src_transaction_hash}",
            map_signed_for_affirmation,
        ),
        NormalizationJob(
            OmnibridgeUserRequestForSignature,
            "omnibridge_user_request_for_signature",
            lambda row: str(row.message_id) if row.message_id else str(row.encoded_data_hash),
            map_user_request_for_signature,
        ),
        NormalizationJob(
            OmnibridgeAffirmationCompleted,
            "omnibridge_affirmation_completed",
            lambda row: str(row.src_transaction_hash),
            map_affirmation_completed,
        ),
        NormalizationJob(
            OmnibridgeUserRequestForAffirmation,
            "omnibridge_user_request_for_affirmation",
            lambda row: str(row.message_id) if row.message_id else str(row.transaction_hash),
            map_user_request_for_affirmation,
        ),
    ),
    "polygon": (
        NormalizationJob(
            PolygonStateSynced,
            "polygon_state_synced",
            lambda row: str(row.state_id),
            map_state_synced,
        ),
        NormalizationJob(
            PolygonStateCommitted,
            "polygon_state_committed",
            lambda row: str(row.state_id),
            map_state_committed,
        ),
        NormalizationJob(
            PolygonLockedToken,
            "polygon_locked_token",
            _id_or_fallback(
                "transaction_hash",
                "depositor",
                "deposit_receiver",
                "root_token",
                "amount",
            ),
            map_locked_token,
        ),
        NormalizationJob(
            PolygonExitedToken,
            "polygon_exited_token",
            _id_or_fallback("transaction_hash", "exitor", "root_token", "amount"),
            map_exited_token,
        ),
        NormalizationJob(
            PolygonTokenDeposited,
            "polygon_token_deposited",
            _id_or_fallback("transaction_hash", "user", "root_token", "child_token", "amount"),
            map_token_deposited,
        ),
        NormalizationJob(
            PolygonBridgeWithdraw,
            "polygon_bridge_withdraw",
            _id_or_fallback("transaction_hash", "user", "root_token", "child_token", "amount"),
            map_bridge_withdraw,
        ),
        NormalizationJob(
            PolygonPOLWithdraw,
            "polygon_pol_withdraw",
            _id_or_fallback("transaction_hash", "user", "root_token", "child_token", "amount"),
            map_pol_withdraw,
        ),
    ),
    "ronin": (
        NormalizationJob(
            RoninDepositRequested,
            "ronin_deposit_requested",
            lambda row: str(row.deposit_id),
            map_deposit_requested,
        ),
        NormalizationJob(
            RoninTokenDeposited,
            "ronin_token_deposited",
            lambda row: str(row.deposit_id),
            map_token_deposited,
        ),
        NormalizationJob(
            RoninWithdrawalRequested,
            "ronin_withdrawal_requested",
            lambda row: str(row.withdrawal_id),
            map_withdrawal_requested,
        ),
        NormalizationJob(
            RoninTokenWithdrew,
            "ronin_token_withdrew",
            lambda row: str(row.withdrawal_id),
            map_token_withdrew,
        ),
    ),
}


def get_jobs_for_bridge(bridge: str) -> tuple[NormalizationJob, ...]:
    try:
        return BRIDGE_JOBS[bridge]
    except KeyError as exc:
        raise ValueError(f"Unsupported bridge: {bridge}") from exc
