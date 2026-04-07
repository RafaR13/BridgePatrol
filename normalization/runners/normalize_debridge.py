from db.repository.bridge_tables.debridge import (
    DeBridgeCreatedOrder,
    DeBridgeFulfilledOrder,
    DeBridgeClaimedUnlock
)
from normalization.mappers.debridge.mapper import map_debridge_created_order, map_debridge_fulfilled_order, map_debridge_claimed_unlock
from .runner import normalize

def normalize_debridge():
    jobs = [
        (
            DeBridgeCreatedOrder,
            "debridge_created_order",
            lambda row: str(row.order_id),
            map_debridge_created_order,
        ),
        (
            DeBridgeFulfilledOrder,
            "debridge_fulfilled_order",
            lambda row: str(row.order_id),
            map_debridge_fulfilled_order,
        ),
        (
            DeBridgeClaimedUnlock,
            "debridge_claimed_unlock",
            lambda row: str(row.order_id),
            map_debridge_claimed_unlock,
        ),
    ]
    normalize(bridge="debridge", jobs=jobs)