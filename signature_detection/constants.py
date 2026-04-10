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
class BridgeFlow:
    lock: NormalizedEventType | None = None
    mint: NormalizedEventType | None = None
    burn: NormalizedEventType  | None = None
    release: NormalizedEventType  | None = None
    source: NormalizedEventType  | None = None
    destination: NormalizedEventType  | None = None

BRIDGE_EVENT_MAP: Dict[str, BridgeFlow] = {
    "ronin": BridgeFlow(
        lock=NormalizedEventType.DEPOSIT_REQUESTED,
        mint=NormalizedEventType.TOKEN_DEPOSITED,
        burn=NormalizedEventType.WITHDRAWAL_REQUESTED,
        release=NormalizedEventType.TOKEN_WITHDREW
    ),
    "polygon": BridgeFlow(
        lock=NormalizedEventType.DEPOSIT_REQUESTED,
        mint=NormalizedEventType.TOKEN_DEPOSITED,
        burn=NormalizedEventType.WITHDRAWAL_REQUESTED,
        release=NormalizedEventType.TOKEN_WITHDREW
    ),
    "omnibridge": BridgeFlow(
        lock=NormalizedEventType.BRIDGING_INITIATED,
        mint=NormalizedEventType.TOKENS_BRIDGED,
        burn=NormalizedEventType.USER_REQUEST_FOR_AFFIRMATION,
        release=NormalizedEventType.AFFIRMATION_COMPLETED,
    ),
    
    "ccip": BridgeFlow(
        source=NormalizedEventType.MESSAGE_SENT,
        destination=NormalizedEventType.MESSAGE_EXECUTION_STATE_CHANGED,
    ),
    "cctp": BridgeFlow(
        burn=NormalizedEventType.DEPOSIT_FOR_BURN,
        mint=NormalizedEventType.MESSAGE_RECEIVED
    ),
    "across": BridgeFlow(
        source=NormalizedEventType.DEPOSIT_INTENT,
        destination=NormalizedEventType.FILL_EXECUTED,
    )
    # TODO: add mayan and debridge, but they are kinda different
}