from enum import Enum
from dataclasses import dataclass
from typing import Dict

from normalization.event_types import NormalizedEventType


class AlertSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class SignatureType(str, Enum):
    LOCK_WITHOUT_MINT = "LOCK_WITHOUT_MINT"
    MINT_WITHOUT_LOCK = "MINT_WITHOUT_LOCK"
    AMOUNT_MISMATCH = "AMOUNT_MISMATCH"
    RECIPIENT_MISMATCH = "RECIPIENT_MISMATCH"
    PROOF_REPLAY = "PROOF_REPLAY"
    UNAUTHORIZED_CONTRACT = "UNAUTHORIZED_CONTRACT"
    CONTRACT_MISMATCH = "CONTRACT_MISMATCH"
    UNEXPECTED_EVENT_CALLER = "UNEXPECTED_EVENT_CALLER"
    DANGEROUS_TRACE_OPERATION = "DANGEROUS_TRACE_OPERATION"
    DUPLICATE_SIGNATURE = "DUPLICATE_SIGNATURE"
    INSUFFICIENT_SIGNATURES = "INSUFFICIENT_SIGNATURES"
    RECEIPT_REPLAY = "RECEIPT_REPLAY"


EXPECTED_EVENT_CALLERS: dict[
    str,
    dict[str, tuple[str, ...] | dict[str, tuple[str, ...]]],
] = {
    # Destination-side token mints/deposits on Polygon should be triggered by the
    # child chain manager; source-side exits/releases should be triggered through
    # the root chain manager before the predicate/token emits the destination log.
    #
    # Do not configure public entrypoint events such as Across FillExecuted or
    # CCTP MessageReceived here: their direct caller can be an arbitrary relayer.
    # For those bridges, use this check only when normalized token movement
    # events are available and the token's internal caller is protocol-controlled.
    "polygon": {
        "TOKEN_DEPOSITED": {
            "0xd9c7c4ed4b66858301d0cb28cc88bf655fe34861": (
                "0xa6fa4fb5f76172d178d61b04b0ecd319c5d1c0aa",
            ),
        },
        "EXITED_TOKEN": {
            "0x40ec5b33f54e0e8a33a975908c5ba1c14e5bbbdf": (
                "0xa0c68c638235ee32657e8f720a23cec1bfc77c77",
            ),
            "0x8484ef722627bf18ca5ae6bcf031c23e6e922b30": (
                "0xa0c68c638235ee32657e8f720a23cec1bfc77c77",
            ),
        },
    },
    # Qubit's destination ProposalEvent authorizes the synthetic qXETH mint. If
    # Transfer events for qXETH are normalized, the token caller should be the
    # destination bridge handler, not a temporary attacker contract.
    "qubit": {
        "Transfer": {
            "0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f": (
                "0x4d8ae68fcae98bf93299548545933c0d273ba23a",
            ),
        },
    },
}


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


@dataclass(frozen=True)
class TokenContractAttackConfig:
    event_type: NormalizedEventType
    native_tokens: dict[str, str]
    expected_contracts: tuple[str, ...]
    correlation_type: str
    event_label: str
    actor_label: str
    amount_label: str
    title: str


