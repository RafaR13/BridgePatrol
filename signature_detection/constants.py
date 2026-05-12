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
    UNAUTHORIZED_CONTRACT = "UNAUTHORIZED_CONTRACT"
    CONTRACT_MISMATCH = "CONTRACT_MISMATCH"
    DUPLICATE_SIGNATURE = "DUPLICATE_SIGNATURE"
    INSUFFICIENT_SIGNATURES = "INSUFFICIENT_SIGNATURES"
    RECEIPT_REPLAY = "RECEIPT_REPLAY"


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


POLYGON_POS_CORE = {
    "root_chain_manager": (
        "0xa0c68c638235ee32657e8f720a23cec1bfc77c77",
    ),
    "state_sender": (
        "0x28e4f3a7f651294b9564800b2d01f35189a5bfbe",
    ),
    "child_chain_manager_proxy": (
        "0xa6fa4fb5f76172d178d61b04b0ecd319c5d1caa",
    ),
}


VERIFIED_CONTRACTS: dict[str, dict[str, dict[NormalizedEventType, tuple[str, ...]]]] = {
    "polygon": {
        "pos_deposit": {
            NormalizedEventType.LOCKED_TOKEN: (
                "0x40ec5b33f54e0e8a33a975908c5ba1c14e5bbbdf",
                "0x8484ef722627bf18ca5ae6bcf031c23e6e922b30",
            ),
            NormalizedEventType.TOKEN_DEPOSITED: (
                "0xd9c7c4ed4b66858301d0cb28cc88bf655fe34861",
            ),
        },
        "plasma_deposit": {
            NormalizedEventType.NEW_DEPOSIT_BLOCK: (
                "0x401f6c983ea34274ec46f84d70b31c151321188b",
            ),
            NormalizedEventType.TOKEN_DEPOSITED: (
                "0xd9c7c4ed4b66858301d0cb28cc88bf655fe34861",
            ),
        },
        "pos_withdrawal": {
            NormalizedEventType.CHILD_TOKEN_BURN: (),
            NormalizedEventType.EXITED_TOKEN: (
                "0x40ec5b33f54e0e8a33a975908c5ba1c14e5bbbdf",
                "0x8484ef722627bf18ca5ae6bcf031c23e6e922b30",
            ),
        },
        "plasma_withdrawal": {
            NormalizedEventType.POL_WITHDRAW: (
                "0x0000000000000000000000000000000000001010",
            ),
            NormalizedEventType.BRIDGE_WITHDRAWAL: (
                "0x2a88696e0ffa76baa1338f2c74497cc013495922",
            ),
        },
    },
    "ronin": {
        "deposit": {
            NormalizedEventType.DEPOSIT_REQUESTED: (
                "0x64192819ac13ef72bf6b5ae239ac672b43a9af08",
            ),
            NormalizedEventType.TOKEN_DEPOSITED: (
                "0x0cf8ff40a508bdbc39fbe1bb679dcba64e65c7df",
            ),
        },
        "withdrawal": {
            NormalizedEventType.WITHDRAWAL_REQUESTED: (
                "0x0cf8ff40a508bdbc39fbe1bb679dcba64e65c7df",
            ),
            NormalizedEventType.TOKEN_WITHDREW: (
                "0x64192819ac13ef72bf6b5ae239ac672b43a9af08",
            ),
        },
    },
    "omnibridge": {},
    "ccip": {
        "message_execution": {},
    },
    "cctp": {
        "burn_message": {
            NormalizedEventType.DEPOSIT_FOR_BURN: (
                "0xbd3fa81b58ba92a82136038b25adec7066af3155",
                "0x19330d10d9cc8751218eaf51e8885d058642e08a",
                "0x6b25532e1060ce10cc3b0a99e5683b91bfde6982",
                "0x9daf8c91aefae50b9c0e69629d3f6ca40ca3b3fe",
                "0x2b4069517957735be00cee0fadae88a26365528f",
                "0x1682ae6375c4e4a97e4b583bc394c861a46d8962",
            ),
            NormalizedEventType.MESSAGE_RECEIVED: (
                "0x0a992d191deec32afe36203ad87d7d289a738f81",
                "0xc30362313fbba5cf9163f0bb16a0e01f01a896ca",
                "0x8186359af5f57fbb40c6b14a588d2a59c0c29880",
                "0xf3be9355363857f3e001be68856a2f96b4c39ba9",
                "0x4d41f22c5a0e5c74090899e5a8fb597a8842b3e8",
                "0xad09780d193884d503182ad4588450c416d6f9d4",
            ),
        },
    },
    "across": {
        "deposit_fill": {
            NormalizedEventType.DEPOSIT_INTENT: (
                "0x5c7bcd6e7de5423a257d81b442095a1a6ced35c5",
                "0x09aea4b2242abc8bb4bb78d537a67a245a7bec64",
                "0xe35e9842fceaca96570b734083f4a58e8f7c5f2a",
                "0x9295ee1d8c5b022be115a2ad3c30c72e34e7f096",
                "0x6f26bf09b1c792e3228e5467807a900a503c0281",
                "0x3bad7ad0728f9917d1bf08af5782dcbd516cdd96",
                "0x7e63a5f1a8f0b4d0934b2f2327daed3f6bb2ee75",
            ),
            NormalizedEventType.FILL_EXECUTED: (
                "0x5c7bcd6e7de5423a257d81b442095a1a6ced35c5",
                "0x09aea4b2242abc8bb4bb78d537a67a245a7bec64",
                "0xe35e9842fceaca96570b734083f4a58e8f7c5f2a",
                "0x9295ee1d8c5b022be115a2ad3c30c72e34e7f096",
                "0x6f26bf09b1c792e3228e5467807a900a503c0281",
                "0x3bad7ad0728f9917d1bf08af5782dcbd516cdd96",
                "0x7e63a5f1a8f0b4d0934b2f2327daed3f6bb2ee75",
            ),
        },
    },
    "mayan": {},
    "debridge": {},
    "stargate": {},
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
