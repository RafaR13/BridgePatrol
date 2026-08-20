import json

import pytest

from normalization.event_types import NormalizedEventType
from signature_detection.constants import (
    BRIDGE_EVENT_MAP,
    EXPECTED_EVENT_CALLERS,
    VERIFIED_CONTRACTS,
    Bridges,
    SignatureType,
)
from signature_detection.runners.run_signature_detection import ANALYSER_BY_BRIDGE

from conftest import make_event, make_transaction


CONFIGURED_DEPOSIT_FLOWS = [
    (bridge, flow)
    for bridge, config in BRIDGE_EVENT_MAP.items()
    for flow in config.deposits
]

AMOUNT_CHECKED_FLOWS = [
    (bridge, flow_type, flow)
    for bridge, config in BRIDGE_EVENT_MAP.items()
    for flow_type, flows in (
        ("deposits", config.deposits),
        ("withdrawals", config.withdrawals),
    )
    for flow in flows
    if flow.amount_check
]

VERIFIED_FLOW_CONTRACTS = [
    (bridge, flow, event_type, contracts)
    for bridge, config in BRIDGE_EVENT_MAP.items()
    for flow in (*config.deposits, *config.withdrawals)
    for event_type, contracts in VERIFIED_CONTRACTS.get(bridge, {})
    .get(flow.name, {})
    .items()
    if event_type in (flow.source, flow.destination)
    if contracts
]


def signature_types(alerts):
    return {alert.signature_type for alert in alerts}


def event_for_flow(event_id, event_type, correlation_id, tx_hash, flow, **kwargs):
    event = make_event(
        event_id,
        event_type,
        correlation_id,
        tx_hash,
        **kwargs,
    )
    key_fields = (
        flow.source_key if event_type == flow.source else flow.destination_key
    )
    for field in key_fields:
        if field == "correlation_id":
            continue
        if field.startswith("extra_data."):
            key = field.split(".", 1)[1]
            extra_data = json.loads(event.extra_data) if event.extra_data else {}
            extra_data[key] = correlation_id
            event.extra_data = json.dumps(extra_data)
            continue
        setattr(event, field, correlation_id)
    return event


def test_every_supported_bridge_has_an_analyser():
    supported_bridges = {bridge.value for bridge in Bridges}
    assert set(ANALYSER_BY_BRIDGE) == supported_bridges


def test_unconfigured_bridges_have_an_explicit_todo():
    for bridge, config in BRIDGE_EVENT_MAP.items():
        if config.deposits or config.withdrawals:
            continue
        assert config.todo, f"{bridge} has no event flows and no explanatory TODO"


@pytest.mark.parametrize(
    ("bridge", "flow"),
    CONFIGURED_DEPOSIT_FLOWS,
    ids=lambda value: getattr(value, "name", value),
)
@pytest.mark.skip(reason="lock_without_mint is currently disabled in analyse_all")
def test_detects_lock_without_mint_for_every_configured_deposit_flow(
    synthetic_analysis,
    bridge,
    flow,
):
    source = event_for_flow(1, flow.source, "attack-1", "0xsource", flow)
    analyser = synthetic_analysis(
        bridge,
        [source],
        [
            make_transaction("0xsource", block_number=100, timestamp=100),
            make_transaction("0xlatest", block_number=1000, timestamp=10_000),
        ],
    )

    alerts = analyser.lock_without_mint(bridge)

    assert SignatureType.LOCK_WITHOUT_MINT in signature_types(alerts)
    assert alerts[0].correlation_id == "attack-1"
    assert alerts[0].src_event_id == source.id


@pytest.mark.parametrize(
    ("bridge", "flow"),
    CONFIGURED_DEPOSIT_FLOWS,
    ids=lambda value: getattr(value, "name", value),
)
def test_detects_mint_without_lock_for_every_configured_deposit_flow(
    synthetic_analysis,
    bridge,
    flow,
):
    destination = event_for_flow(
        2,
        flow.destination,
        "attack-2",
        "0xdestination",
        flow,
    )
    analyser = synthetic_analysis(
        bridge,
        [destination],
        [
            make_transaction("0xdestination", block_number=100, timestamp=100),
            make_transaction("0xlatest", block_number=1000, timestamp=10_000),
        ],
    )

    alerts = analyser.mint_without_lock(bridge)

    assert SignatureType.MINT_WITHOUT_LOCK in signature_types(alerts)
    assert alerts[0].correlation_id == "attack-2"
    assert alerts[0].dst_event_id == destination.id


