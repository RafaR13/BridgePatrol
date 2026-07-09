from types import SimpleNamespace

import pytest

from db.repository.normalized_event.normalized_event_repository import (
    NormalizedEventRepository,
)
from signature_detection.signature_scripts.analyser import Analyser


class SyntheticAnalyser(Analyser):
    def __init__(self, bridge: str, transactions: list):
        super().__init__(bridge)
        self.transactions = transactions

    def fetch_blockchain_transactions(self):
        return self.transactions

    def analyse_bridge_specific_signatures(self):
        return []


def make_event(
    event_id,
    event_type,
    correlation_id,
    transaction_hash,
    *,
    amount=100,
    recipient="0xrecipient",
    contract_address=None,
    block_number=100,
    timestamp=100,
):
    return SimpleNamespace(
        id=event_id,
        event_type=event_type,
        correlation_id=correlation_id,
        transaction_hash=transaction_hash,
        amount_in=amount,
        amount_out=None,
        token_in="0xtoken",
        token_out=None,
        actor_from="0xsender",
        actor_to=recipient,
        contract_address=contract_address,
        block_number=block_number,
        timestamp=timestamp,
        raw_pk=str(event_id),
        src_blockchain="source",
        dst_blockchain="destination",
        extra_data=None,
    )


def make_transaction(
    transaction_hash,
    *,
    block_number=100,
    timestamp=100,
):
    return SimpleNamespace(
        transaction_hash=transaction_hash,
        block_number=block_number,
        timestamp=timestamp,
        calls=None,
        from_address=None,
        to_address=None,
    )


@pytest.fixture
def synthetic_analysis(monkeypatch):
    events = []

    def get_events_by_event_type(event_type, bridge_name):
        expected_type = getattr(event_type, "value", event_type)
        return [
            event
            for event in events
            if getattr(event.event_type, "value", event.event_type) == expected_type
        ]

    monkeypatch.setattr(
        NormalizedEventRepository,
        "get_events_by_event_type",
        get_events_by_event_type,
    )

    def build(bridge, bridge_events, transactions=None):
        events[:] = bridge_events
        analyser = SyntheticAnalyser(bridge, transactions or [])
        analyser._set_analysis_window()
        return analyser

    return build
