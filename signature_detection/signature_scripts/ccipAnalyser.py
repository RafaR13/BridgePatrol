from db.repository.blockchain_transactions.blockchain_transactions_repository import (
    CCIPBlockchainTransactionRepository,
)
from normalization.event_types import NormalizedEventType
from signature_detection.constants import (
    VERIFIED_CONTRACTS,
)

from .analyser import Analyser
from db.repository.detection_alert.detection_alert_model import DetectionAlert


class CCIPAnalyser(Analyser):
    CCIP_NATIVE_TOKEN = "TODO"

    def __init__(self):
        super().__init__("ccip")

    def fetch_blockchain_transactions(
        self, start_ts: int | None = None, end_ts: int | None = None
    ):
        return CCIPBlockchainTransactionRepository.get_by_time_window(start_ts, end_ts)

    def fetch_latest_transaction_timestamp(self, start_ts: int | None = None):
        return CCIPBlockchainTransactionRepository.get_latest_timestamp(start_ts)

    def analyse_bridge_specific_signatures(self) -> list[DetectionAlert]:
        return self.token_contract_attacks()

    def bridge_specific_signature_checks(self):
        return (("token_contract_attacks", self.token_contract_attacks, ()),)

    def _normalized_value(self, value):
        if value is None:
            return None
        return str(value).lower()

    def _expected_source_contracts(self) -> tuple[str, ...]:
        return VERIFIED_CONTRACTS["ccip"]["message_execution"][NormalizedEventType.MESSAGE_SENT]
