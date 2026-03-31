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
    lock: NormalizedEventType
    mint: NormalizedEventType
    burn: NormalizedEventType
    release: NormalizedEventType

BRIDGE_EVENT_MAP: Dict[str, BridgeFlow] = {
    "ronin": BridgeFlow(
        lock=NormalizedEventType.DEPOSIT_REQUESTED,
        mint=NormalizedEventType.TOKEN_DEPOSITED,
        burn=NormalizedEventType.WITHDRAWAL_REQUESTED,
        release=NormalizedEventType.TOKEN_WITHDREW
    )
}