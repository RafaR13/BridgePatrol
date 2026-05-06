from enum import Enum
from dataclasses import dataclass
from typing import Dict

from normalization.event_types import NormalizedEventType


class AlertSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    # for now, all alerts will have a low severity


class AlertStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class SignatureType(str, Enum):
    LOCK_WITHOUT_MINT = "LOCK_WITHOUT_MINT"
    MINT_WITHOUT_LOCK = "MINT_WITHOUT_LOCK"
    OVER_MINT = "OVER_MINT"
    OVER_RELEASE = "OVER_RELEASE"
    AMOUNT_MISMATCH = "AMOUNT_MISMATCH"
    PROOF_REPLAY = "PROOF_REPLAY"


@dataclass(frozen=True)
class RelatedEvent:
    event_type: NormalizedEventType
    side: str
    anchor_side: str
    anchor_event_type: NormalizedEventType
    anchor_field: str = "transaction_hash"
    event_field: str = "transaction_hash"


@dataclass(frozen=True)
class EventPairFlow:
    name: str
    source: NormalizedEventType
    destination: NormalizedEventType
    source_key: tuple[str, ...] = ("correlation_id",)
    destination_key: tuple[str, ...] = ("correlation_id",)
    related_events: tuple[RelatedEvent, ...] = ()
    amount_check: bool = False


@dataclass(frozen=True)
class BridgeEventConfig:
    deposits: tuple[EventPairFlow, ...] = ()
    withdrawals: tuple[EventPairFlow, ...] = ()
    todo: str | None = None


