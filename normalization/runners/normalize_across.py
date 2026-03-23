from normalization.source_models.across import (
    AcrossFundsDeposited,
    AcrossFilledRelay,
    AcrossRelayerRefund,
)
from normalization.mappers.across.mapper import map_funds_deposited, map_filled_relay, map_relayer_refund
from .runner import normalize

def normalize_across():
    jobs = [
        (
            AcrossFundsDeposited,
            "across_funds_deposited",
            lambda row: str(row.deposit_id),
            map_funds_deposited,
        ),
        (
            AcrossFilledRelay,
            "across_filled_relay",
            lambda row: str(row.deposit_id),
            map_filled_relay,
        ),
        (
            AcrossRelayerRefund,
            "across_relayer_refund",
            lambda row: f"{row.transaction_hash}:{row.root_bundle_id}:{row.refund_address}",
            map_relayer_refund,
        ),
    ]
    normalize(bridge="across", jobs=jobs)