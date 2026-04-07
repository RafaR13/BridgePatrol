from db.repository.bridge_tables.cctp import (
    CCTPDepositForBurn,
    CCTPMessageReceived
)

from normalization.mappers.cctp.mapper import map_deposit_for_burn,map_message_received
from .runner import normalize

def normalize_cctp():
    jobs = [
        (
            CCTPDepositForBurn,
            "cctp_deposit_for_burn",
            lambda row: str(row.id) if getattr(row, "id", None) is not None else row.transaction_hash,
            map_deposit_for_burn,
        ),
        (
            CCTPMessageReceived,
            "cctp_message_received",
            lambda row: str(row.id) if getattr(row, "id", None) is not None else row.transaction_hash,
            map_message_received,
        ),
    ]
    normalize(bridge="cctp", jobs=jobs)