@dataclass(frozen=True)
class BridgeCctxTimeout:
    typical_seconds: int
    max_seconds: int


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
                source=NormalizedEventType.LOCKED_TOKEN,
                destination=NormalizedEventType.TRANSFER,
                source_key=("correlation_id",),  # source tx hash
                destination_key=("cctx_id",),  # attached via StateCommitted tx hash
                related_events=(
                    RelatedEvent(
                        event_type=NormalizedEventType.STATE_SYNCED,
                        side="source",
                        anchor_side="source",
                        anchor_event_type=NormalizedEventType.LOCKED_TOKEN,
                        anchor_field="transaction_hash",
                        event_field="transaction_hash",
                    ),
                    RelatedEvent(
                        event_type=NormalizedEventType.STATE_COMMITTED,
                        side="source",
                        anchor_side="source",
                        anchor_event_type=NormalizedEventType.STATE_SYNCED,
                        anchor_field="correlation_id",
                        event_field="correlation_id",
                    ),
                    RelatedEvent(
                        event_type=NormalizedEventType.TRANSFER,
                        side="destination",
                        anchor_side="source",
                        anchor_event_type=NormalizedEventType.STATE_COMMITTED,
                        anchor_field="transaction_hash",
                        event_field="transaction_hash",
                    ),
                ),
                amount_check=True,
            ),
            EventPairFlow(
                name="plasma_deposit",
                source=NormalizedEventType.NEW_DEPOSIT_BLOCK,
                destination=NormalizedEventType.TOKEN_DEPOSITED,
                source_key=("correlation_id",),  # deposit_block_id
                destination_key=("correlation_id",),  # deposit_count
                related_events=(
                    RelatedEvent(
                        event_type=NormalizedEventType.STATE_SYNCED,
                        side="source",
                        anchor_side="source",
                        anchor_event_type=NormalizedEventType.NEW_DEPOSIT_BLOCK,
                        anchor_field="transaction_hash",
                        event_field="transaction_hash",
                    ),
                    RelatedEvent(
                        event_type=NormalizedEventType.STATE_COMMITTED,
                        side="source",
                        anchor_side="source",
                        anchor_event_type=NormalizedEventType.STATE_SYNCED,
                        anchor_field="correlation_id",
                        event_field="correlation_id",
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
                source_key=("message_id", "extra_data.sequence_number"),
                destination_key=("message_id", "extra_data.sequence_number"),
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
    "nomad": BridgeEventConfig(
        deposits=(
            EventPairFlow(
                name="message_delivery",
                source=NormalizedEventType.NOMAD_HOME_DISPATCH,
                destination=NormalizedEventType.NOMAD_ROUTER_RECEIVE,
                source_key=("src_blockchain", "dst_blockchain", "nonce"),
                destination_key=("src_blockchain", "dst_blockchain", "nonce"),
                related_events=(
                    RelatedEvent(
                        event_type=NormalizedEventType.NOMAD_ROUTER_SEND,
                        side="source",
                        anchor_side="source",
                        anchor_event_type=NormalizedEventType.NOMAD_HOME_DISPATCH,
                        anchor_field="transaction_hash",
                        event_field="transaction_hash",
                    ),
                    RelatedEvent(
                        event_type=NormalizedEventType.NOMAD_REPLICA_PROCESS,
                        side="destination",
                        anchor_side="destination",
                        anchor_event_type=NormalizedEventType.NOMAD_ROUTER_RECEIVE,
                        anchor_field="transaction_hash",
                        event_field="transaction_hash",
                    ),
                ),
                amount_check=True,
            ),
        ),
    ),
    "debridge": BridgeEventConfig(
        todo="TODO: define DeBridge event pair grouping.",
    ),
    "stargate": BridgeEventConfig(
        todo="TODO: define Stargate event pair grouping.",
    ),
    "thorchain": BridgeEventConfig(
        todo=(
            "Source-only dataset: destination pairing is intentionally not configured "
            "and must not be treated as a missing destination event."
        ),
    ),
    "meter.io": BridgeEventConfig(
        deposits=(
            EventPairFlow(
                name="deposit_execution",
                source=NormalizedEventType.DEPOSIT,
                destination=NormalizedEventType.PROPOSAL_EVENT,
                source_key=("correlation_id",),
                destination_key=("correlation_id",),
                related_events=(
                    RelatedEvent(
                        event_type=NormalizedEventType.TRANSFER,
                        side="destination",
                        anchor_side="destination",
                        anchor_event_type=NormalizedEventType.PROPOSAL_EVENT,
                    ),
                    RelatedEvent(
                        event_type=NormalizedEventType.INTERNAL_TRANSFER,
                        side="destination",
                        anchor_side="destination",
                        anchor_event_type=NormalizedEventType.PROPOSAL_EVENT,
                    ),
                ),
            ),
        ),
        todo=(
            "TODO: Meter.io source amount is currently stored only in extra_data for "
            "the documented samples, so amount checks remain disabled. Some Meter "
            "destinations are also unavailable in the source material."
        ),
    ),
    "qubit": BridgeEventConfig(
        deposits=(
            EventPairFlow(
                name="deposit_mint",
                source=NormalizedEventType.DEPOSIT,
                destination=NormalizedEventType.PROPOSAL_EVENT,
                source_key=("correlation_id",),
                destination_key=("correlation_id",),
                related_events=(
                    RelatedEvent(
                        event_type=NormalizedEventType.TRANSFER,
                        side="destination",
                        anchor_side="destination",
                        anchor_event_type=NormalizedEventType.PROPOSAL_EVENT,
                    ),
                ),
                amount_check=True,
            ),
        ),
        todo=(
            "TODO: populate the intended recipient on the source Deposit event "
            "(currently actor_to is NULL in the documented samples) before enabling "
            "meaningful recipient mismatch detection."
        ),
    ),
    "chainswap": BridgeEventConfig(
        todo=(
            "TODO: define ChainSwap source/destination event pair grouping. "
            "The current curated attack dataset has destination-side Receive() "
            "transactions only and no normalized events."
        ),
    ),
}


POLYGON_POS_CORE = {
    "root_chain_manager": ("0xa0c68c638235ee32657e8f720a23cec1bfc77c77",),
    "state_sender": ("0x28e4f3a7f651294b9564800b2d01f35189a5bfbe",),
    "child_chain_manager_proxy": ("0xa6fa4fb5f76172d178d61b04b0ecd319c5d1c0aa",),
}


EVM_NATIVE_TOKEN_CONTRACTS: dict[str, str] = {
    "base": "0x4200000000000000000000000000000000000006",
    "optimism": "0x4200000000000000000000000000000000000006",
    "arbitrum": "0x82af49447d8a07e3bd95bd0d56f35241523fbab1",
    "polygon": "0x0000000000000000000000000000000000000000",
    "ethereum": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
    "scroll": "0x5300000000000000000000000000000000000004",
    "linea": "0xe5d7c2a44ffddf6b295a15c148167daaaf5cf34f",
    "bnb": "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c",
    "avalanche": "0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7",
    "gnosis": "0xe91d153e0b41518a2ce8dd3d7944fa863463a97d",
    "unichain": "0x4200000000000000000000000000000000000006",
    "moonbeam": "0xacc15dc74880c9944775448304b263d191c6077f",
}

NULL_NATIVE_TOKEN = "0x0000000000000000000000000000000000000000"

NATIVE_TOKENS: dict[str, dict[str, str]] = {
    "polygon": {
        "ethereum": EVM_NATIVE_TOKEN_CONTRACTS["ethereum"],
    },
    "omnibridge": {
        "ethereum": EVM_NATIVE_TOKEN_CONTRACTS["ethereum"],
        "gnosis": EVM_NATIVE_TOKEN_CONTRACTS["gnosis"],
    },
    # Ronin has different source chains for deposits and withdrawals. The
    # available XChainDataGen metadata identifies Ronin's native asset symbol
    # but does not provide a contract/sentinel value to compare with token_in.
    "ronin": {
        "ethereum": EVM_NATIVE_TOKEN_CONTRACTS["ethereum"],
    },
    "cctp": {
        "ethereum": EVM_NATIVE_TOKEN_CONTRACTS["ethereum"],
        "base": EVM_NATIVE_TOKEN_CONTRACTS["base"],
        "optimism": EVM_NATIVE_TOKEN_CONTRACTS["optimism"],
        "arbitrum": EVM_NATIVE_TOKEN_CONTRACTS["arbitrum"],
        "polygon": EVM_NATIVE_TOKEN_CONTRACTS["polygon"],
        "avalanche": EVM_NATIVE_TOKEN_CONTRACTS["avalanche"],
    },
    "ccip": EVM_NATIVE_TOKEN_CONTRACTS,
    "across": {
        "ethereum": EVM_NATIVE_TOKEN_CONTRACTS["ethereum"],
        "unichain": EVM_NATIVE_TOKEN_CONTRACTS["unichain"],
        "arbitrum": EVM_NATIVE_TOKEN_CONTRACTS["arbitrum"],
        "polygon": EVM_NATIVE_TOKEN_CONTRACTS["polygon"],
        "optimism": EVM_NATIVE_TOKEN_CONTRACTS["optimism"],
        "base": EVM_NATIVE_TOKEN_CONTRACTS["base"],
        "scroll": EVM_NATIVE_TOKEN_CONTRACTS["scroll"],
        "linea": EVM_NATIVE_TOKEN_CONTRACTS["linea"],
    },
    "debridge": {
        "ethereum": NULL_NATIVE_TOKEN,
        "optimism": NULL_NATIVE_TOKEN,
        "arbitrum": NULL_NATIVE_TOKEN,
        "avalanche": NULL_NATIVE_TOKEN,
        "base": NULL_NATIVE_TOKEN,
        "bnb": NULL_NATIVE_TOKEN,
        "polygon": NULL_NATIVE_TOKEN,
        "linea": NULL_NATIVE_TOKEN,
        "solana": NULL_NATIVE_TOKEN,
    },
    "mayan": {
        **EVM_NATIVE_TOKEN_CONTRACTS,
        "solana": NULL_NATIVE_TOKEN,
    },
    "thorchain": {
        "thorchain": NULL_NATIVE_TOKEN,
    },
    "meter.io": EVM_NATIVE_TOKEN_CONTRACTS,
    "pnetwork": {},
    "qubit": {
        "ethereum": NULL_NATIVE_TOKEN,
    },
    "chainswap": {},  # TODO: fill token/native-token mapping if ChainSwap events are normalized.
}

# Source event contracts observed in the supplied Thorchain samples.
# TODO: confirm whether this is a complete allowlist before enforcing it.
THORCHAIN_OBSERVED_SOURCE_CONTRACTS = (
    "0x42a5ed456650a09dc10ebc6361a7480fdd61f27b",
    "0xc145990e84155416144c532e31f89b840ca8c2ce",
)


TOKEN_CONTRACT_ATTACK_CONFIG: dict[str, tuple[TokenContractAttackConfig, ...]] = {
    "polygon": (
        TokenContractAttackConfig(
            event_type=NormalizedEventType.LOCKED_TOKEN,
            native_tokens=NATIVE_TOKENS["polygon"],
            expected_contracts=(
                "0x40ec5b33f54e0e8a33a975908c5ba1c14e5bbbdf",
                "0x8484ef722627bf18ca5ae6bcf031c23e6e922b30",
            ),
            correlation_type="locked_token_contract_attack",
            event_label="LockedToken",
            actor_label="depositor",
            amount_label="locked amount",
            title="polygon: LockedToken failed token contract checks",
        ),
    ),
    "ronin": (
        TokenContractAttackConfig(
            event_type=NormalizedEventType.DEPOSIT_REQUESTED,
            native_tokens=NATIVE_TOKENS["ronin"],
            expected_contracts=("0x64192819ac13ef72bf6b5ae239ac672b43a9af08",),
            correlation_type="ronin_token_contract_attack",
            event_label="DepositRequested",
            actor_label="request actor",
            amount_label="requested amount",
            title="ronin: request event failed token contract checks",
        ),
        TokenContractAttackConfig(
            event_type=NormalizedEventType.WITHDRAWAL_REQUESTED,
            native_tokens=NATIVE_TOKENS["ronin"],
            expected_contracts=("0x0cf8ff40a508bdbc39fbe1bb679dcba64e65c7df",),
            correlation_type="ronin_token_contract_attack",
            event_label="WithdrawalRequested",
            actor_label="request actor",
            amount_label="requested amount",
            title="ronin: request event failed token contract checks",
        ),
    ),
    "cctp": (
        TokenContractAttackConfig(
            event_type=NormalizedEventType.DEPOSIT_FOR_BURN,
            native_tokens=NATIVE_TOKENS["cctp"],
            expected_contracts=(
                "0xbd3fa81b58ba92a82136038b25adec7066af3155",
                "0x19330d10d9cc8751218eaf51e8885d058642e08a",
                "0x6b25532e1060ce10cc3b0a99e5683b91bfde6982",
                "0x9daf8c91aefae50b9c0e69629d3f6ca40ca3b3fe",
                "0x2b4069517957735be00cee0fadae88a26365528f",
                "0x1682ae6375c4e4a97e4b583bc394c861a46d8962",
            ),
            correlation_type="cctp_token_contract_attack",
            event_label="DepositForBurn",
            actor_label="depositor",
            amount_label="DepositForBurn amount",
            title="cctp: DepositForBurn failed token contract checks",
        ),
    ),
    "across": (
        TokenContractAttackConfig(
            event_type=NormalizedEventType.DEPOSIT_INTENT,
            native_tokens=NATIVE_TOKENS["across"],
            expected_contracts=(
                "0x5c7bcd6e7de5423a257d81b442095a1a6ced35c5",
                "0x09aea4b2242abc8bb4bb78d537a67a245a7bec64",
                "0xe35e9842fceaca96570b734083f4a58e8f7c5f2a",
                "0x9295ee1d8c5b022be115a2ad3c30c72e34e7f096",
                "0x6f26bf09b1c792e3228e5467807a900a503c0281",
                "0x3bad7ad0728f9917d1bf08af5782dcbd516cdd96",
                "0x7e63a5f1a8f0b4d0934b2f2327daed3f6bb2ee75",
            ),
            correlation_type="across_token_contract_attack",
            event_label="DepositIntent",
            actor_label="depositor",
            amount_label="input amount",
            title="across: DepositIntent failed token contract checks",
        ),
    ),
    "pnetwork": (
        TokenContractAttackConfig(
            event_type=NormalizedEventType.PNETWORK_REDEEM,
            native_tokens=NATIVE_TOKENS["pnetwork"],
            expected_contracts=("0xed28a457a5a76596ac48d87c0f577020f6ea1c4c",),
            correlation_type="pnetwork_redeem_contract_attack",
            event_label="Redeem",
            actor_label="redeemer",
            amount_label="redeem amount",
            title="pNetwork: Redeem event failed token contract checks",
        ),
    ),
    "debridge": (
        TokenContractAttackConfig(
            event_type=NormalizedEventType.ORDER_CREATED,
            native_tokens=NATIVE_TOKENS["debridge"],
            expected_contracts=("0xef4fb24ad0916217251f553c0596f8edc630eb66",),
            correlation_type="debridge_token_contract_attack",
            event_label="OrderCreated",
            actor_label="maker",
            amount_label="give amount",
            title="debridge: OrderCreated failed token contract checks",
        ),
    ),
    "omnibridge": (
        TokenContractAttackConfig(
            event_type=NormalizedEventType.BRIDGING_INITIATED,
            native_tokens=NATIVE_TOKENS["omnibridge"],
            expected_contracts=(
                "0x88ad09518695c6c3712ac10a214be5109a655671",
                "0xf6a78083ca3e2a662d6dd1703c939c8ace2e268d",
            ),
            correlation_type="omnibridge_token_contract_attack",
            event_label="TokensBridgingInitiated",
            actor_label="sender",
            amount_label="bridged amount",
            title="omnibridge: TokensBridgingInitiated failed token contract checks",
        ),
    ),
    "mayan": (
        TokenContractAttackConfig(
            event_type=NormalizedEventType.SWAP_AND_FORWARDED,
            native_tokens=NATIVE_TOKENS["mayan"],
            expected_contracts=(
                "0x337685fdab40d39bd02028545a4ffa7d287cc3e2",
                "0x0654874eb7f59c6f5b39931fc45dc45337c967c3",
            ),
            correlation_type="mayan_token_contract_attack",
            event_label="SwapAndForwarded",
            actor_label="sender",
            amount_label="input amount",
            title="mayan: SwapAndForwarded failed token contract checks",
        ),
        TokenContractAttackConfig(
            event_type=NormalizedEventType.FORWARDED,
            native_tokens=NATIVE_TOKENS["mayan"],
            expected_contracts=(
                "0x337685fdab40d39bd02028545a4ffa7d287cc3e2",
                "0x0654874eb7f59c6f5b39931fc45dc45337c967c3",
            ),
            correlation_type="mayan_token_contract_attack",
            event_label="Forwarded",
            actor_label="sender",
            amount_label="forwarded amount",
            title="mayan: Forwarded failed token contract checks",
        ),
        TokenContractAttackConfig(
            event_type=NormalizedEventType.INIT_ORDER,
            native_tokens=NATIVE_TOKENS["mayan"],
            expected_contracts=("0xc38e4e6a15593f908255214653d3d947ca1c2338",),
            correlation_type="mayan_token_contract_attack",
            event_label="InitOrder",
            actor_label="sender",
            amount_label="source amount",
            title="mayan: InitOrder failed token contract checks",
        ),
    ),
    "meter.io": (
        TokenContractAttackConfig(
            event_type=NormalizedEventType.DEPOSIT,
            native_tokens=NATIVE_TOKENS["meter.io"],
            expected_contracts=(
                "0xfd55ebc7bbde603a048648c6eab8775c997c1001",
                "0xa2a22b46b8df38cd7c55e6bf32ea5a32637cf2b1",
            ),
            correlation_type="meter_io_token_contract_attack",
            event_label="Deposit",
            actor_label="sender",
            amount_label="deposit amount",
            title="meter.io: Deposit failed token contract checks",
        ),
    ),
    "qubit": (
        TokenContractAttackConfig(
            event_type=NormalizedEventType.DEPOSIT,
            native_tokens=NATIVE_TOKENS["qubit"],
            expected_contracts=("0x20e5e35ba29dc3b540a1aee781d0814d5c77bce6",),
            correlation_type="qubit_token_contract_attack",
            event_label="Deposit",
            actor_label="sender",
            amount_label="deposit amount",
            title="qubit: Deposit failed token contract checks",
        ),
    ),
    "thorchain": (
        TokenContractAttackConfig(
            event_type=NormalizedEventType.DEPOSIT,
            native_tokens=NATIVE_TOKENS["thorchain"],
            expected_contracts=THORCHAIN_OBSERVED_SOURCE_CONTRACTS,
            correlation_type="thorchain_deposit_contract_attack",
            event_label="Deposit",
            actor_label="sender",
            amount_label="deposit amount",
            title="thorchain: Deposit failed token contract checks",
        ),
    ),
}


VERIFIED_CONTRACTS: dict[str, dict[str, dict[NormalizedEventType, tuple[str, ...]]]] = {
    "polygon": {
        "pos_deposit": {
            NormalizedEventType.LOCKED_TOKEN: (
                "0x40ec5b33f54e0e8a33a975908c5ba1c14e5bbbdf",
                "0x8484ef722627bf18ca5ae6bcf031c23e6e922b30",
            ),
            NormalizedEventType.TOKEN_DEPOSITED: ("0xd9c7c4ed4b66858301d0cb28cc88bf655fe34861",),
        },
        "plasma_deposit": {
            NormalizedEventType.NEW_DEPOSIT_BLOCK: ("0x401f6c983ea34274ec46f84d70b31c151321188b",),
            NormalizedEventType.TOKEN_DEPOSITED: ("0xd9c7c4ed4b66858301d0cb28cc88bf655fe34861",),
        },
        "pos_withdrawal": {
            NormalizedEventType.CHILD_TOKEN_BURN: (),
            NormalizedEventType.EXITED_TOKEN: (
                "0x40ec5b33f54e0e8a33a975908c5ba1c14e5bbbdf",
                "0x8484ef722627bf18ca5ae6bcf031c23e6e922b30",
            ),
        },
        "plasma_withdrawal": {
            NormalizedEventType.POL_WITHDRAW: ("0x0000000000000000000000000000000000001010",),
            NormalizedEventType.BRIDGE_WITHDRAWAL: ("0x2a88696e0ffa76baa1338f2c74497cc013495922",),
        },
    },
    "ronin": {
        "deposit": {
            NormalizedEventType.DEPOSIT_REQUESTED: ("0x64192819ac13ef72bf6b5ae239ac672b43a9af08",),
            NormalizedEventType.TOKEN_DEPOSITED: ("0x0cf8ff40a508bdbc39fbe1bb679dcba64e65c7df",),
        },
        "withdrawal": {
            NormalizedEventType.WITHDRAWAL_REQUESTED: (
                "0x0cf8ff40a508bdbc39fbe1bb679dcba64e65c7df",
            ),
            NormalizedEventType.TOKEN_WITHDREW: ("0x64192819ac13ef72bf6b5ae239ac672b43a9af08",),
        },
    },
    "omnibridge": {
        "token_bridge": {
            NormalizedEventType.BRIDGING_INITIATED: (
                "0x88ad09518695c6c3712ac10a214be5109a655671",
                "0xf6a78083ca3e2a662d6dd1703c939c8ace2e268d",
            ),
            NormalizedEventType.TOKENS_BRIDGED: (
                "0x88ad09518695c6c3712ac10a214be5109a655671",
                "0xf6a78083ca3e2a662d6dd1703c939c8ace2e268d",
            ),
        },
        "amb_eth": {
            NormalizedEventType.USER_REQUEST_FOR_AFFIRMATION: (
                "0x4c36d2919e407f0cc2ee3c993ccf8ac26d9ce64e",
            ),
        },
        "xdai_bridge_eth": {
            NormalizedEventType.USER_REQUEST_FOR_AFFIRMATION: (
                "0x4aa42145aa6ebf72e164c9bbc74fbd3788045016",
            ),
            NormalizedEventType.RELAYED_MESSAGE: ("0x4aa42145aa6ebf72e164c9bbc74fbd3788045016",),
        },
        "amb_gnosis": {
            NormalizedEventType.USER_REQUEST_FOR_SIGNATURE: (
                "0x75df5af045d91108662d8080fd1fefad6aa0bb59",
            ),
            NormalizedEventType.SIGNED_FOR_USER_REQUEST: (
                "0x75df5af045d91108662d8080fd1fefad6aa0bb59",
            ),
            NormalizedEventType.SIGNED_FOR_AFFIRMATION: (
                "0x75df5af045d91108662d8080fd1fefad6aa0bb59",
            ),
        },
        "xdai_bridge_gnosis": {
            NormalizedEventType.USER_REQUEST_FOR_SIGNATURE: (
                "0x7301cfa0e1756b71869e93d4e4dca5c7d0eb0aa6",
            ),
            NormalizedEventType.SIGNED_FOR_AFFIRMATION: (
                "0x7301cfa0e1756b71869e93d4e4dca5c7d0eb0aa6",
            ),
            NormalizedEventType.AFFIRMATION_COMPLETED: (
                "0x7301cfa0e1756b71869e93d4e4dca5c7d0eb0aa6",
            ),
        },
    },
    "ccip": {
        "message_execution": {
            NormalizedEventType.MESSAGE_SENT: (
                "0x69ecc4e2d8ea56e2d0a05bf57f4fd6aee7f2c284",
                "0xafd31c0c78785adf53e4c185670bfd5376249d8a",
                "0x15a9d79d6b3485f70bf82bc49ddd1fcb37a7149c",
                "0x3455d8e039736944e66e19eac77a42e8077b07bf",
                "0x948306c220ac325fa9392a6e601042a3cd0b480d",
                "0xb8a882f3b88bd52d1ff56a873bfdb84b70431937",
                "0xf50b9a46c394bd98491ce163d420222d8030f6f0",
                "0xdc5b578ff3afcc4a4a6e149892b9472390b50844",
                "0x626189c882a80ff0d036d8d9f6447555e81f78e9",
                "0x362a221c3cfd7f992dfe221687323f0ba9ba8187",
                "0x67761742ac8a21ec4d76ca18cbd701e5a6f3bef3",
                "0xe80cc83b895ada027b722b78949b296bd1fc5639",
                "0x6087d6c33946670232df09fe93eecbaea3d6864d",
                "0xafecc7b67c6a8e606e94ce4e2f70d83c2206c2cb",
                "0x14bf7b1ca6b843f386bfdfa76bfd439919b9378d",
                "0xc1b6287a3292d6469f2d8545877e40a2f75ca9a6",
                "0xceab512ed28727eeab94698281f38a2c04b0ce78",
                "0xe8784c29c583c52fa89144b9e5dd91df2a1c2587",
                "0x4e910c8bbe88dadf90baa6c1b7850dbea32c5b29",
                "0x5570a4e979d7460f13b84075acef69fac73914b1",
                "0x3e3b4fba004e7824219e79ae9f676d9d41a216fa",
                "0xe6e161d55019aa5960dcf0af9bb6e4d574c69f99",
                "0x139d4108c23e66745eda4ab47c25c83494b7c14d",
                "0xc432b86153eb64d46ecea00591ee7cbc27538c4b",
                "0x1dacbae00c779913e6e9fc1a3323fba4847ba53c",
                "0x13263ac754d1e29430930672e3c0019f2bc44ba2",
                "0x56cb9cd82553bd8157e6504020c38f6da4971717",
                "0x868b71490b36674b3b9006fa8711c6fa26a26631",
                "0x164507757f7d5ab35c6af44eeeb099f5be29da57",
                "0xd26a4e0c664e72e3c29e634867191cb1cb9af570",
                "0xe4c51dc01a4e0ab14c7a7a2ed1655e9cf8a3e698",
                "0x6ba81b83091a23e8f2aa173b2b939faf9e320dfb",
                "0xb9d655ad5ba80036725d6c753fa6af0454cbf630",
                "0x9c725164b60e3f6d4d5b7a2841c63e9fd0988805",
                "0xfc51a4cf925f202d86c6092cda879689d2c17201",
                "0xfe11cfc957cca331192eac60040b442303cca0a9",
                "0x35c724666ba31632a56bad4390eb69f206ab60c7",
                "0x5577c19bd183e39a007ce4ce236f1d91e9132d5c",
                "0x43f00dbf0aa61a099c674a74fbdcb93786564950",
                "0x1c88e3fd2b0a8735d1b19a77aa6e2333555bb95c",
                "0x3a3649852a518ab180f41f28288c6c9184563616",
                "0xdabb6de5ec48dd2fcf28ac85cbefe3f19e03f1bd",
                "0x86768b77c971524d5042631749a59527e8a9604d",
                "0x56b30a0dcd8dc87ec08b80fa09502bab801fa78e",
                "0x9d0ffa76c7f82c34be313b5bfc6d42a72da8ca69",
                "0x4be6e0f97ea849ff80773af7a317356e6c646fd7",
                "0xd3bde678bb706cf727a512515c254bcf021dd203",
                "0x362e6be957c18e268ad91046ca6b47eb09ad98c1",
                "0xe5fd5a0ec3657ad58e875518e73f6264e00eb754",
                "0xb1dddde9c1e88df7751f8f2cf18569b13c8af670",
                "0x014abcfdbce9f67d0df34574664a6c0a241ec03a",
                "0x02b60267bceeafdc45005e0fa0dd783efebc9f1b",
                "0x69abb6043bbea2467f41ccd0144d1b3b4ecd20f4",
                "0x6d297db3471057d7d014d7100a073de2e2656b8f",
                "0x03dd4319019435d8fd5ae5920b96f37989ea410e",
                "0x39ee3a92a5e836ed5a3cceb6b6f00481b5093b3e",
                "0xd0f398854358f8846596c78f8363f3d182e77cc8",
                "0x30ebb71daa827beae71ee325a77ca47daed7ec9b",
                "0x28ccf73f7982c1786b84e243ffbd47f4fb8ae43d",
                "0x05d472b114d57e6035089a58fa997a7940d29a23",
            ),
            NormalizedEventType.MESSAGE_EXECUTION_STATE_CHANGED: (
                "0xdf615ef8d4c64d0ed8fd7824bbed2f6a10245ac9",
                "0xd98e80c79a15e4dbaf4c40b6ccdf690fe619bfbb",
                "0x718672076d6d51e4c76142b37bc99e4945d704a3",
                "0x562a2025e60aa19aa03ea41d70ea1fd3286d1d3b",
                "0x66d84feded0e51aeb47ced1bb2fc0221ae8d7c12",
                "0x6b4b6359dd5b47cdb030e5921456d2a0625a9ebd",
                "0x70c705ff3ecaa04c8c61d581a59a168a1c49c2ec",
                "0x9a3ed7007809cfd666999e439076b4ce4120528d",
                "0x418dcbcf229897d0ccf1b8b464db06c23879fbb4",
                "0x26a10137a54f4ea01d20758ac5adbf9326340fc3",
                "0x91e46cc5590a4b9182e47f40006140a7077dec31",
                "0x95095007d5cc3e7517a1a03c9e228ada5d0bc376",
                "0xcabc2d71dc3172a154a5a34cd706b050e0ef9b6f",
                "0x27a971d482335d0f8d1917451390734f7372a4a3",
                "0x16b9709f8a23b9eb922e8dde7eab1ede7c79f663",
                "0xb62178f8198905d0fa6d640bdb188e4e8143ac4b",
                "0xcb1dbbb4be5aec889c65ff34882f1eab2cd5785b",
                "0xe5f21f43937199d4d57876a83077b3923f68eb76",
                "0x508ea280d46e4796ce0f1acf8beda610c4238db3",
                "0xff49e35626eba28bee1d251782ab75a6ced91c45",
                "0x376c0afc9e64efe0d9202e1f02c3d7f9dc15e404",
                "0x6cdaa2711bdf0b719911bf00588a79fa97bf9264",
                "0x37879ebfcb807f8c397fce2f42dc0f5329ad6823",
                "0x6a3cef8e5ca7135c574f69d0b58dd0ac9db2d892",
                "0xa06e68a11d5694316cc819f2ffd02663e3314c7c",
                "0x60f2788225cee4a94f8e7589931d5a14cbc4367d",
                "0x35c1bb5a9c2f3fa8f8dff470a6be7d362cea1ef3",
                "0x805c292775be43b10cc744ea7e81d9939a08cea4",
                "0xe58074f8f56e23836f088ac8b4f3882c1b4cacbb",
                "0xf4a9dbb7f3fba02e3a244b464e459c32b63857f1",
                "0x9979c2dfeca9051cf7f08274d978984b2db12c60",
                "0xeb3d6956bcf7b1e29634c8cd182fc9fa740bce34",
                "0xf8e38b4503418659f791f2135c4912f85bfb7988",
                "0x4ba0a3bd1e2b70b2fe165a53219e7ef6376849a4",
                "0x51f37b538ad2bcb9eaf884859bf7c5ec58aec885",
                "0x519ee6b83f57df95486aea6e26819cb7b4b8ee99",
                "0xf616733641d420207b8f30db9c4ce39684768991",
                "0x2a9c65aff39758ceaa24dbd1acd1beb3618e6780",
                "0xc69a550470bebc5c3be98a4c3dd26c6add90c64b",
                "0x21159ebda3e6a2437bcd6ef39853042acc436d2d",
                "0x3c5e62cdfd08e23a0961ff2a3155cabb96cbc89d",
                "0x133672c0f0067573254dd7c8c9818a37d6208610",
                "0x0c42a007bf89dc2cafab3fbd2ec1c1ca5bfe7d7c",
                "0xca04169671a81e4fb8768cfad46c347ae65371f1",
                "0x7d38c6363d5e4dfd500a691bc34878b383f58d93",
                "0x61c3f6d72c80a3d1790b213c4cb58c3d4aafccdf",
                "0x74d574d11977fc8d40f8590c419504cbe178adb7",
                "0x18095fbd53184a50c2bb3929a6c62ca328732062",
                "0x45d524b6fe99c005c52c65c578dc0e02d9751083",
                "0x335581943ef47030e52e4fe921d4b72d15a20ab3",
                "0x658d9ae41a9c291de423d3b4b6c064f6dd0e7ed2",
                "0x320a10449556388503fd71d74a16ab52e0bd1deb",
                "0x656e2aa127cb15815a90ef70c6aa7ed449d689ce",
                "0x90388147f034a60adc4fbe9dc93084bab639d047",
                "0xd2f4330dc0f587770f0fcb61f8d96409f4bd23fe",
                "0x502eaaf47ecc410ed5f7b39dd476d0d05ae55864",
                "0xa7e7cb9185ff4a17f54feded3eeb8d09935a879d",
                "0xa3ea5eb15711041fd28950438b5a682392b54e6c",
                "0x77601f272dd2d6481ac3a13942075388097245fb",
                "0x5834e1c639418a4973391126576f550a6996836a",
            ),
        },
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
            NormalizedEventType.RELAYER_REFUND: (
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
    "mayan": {
        "swift_order": {
            NormalizedEventType.ORDER_CREATED: ("0xc38e4e6a15593f908255214653d3d947ca1c2338",),
            NormalizedEventType.ORDER_FULFILLED: ("0xc38e4e6a15593f908255214653d3d947ca1c2338",),
            NormalizedEventType.ORDER_UNLOCKED: ("0xc38e4e6a15593f908255214653d3d947ca1c2338",),
        },
        "forwarder": {
            NormalizedEventType.SWAP_AND_FORWARDED: (
                "0x337685fdab40d39bd02028545a4ffa7d287cc3e2",
                "0x0654874eb7f59c6f5b39931fc45dc45337c967c3",
            ),
            NormalizedEventType.FORWARDED: (
                "0x337685fdab40d39bd02028545a4ffa7d287cc3e2",
                "0x0654874eb7f59c6f5b39931fc45dc45337c967c3",
            ),
        },
    },
    "debridge": {
        "source_order": {
            NormalizedEventType.ORDER_CREATED: ("0xef4fb24ad0916217251f553c0596f8edc630eb66",),
            NormalizedEventType.CLAIMED_UNLOCK: ("0xef4fb24ad0916217251f553c0596f8edc630eb66",),
        },
        "destination_order": {
            NormalizedEventType.ORDER_FULFILLED: ("0xe7351fd770a37282b91d153ee690b63579d6dd7f",),
        },
    },
    "stargate": {},
    "thorchain": {},
    "meter.io": {
        "deposit_execution": {
            NormalizedEventType.DEPOSIT: (
                "0xfd55ebc7bbde603a048648c6eab8775c997c1001",
                "0xa2a22b46b8df38cd7c55e6bf32ea5a32637cf2b1",
            ),
            NormalizedEventType.PROPOSAL_EVENT: (
                "0xf41e7fc4ec990298d36f667b93951c9dba65224e",
                "0xa2a22b46b8df38cd7c55e6bf32ea5a32637cf2b1",
                "0xfd55ebc7bbde603a048648c6eab8775c997c1001",
            ),
            NormalizedEventType.TRANSFER: (
                "0x868892cccedbff0b028f3b3595205ea91b99376b",
                "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
            ),
            NormalizedEventType.INTERNAL_TRANSFER: ("0xfd55ebc7bbde603a048648c6eab8775c997c1001",),
        },
    },
    "qubit": {
        "deposit_mint": {
            NormalizedEventType.DEPOSIT: ("0x20e5e35ba29dc3b540a1aee781d0814d5c77bce6",),
            NormalizedEventType.PROPOSAL_EVENT: ("0x4d8ae68fcae98bf93299548545933c0d273ba23a",),
            NormalizedEventType.TRANSFER: ("0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f",),
        },
    },
    "chainswap": {},  # TODO: add Receive()/bridge handler allowlists when events are normalized.
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
    NOMAD = "nomad"
    THORCHAIN = "thorchain"
    METER_IO = "meter.io"
    PNETWORK = "pnetwork"
    QUBIT = "qubit"
    CHAINSWAP = "chainswap"


MINUTE = 60
HOUR = 60 * MINUTE

BRIDGE_CCTX_TIMEOUTS = {
    "across": BridgeCctxTimeout(typical_seconds=2 * MINUTE, max_seconds=10 * MINUTE),
    "ccip": BridgeCctxTimeout(typical_seconds=10 * MINUTE, max_seconds=60 * MINUTE),
    "cctp": BridgeCctxTimeout(typical_seconds=20 * MINUTE, max_seconds=45 * MINUTE),
    "polygon": BridgeCctxTimeout(typical_seconds=60 * MINUTE, max_seconds=6 * HOUR),
    "ronin": BridgeCctxTimeout(typical_seconds=10 * MINUTE, max_seconds=60 * MINUTE),
    "omnibridge": BridgeCctxTimeout(typical_seconds=30 * MINUTE, max_seconds=2 * HOUR),
    "debridge": BridgeCctxTimeout(typical_seconds=5 * MINUTE, max_seconds=30 * MINUTE),
    "pnetwork": BridgeCctxTimeout(typical_seconds=30 * MINUTE, max_seconds=2 * HOUR),
    "thorchain": BridgeCctxTimeout(typical_seconds=60 * MINUTE, max_seconds=4 * HOUR),
    "qubit": BridgeCctxTimeout(typical_seconds=30 * MINUTE, max_seconds=90 * MINUTE),
    "meter.io": BridgeCctxTimeout(typical_seconds=30 * MINUTE, max_seconds=90 * MINUTE),
    "chainswap": BridgeCctxTimeout(typical_seconds=30 * MINUTE, max_seconds=90 * MINUTE),
    "mayan": BridgeCctxTimeout(typical_seconds=5 * MINUTE, max_seconds=30 * MINUTE),
    "nomad": BridgeCctxTimeout(typical_seconds=30 * MINUTE, max_seconds=2 * HOUR),
}


TIME_THRESHOLDS = {
    # times after which we consider a lock/mint pair to be suspicious if the corresponding mint/lock event has not been observed
    Bridges.RONIN.value: BRIDGE_CCTX_TIMEOUTS[Bridges.RONIN.value].max_seconds,
    Bridges.POLYGON.value: BRIDGE_CCTX_TIMEOUTS[Bridges.POLYGON.value].max_seconds,
    Bridges.OMNIBRIDGE.value: BRIDGE_CCTX_TIMEOUTS[Bridges.OMNIBRIDGE.value].max_seconds,
    Bridges.CCIP.value: BRIDGE_CCTX_TIMEOUTS[Bridges.CCIP.value].max_seconds,
    Bridges.CCTP.value: BRIDGE_CCTX_TIMEOUTS[Bridges.CCTP.value].max_seconds,
    Bridges.ACROSS.value: BRIDGE_CCTX_TIMEOUTS[Bridges.ACROSS.value].max_seconds,
    Bridges.NOMAD.value: BRIDGE_CCTX_TIMEOUTS[Bridges.NOMAD.value].max_seconds,
    Bridges.METER_IO.value: BRIDGE_CCTX_TIMEOUTS[Bridges.METER_IO.value].max_seconds,
    Bridges.PNETWORK.value: BRIDGE_CCTX_TIMEOUTS[Bridges.PNETWORK.value].max_seconds,
    Bridges.QUBIT.value: BRIDGE_CCTX_TIMEOUTS[Bridges.QUBIT.value].max_seconds,
    Bridges.CHAINSWAP.value: BRIDGE_CCTX_TIMEOUTS[Bridges.CHAINSWAP.value].max_seconds,
    Bridges.DEBRIDGE.value: BRIDGE_CCTX_TIMEOUTS[Bridges.DEBRIDGE.value].max_seconds,
    Bridges.MAYAN.value: BRIDGE_CCTX_TIMEOUTS[Bridges.MAYAN.value].max_seconds,
    Bridges.THORCHAIN.value: BRIDGE_CCTX_TIMEOUTS[Bridges.THORCHAIN.value].max_seconds,
}

BlockConfirmationThresholds = {
    Bridges.RONIN.value: 120,
    Bridges.POLYGON.value: 180,
    Bridges.OMNIBRIDGE.value: 20,
    Bridges.CCIP.value: 20,
    Bridges.CCTP.value: 20,
    Bridges.ACROSS.value: 20,
    Bridges.NOMAD.value: 20,
    Bridges.METER_IO.value: 20,  # TODO: use per-chain confirmation thresholds
    Bridges.QUBIT.value: 20,  # TODO: use per-chain confirmation thresholds
    Bridges.CHAINSWAP.value: 20,  # TODO: confirm Ethereum-only threshold for ChainSwap.
}
