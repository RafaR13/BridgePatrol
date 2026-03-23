from normalization.source_models.polygon import (
    PolygonLockedToken,
    PolygonStateSynced,
    PolygonExitedToken,
    PolygonTokenDeposited,
    PolygonStateCommitted,
    PolygonBridgeWithdraw,
    PolygonPOLWithdraw
)
from normalization.mappers.polygon.mapper import map_bridge_withdraw,map_exited_token, map_locked_token, map_state_committed, map_state_synced, map_token_deposited, map_pol_withdraw
from .runner import normalize

def normalize_polygon():
    jobs = [
        (
            PolygonStateSynced,
            "polygon_state_synced",
            lambda row: str(row.state_id),
            map_state_synced,
        ),
        (
            PolygonStateCommitted,
            "polygon_state_committed",
            lambda row: str(row.state_id),
            map_state_committed,
        ),
        (
            PolygonLockedToken,
            "polygon_locked_token",
            lambda row: str(row.id) if getattr(row, "id", None) is not None else f"{row.transaction_hash}:{row.depositor}:{row.deposit_receiver}:{row.root_token}:{row.amount}",
            map_locked_token,
        ),
        (
            PolygonExitedToken,
            "polygon_exited_token",
            lambda row: str(row.id) if getattr(row, "id", None) is not None else f"{row.transaction_hash}:{row.exitor}:{row.root_token}:{row.amount}",
            map_exited_token,
        ),
        (
            PolygonTokenDeposited,
            "polygon_token_deposited",
            lambda row: str(row.id) if getattr(row, "id", None) is not None else f"{row.transaction_hash}:{row.user}:{row.root_token}:{row.child_token}:{row.amount}",
            map_token_deposited,
        ),
        (
            PolygonBridgeWithdraw,
            "polygon_bridge_withdraw",
            lambda row: str(row.id) if getattr(row, "id", None) is not None else f"{row.transaction_hash}:{row.user}:{row.root_token}:{row.child_token}:{row.amount}",
            map_bridge_withdraw,
        ),
        (
            PolygonPOLWithdraw,
            "polygon_pol_withdraw",
            lambda row: str(row.id) if getattr(row, "id", None) is not None else f"{row.transaction_hash}:{row.user}:{row.root_token}:{row.child_token}:{row.amount}",
            map_pol_withdraw,
        ),
    ]
    normalize(bridge="polygon", jobs=jobs)