def test_lock_without_mint_probability_uses_end_boundary(synthetic_analysis):
    analyser = synthetic_analysis("across", [])
    analyser._set_analysis_window(start_ts=1_000, end_ts=2_000)

    probability = analyser._missing_pair_attack_probability(
        "across",
        1_010,
        missing_side="destination",
    )

    assert "990s from the end analysis-window boundary" in probability
    assert "missing_side=destination" in probability


def test_mint_without_lock_probability_uses_start_boundary(synthetic_analysis):
    analyser = synthetic_analysis("across", [])
    analyser._set_analysis_window(start_ts=1_000, end_ts=2_000)

    probability = analyser._missing_pair_attack_probability(
        "across",
        1_990,
        missing_side="source",
    )

    assert "990s from the start analysis-window boundary" in probability
    assert "missing_side=source" in probability


@pytest.mark.parametrize(
    ("bridge", "flow_type", "flow"),
    AMOUNT_CHECKED_FLOWS,
    ids=lambda value: getattr(value, "name", value),
)
def test_detects_amount_inflation_for_every_amount_checked_flow(
    synthetic_analysis,
    bridge,
    flow_type,
    flow,
):
    source = event_for_flow(
        1,
        flow.source,
        "attack-3",
        "0xsource",
        flow,
        amount=100,
    )
    destination = event_for_flow(
        2,
        flow.destination,
        "attack-3",
        "0xdestination",
        flow,
        amount=150,
    )
    analyser = synthetic_analysis(bridge, [source, destination])

    alerts = analyser.amount_mismatch(bridge)
    alerts.extend(
        analyser.over_mint(bridge)
        if flow_type == "deposits"
        else analyser.over_release(bridge)
    )

    expected_inflation = (
        SignatureType.OVER_MINT
        if flow_type == "deposits"
        else SignatureType.OVER_RELEASE
    )
    assert SignatureType.AMOUNT_MISMATCH in signature_types(alerts)
    assert expected_inflation in signature_types(alerts)


@pytest.mark.parametrize(
    ("bridge", "flow"),
    CONFIGURED_DEPOSIT_FLOWS,
    ids=lambda value: getattr(value, "name", value),
)
def test_detects_recipient_mismatch_for_every_configured_deposit_flow(
    synthetic_analysis,
    bridge,
    flow,
):
    source = event_for_flow(
        1,
        flow.source,
        "attack-4",
        "0xsource",
        flow,
        recipient="0xexpected",
    )
    destination = event_for_flow(
        2,
        flow.destination,
        "attack-4",
        "0xdestination",
        flow,
        recipient="0xattacker",
    )
    analyser = synthetic_analysis(bridge, [source, destination])

    alerts = analyser.recipient_mismatch(bridge)

    assert SignatureType.RECIPIENT_MISMATCH in signature_types(alerts)


@pytest.mark.parametrize(
    ("bridge", "flow"),
    CONFIGURED_DEPOSIT_FLOWS,
    ids=lambda value: getattr(value, "name", value),
)
def test_detects_replayed_destination_for_every_configured_deposit_flow(
    synthetic_analysis,
    bridge,
    flow,
):
    source = event_for_flow(1, flow.source, "attack-5", "0xsource", flow)
    first_destination = event_for_flow(
        2,
        flow.destination,
        "attack-5",
        "0xdestination-1",
        flow,
    )
    replayed_destination = event_for_flow(
        3,
        flow.destination,
        "attack-5",
        "0xdestination-2",
        flow,
    )
    analyser = synthetic_analysis(
        bridge,
        [source, first_destination, replayed_destination],
    )

    alerts = analyser.detect_replays(bridge, flow)

    assert SignatureType.PROOF_REPLAY in signature_types(alerts)
    assert {alert.dst_event_id for alert in alerts} == {2, 3}


