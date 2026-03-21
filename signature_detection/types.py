from enum import Enum

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
    FILL_WITHOUT_SOURCE = "FILL_WITHOUT_SOURCE"
    SOURCE_WITHOUT_FILL = "SOURCE_WITHOUT_FILL"
    AMOUNT_MISMATCH = "AMOUNT_MISMATCH"

class Bridges(Enum): # supported bridges (TODO: move this somewhere else)
    STARGATE = "stargate"
    CCTP = "cctp"
    CCIP = "ccip"
    ACROSS = "across"
    POLYGON = "polygon"
    RONIN = "ronin"
    OMNIBRIDGE = "omnibridge"
    DEBRIDGE = "debridge"
    MAYAN = "mayan"

ALLOWED_SOURCE_DESTINATION_PAIRS = {
    "across": {
        "source": NormalizedEventType.DEPOSIT_INTENT,
        "dest": NormalizedEventType.FILL_EXECUTED
    }
    # TODO: add more
}

"""SETTLEMENT_SOURCE_TYPES = {
    NormalizedEventType.DEPOSIT_INTENT,
    NormalizedEventType.LOCK,
    NormalizedEventType.LOCK_REQUESTED,
    NormalizedEventType.BURN_INITIATED,
    NormalizedEventType.BURN_REQUESTED,
    NormalizedEventType.ORDER_CREATED,
    NormalizedEventType.BRIDGE_INITIATED,
    NormalizedEventType.MESSAGE_SENT,
    NormalizedEventType.SWAP_INITIATED,
}

SETTLEMENT_DESTINATION_TYPES = {
    NormalizedEventType.FILL_EXECUTED,
    NormalizedEventType.MINT,
    NormalizedEventType.MINT_EXECUTED,
    NormalizedEventType.RELEASE,
    NormalizedEventType.RELEASE_EXECUTED,
    NormalizedEventType.ORDER_FULFILLED,
    NormalizedEventType.BRIDGE_COMPLETED,
    NormalizedEventType.MESSAGE_EXECUTED,
    NormalizedEventType.SWAP_EXECUTED,
}"""