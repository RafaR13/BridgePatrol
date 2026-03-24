from normalization.source_models.ccip import (
    CCIPSendRequested,
    CCIPExecutionStateChanged,
)
from normalization.mappers.ccip.mapper import map_ccip_send_requested, map_ccip_execution_state_changed
from .runner import normalize

def normalize_ccip():
    jobs = [
        (
            CCIPSendRequested,
            "ccip_send_requested",
            lambda row: str(row.id),
            map_ccip_send_requested,
        ),
        (
            CCIPExecutionStateChanged,
            "ccip_execution_state_changed",
            lambda row: str(row.id),
            map_ccip_execution_state_changed,
        ),
    ]
    normalize(bridge="ccip", jobs=jobs)