@pytest.mark.parametrize(
    ("bridge", "flow", "event_type", "contracts"),
    VERIFIED_FLOW_CONTRACTS,
    ids=lambda value: getattr(value, "name", value),
)
@pytest.mark.skip(reason="unauthorized_contracts is currently disabled in analyse_all")
def test_detects_events_from_unauthorized_contracts(
    synthetic_analysis,
    bridge,
    flow,
    event_type,
    contracts,
):
    event = event_for_flow(
        1,
        event_type,
        "attack-6",
        "0xmalicious",
        flow,
        contract_address="0xmalicious",
    )
    analyser = synthetic_analysis(bridge, [event])

    alerts = analyser.unauthorized_contracts(bridge)

    assert SignatureType.UNAUTHORIZED_CONTRACT in signature_types(alerts)
    assert "0xmalicious" not in {contract.lower() for contract in contracts}


@pytest.mark.parametrize(
    ("bridge", "flow"),
    CONFIGURED_DEPOSIT_FLOWS,
    ids=lambda value: getattr(value, "name", value),
)
def test_valid_pair_does_not_raise_pairing_or_payload_alerts(
    synthetic_analysis,
    bridge,
    flow,
):
    source = event_for_flow(1, flow.source, "valid-1", "0xsource", flow)
    destination = event_for_flow(
        2,
        flow.destination,
        "valid-1",
        "0xdestination",
        flow,
    )
    analyser = synthetic_analysis(bridge, [source, destination])

    alerts = []
    alerts.extend(analyser.lock_without_mint(bridge))
    alerts.extend(analyser.mint_without_lock(bridge))
    alerts.extend(analyser.recipient_mismatch(bridge))
    alerts.extend(analyser.amount_mismatch(bridge))
    alerts.extend(analyser.detect_replays(bridge, flow))

    assert alerts == []


def test_qubit_uses_related_transfer_for_amount_checks(synthetic_analysis):
    flow = BRIDGE_EVENT_MAP["qubit"].deposits[0]
    source = event_for_flow(
        1,
        flow.source,
        "73",
        "0xsource",
        flow,
        amount=100,
    )
    proposal = event_for_flow(
        2,
        flow.destination,
        "73",
        "0xdestination",
        flow,
        amount=None,
    )
    transfer = make_event(
        3,
        NormalizedEventType.TRANSFER,
        "73",
        "0xdestination",
        amount=150,
    )
    analyser = synthetic_analysis("qubit", [source, proposal, transfer])

    alerts = analyser.amount_mismatch("qubit")
    alerts.extend(analyser.over_mint("qubit"))

    assert SignatureType.AMOUNT_MISMATCH in signature_types(alerts)
    assert SignatureType.OVER_MINT in signature_types(alerts)
    assert {alert.dst_event_id for alert in alerts} == {transfer.id}


def test_thorchain_deposit_without_transfer_accepts_matching_tx_value(synthetic_analysis):
    event = make_event(
        1,
        NormalizedEventType.DEPOSIT,
        "thorchain-deposit",
        "0xsource",
        amount=100,
        token_in="0x0000000000000000000000000000000000000000",
        src_blockchain="ethereum",
        contract_address="0xc145990e84155416144c532e31f89b840ca8c2ce",
    )
    analyser = synthetic_analysis(
        "thorchain",
        [event],
        [make_transaction("0xsource", value=100)],
    )

    assert analyser.token_contract_attacks() == []


def test_thorchain_deposit_without_transfer_flags_tx_value_mismatch(synthetic_analysis):
    event = make_event(
        1,
        NormalizedEventType.DEPOSIT,
        "thorchain-deposit",
        "0xsource",
        amount=100,
        token_in="0x0000000000000000000000000000000000000000",
        src_blockchain="ethereum",
        contract_address="0xc145990e84155416144c532e31f89b840ca8c2ce",
    )
    analyser = synthetic_analysis(
        "thorchain",
        [event],
        [make_transaction("0xsource", value=200)],
    )

    alerts = analyser.token_contract_attacks()

    assert signature_types(alerts) == {SignatureType.AMOUNT_MISMATCH}
    assert alerts[0].src_event_id == event.id


