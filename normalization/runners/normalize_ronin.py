from db.repository.bridge_tables.ronin import (
    RoninDepositRequested,
    RoninTokenDeposited,
    RoninWithdrawalRequested,
    RoninTokenWithdrew
)
from normalization.mappers.ronin.mapper import map_deposit_requested, map_token_deposited, map_withdrawal_requested, map_token_withdrew
from .runner import normalize

def normalize_ronin():
    jobs = [
        (
            RoninDepositRequested,
            "ronin_deposit_requested",
            lambda row: str(row.deposit_id),
            map_deposit_requested,
        ),
        (
            RoninTokenDeposited,
            "ronin_token_deposited",
            lambda row: str(row.deposit_id),
            map_token_deposited,
        ),
        (
            RoninWithdrawalRequested,
            "ronin_withdrawal_requested",
            lambda row: str(row.withdrawal_id),
            map_withdrawal_requested,
        ),
        (
            RoninTokenWithdrew,
            "ronin_token_withdrew",
            lambda row: str(row.withdrawal_id),
            map_token_withdrew,
        ),
    ]
    normalize(bridge="ronin", jobs=jobs)