BRIDGE_EVENT_MAP: Dict[str, BridgeEventConfig] = {
    "ronin": BridgeEventConfig(
        deposits=(
            EventPairFlow(
                name="deposit",
                source=NormalizedEventType.DEPOSIT_REQUESTED,
                destination=NormalizedEventType.TOKEN_DEPOSITED,
                source_key=("correlation_id",),  # deposit_id
                destination_key=("correlation_id",),  # deposit_id
                amount_check=True,
            ),
        ),
        withdrawals=(
            EventPairFlow(
                name="withdrawal",
                source=NormalizedEventType.WITHDRAWAL_REQUESTED,
                destination=NormalizedEventType.TOKEN_WITHDREW,
                source_key=("correlation_id",),  # withdrawal_id
                destination_key=("correlation_id",),  # withdrawal_id
                amount_check=True,
            ),
        ),
    ),
    "polygon": BridgeEventConfig(
        deposits=(
            EventPairFlow(
                name="pos_deposit",
                source=NormalizedEventType.STATE_SYNCED,
                destination=NormalizedEventType.STATE_COMMITTED,
                source_key=("correlation_id",),  # state_id
                destination_key=("correlation_id",),  # state_id
                related_events=(
                    RelatedEvent(
                        event_type=NormalizedEventType.LOCKED_TOKEN,
                        side="source",
                        anchor_side="source",
                        anchor_event_type=NormalizedEventType.STATE_SYNCED,
                        anchor_field="transaction_hash",
                        event_field="transaction_hash",
                    ),
                ),
            ),
            EventPairFlow(
                name="plasma_deposit",
                source=NormalizedEventType.STATE_SYNCED,
                destination=NormalizedEventType.STATE_COMMITTED,
                source_key=("correlation_id",),  # state_id
                destination_key=("correlation_id",),  # state_id
                related_events=(
                    RelatedEvent(
                        event_type=NormalizedEventType.NEW_DEPOSIT_BLOCK,
                        side="source",
                        anchor_side="source",
                        anchor_event_type=NormalizedEventType.STATE_SYNCED,
                        anchor_field="transaction_hash",
                        event_field="transaction_hash",
                    ),
                    RelatedEvent(
                        event_type=NormalizedEventType.TOKEN_DEPOSITED,
                        side="destination",
                        anchor_side="destination",
                        anchor_event_type=NormalizedEventType.STATE_COMMITTED,
                        anchor_field="transaction_hash",
                        event_field="transaction_hash",
                    ),
                    RelatedEvent(
                        event_type=NormalizedEventType.TOKEN_DEPOSITED,
                        side="destination",
                        anchor_side="source",
                        anchor_event_type=NormalizedEventType.NEW_DEPOSIT_BLOCK,
                        anchor_field="extra_data.deposit_block_id",
                        event_field="extra_data.deposit_block_id",
                    ),
                ),
                amount_check=True,
            ),
        ),
        withdrawals=(
            EventPairFlow(
                name="plasma_withdrawal",
                source=NormalizedEventType.POL_WITHDRAW,
                destination=NormalizedEventType.BRIDGE_WITHDRAWAL,
                source_key=("correlation_id",),  # token/from_address/amount
                destination_key=("correlation_id",),  # token/user/amount
                amount_check=True,
            ),
            EventPairFlow(
                name="pos_withdrawal",
                source=NormalizedEventType.CHILD_TOKEN_BURN,
                destination=NormalizedEventType.EXITED_TOKEN,
                source_key=("correlation_id",),  # root_token/from_address/amount
                destination_key=("correlation_id",),  # root_token/exitor/amount
                amount_check=True,
            ),
        ),
    ),
    "omnibridge": BridgeEventConfig(
        todo="TODO: define Omnibridge event pair grouping.",
    ),
    "ccip": BridgeEventConfig(
        deposits=(
            EventPairFlow(
                name="message_execution",
                source=NormalizedEventType.MESSAGE_SENT,
                destination=NormalizedEventType.MESSAGE_EXECUTION_STATE_CHANGED,
                source_key=("extra_data.sequence_number",),
                destination_key=("extra_data.sequence_number",),
            ),
        ),
    ),
    "cctp": BridgeEventConfig(
        deposits=(
            EventPairFlow(
                name="burn_message",
                source=NormalizedEventType.DEPOSIT_FOR_BURN,
                destination=NormalizedEventType.MESSAGE_RECEIVED,
                source_key=("correlation_id",),  # nonce
                destination_key=("correlation_id",),  # nonce
                amount_check=True,
            ),
        ),
    ),
    "across": BridgeEventConfig(
        deposits=(
            EventPairFlow(
                name="deposit_fill",
                source=NormalizedEventType.DEPOSIT_INTENT,
                destination=NormalizedEventType.FILL_EXECUTED,
                source_key=("correlation_id",),  # deposit_id
                destination_key=("correlation_id",),  # deposit_id
            ),
        ),
        todo="TODO: relayer_refund cannot be reliably paired with a deposit/fill.",
    ),
    "mayan": BridgeEventConfig(
        todo="TODO: define Mayan event pair grouping.",
    ),
    "debridge": BridgeEventConfig(
        todo="TODO: define DeBridge event pair grouping.",
    ),
    "stargate": BridgeEventConfig(
        todo="TODO: define Stargate event pair grouping.",
    ),
}


class Bridges(Enum):  # supported bridges
    STARGATE = "stargate"
    CCTP = "cctp"
    CCIP = "ccip"
    ACROSS = "across"
    POLYGON = "polygon"
    RONIN = "ronin"
    OMNIBRIDGE = "omnibridge"
    DEBRIDGE = "debridge"
    MAYAN = "mayan"


TIME_THRESHOLDS = {
    # times after which we consider a lock/mint pair to be suspicious if the corresponding mint/lock event has not been observed
    Bridges.RONIN.value: 3600,  # 1 hour
    Bridges.POLYGON.value: 3600,  # 1 hour
    Bridges.OMNIBRIDGE.value: 3600,  # 1 hour
    Bridges.CCIP.value: 3600,  # 1 hour
    Bridges.CCTP.value: 3600,  # 1 hour
    Bridges.ACROSS.value: 3600,  # 1 hour
}

BlockConfirmationThresholds = {
    Bridges.RONIN.value: 120,
    Bridges.POLYGON.value: 180,
    Bridges.OMNIBRIDGE.value: 20,
    Bridges.CCIP.value: 20,
    Bridges.CCTP.value: 20,
    Bridges.ACROSS.value: 20,
}