@pytest.mark.parametrize(
    "movement_type",
    (NormalizedEventType.TRANSFER, NormalizedEventType.INTERNAL_TRANSFER),
)
def test_meter_pairs_deposit_with_proposal_for_both_movement_types(
    synthetic_analysis,
    movement_type,
):
    flow = BRIDGE_EVENT_MAP["meter.io"].deposits[0]
    source = event_for_flow(1, flow.source, "1", "0xsource", flow)
    proposal = event_for_flow(
        2,
        flow.destination,
        "1",
        "0xdestination",
        flow,
    )
    movement = make_event(
        3,
        movement_type,
        "1",
        "0xdestination",
    )
    analyser = synthetic_analysis("meter.io", [source, proposal, movement])

    assert analyser.lock_without_mint("meter.io") == []
    assert analyser.mint_without_lock("meter.io") == []


def test_event_caller_check_accepts_expected_internal_caller(synthetic_analysis):
    flow = BRIDGE_EVENT_MAP["polygon"].deposits[1]
    event = event_for_flow(
        1,
        NormalizedEventType.TOKEN_DEPOSITED,
        "deposit-1",
        "0xdestination",
        flow,
        contract_address="0xd9c7c4ed4b66858301d0cb28cc88bf655fe34861",
    )
    tx = make_transaction("0xdestination")
    tx.calls = [
        {
            "from": "0xa6fa4fb5f76172d178d61b04b0ecd319c5d1c0aa",
            "to": "0xd9c7c4ed4b66858301d0cb28cc88bf655fe34861",
            "type": "CALL",
        }
    ]
    analyser = synthetic_analysis("polygon", [event], [tx])

    assert analyser.check_event_callers() == []


def test_event_caller_check_flags_unexpected_internal_caller(synthetic_analysis):
    flow = BRIDGE_EVENT_MAP["polygon"].deposits[1]
    event = event_for_flow(
        1,
        NormalizedEventType.TOKEN_DEPOSITED,
        "deposit-1",
        "0xdestination",
        flow,
        contract_address="0xd9c7c4ed4b66858301d0cb28cc88bf655fe34861",
    )
    tx = make_transaction("0xdestination")
    tx.calls = [
        {
            "from": "0xattacker",
            "to": "0xd9c7c4ed4b66858301d0cb28cc88bf655fe34861",
            "type": "CALL",
        }
    ]
    analyser = synthetic_analysis("polygon", [event], [tx])

    alerts = analyser.check_event_callers()

    assert SignatureType.UNEXPECTED_EVENT_CALLER in signature_types(alerts)
    assert alerts[0].dst_event_id == event.id


def test_event_caller_check_includes_related_destination_events(synthetic_analysis):
    flow = BRIDGE_EVENT_MAP["qubit"].deposits[0]
    proposal = event_for_flow(
        1,
        flow.destination,
        "73",
        "0xdestination",
        flow,
        contract_address="0x4d8ae68fcae98bf93299548545933c0d273ba23a",
    )
    transfer = make_event(
        2,
        NormalizedEventType.TRANSFER,
        "73",
        "0xdestination",
        contract_address="0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f",
    )
    tx = make_transaction("0xdestination")
    tx.calls = [
        {
            "from": "0x4d8ae68fcae98bf93299548545933c0d273ba23a",
            "to": "0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f",
            "type": "CALL",
        }
    ]
    analyser = synthetic_analysis("qubit", [proposal, transfer], [tx])

    assert analyser._expected_callers_for_event(transfer) == {
        EXPECTED_EVENT_CALLERS["qubit"]["Transfer"][
            "0x2f422fe9ea622049d6f73f81a906b9b8cff03b7f"
        ][0]
    }
    assert analyser.check_event_callers() == []
