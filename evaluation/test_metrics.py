from evaluation.metrics import (
    calculate_bridge_baseline_metrics,
    calculate_signature_expected_metrics,
)


def test_benign_bridge_extra_incomplete_alerts_do_not_consume_true_negatives():
    metrics = calculate_bridge_baseline_metrics(
        predicted_positive_units_by_bridge={
            "ccip": {f"correlation:missing-{index}" for index in range(108)}
        },
        cctx_analyzed_by_bridge={"ccip": 52},
        expected_positive_bridges=set(),
        complete_cctx_units_by_bridge={"ccip": {f"cctx:{index}" for index in range(52)}},
        predicted_positive_complete_counts_by_bridge={"ccip": 0},
    )

    assert metrics["false_positives"] == 108
    assert metrics["true_negatives"] == 52
    assert metrics["total"] == 160


def test_benign_bridge_mixes_complete_cctx_alerts_with_extra_incomplete_alerts():
    metrics = calculate_bridge_baseline_metrics(
        predicted_positive_units_by_bridge={
            "across": {
                *{f"correlation:complete-tx-{index}" for index in range(8)},
                *{f"correlation:missing-{index}" for index in range(65)},
            }
        },
        cctx_analyzed_by_bridge={"across": 380},
        expected_positive_bridges=set(),
        complete_cctx_units_by_bridge={
            "across": {
                *{f"cctx:{index}" for index in range(380)},
                *{f"correlation:complete-tx-{index}" for index in range(8)},
            }
        },
        predicted_positive_complete_counts_by_bridge={"across": 8},
    )

    assert metrics["false_positives"] == 73
    assert metrics["true_negatives"] == 372
    assert metrics["total"] == 445


def test_partial_attack_bridge_keeps_benign_cctx_as_true_negatives():
    metrics = calculate_bridge_baseline_metrics(
        predicted_positive_units_by_bridge={
            "qubit": {f"cctx:qubit:cctx_{index}" for index in range(4, 20)}
        },
        cctx_analyzed_by_bridge={"qubit": 19},
        expected_positive_bridges=set(),
        complete_cctx_units_by_bridge={
            "qubit": {f"cctx:qubit:cctx_{index}" for index in range(1, 20)}
        },
        expected_positive_units_by_bridge={
            "qubit": {f"cctx:qubit:cctx_{index}" for index in range(4, 20)}
        },
    )

    assert metrics["true_positives"] == 16
    assert metrics["false_negatives"] == 0
    assert metrics["false_positives"] == 0
    assert metrics["true_negatives"] == 3
    assert metrics["total"] == 19


def test_partial_attack_count_keeps_remaining_units_negative():
    metrics = calculate_bridge_baseline_metrics(
        predicted_positive_units_by_bridge={"nomad": {f"cctx:{index}" for index in range(167)}},
        cctx_analyzed_by_bridge={"nomad": 481},
        expected_positive_bridges=set(),
        complete_cctx_units_by_bridge={"nomad": {f"cctx:{index}" for index in range(481)}},
        predicted_positive_complete_counts_by_bridge={"nomad": 167},
        expected_positive_counts_by_bridge={"nomad": 167},
    )

    assert metrics["true_positives"] == 167
    assert metrics["false_negatives"] == 0
    assert metrics["false_positives"] == 0
    assert metrics["true_negatives"] == 314
    assert metrics["total"] == 481


def test_partial_attack_count_counts_extra_predicted_units_in_same_universe():
    metrics = calculate_bridge_baseline_metrics(
        predicted_positive_units_by_bridge={
            "ronin": {
                "cctx:1",
                "correlation:missing-0",
                "correlation:missing-1",
            }
        },
        cctx_analyzed_by_bridge={"ronin": 195},
        expected_positive_bridges=set(),
        complete_cctx_units_by_bridge={"ronin": {f"cctx:{index}" for index in range(193)}},
        predicted_positive_complete_counts_by_bridge={"ronin": 1},
        expected_positive_counts_by_bridge={"ronin": 2},
    )

    assert metrics["true_positives"] == 2
    assert metrics["false_negatives"] == 0
    assert metrics["false_positives"] == 1
    assert metrics["true_negatives"] == 193
    assert metrics["total"] == 196


def test_partial_attack_count_only_uses_expected_window_predictions_as_true_positives():
    metrics = calculate_bridge_baseline_metrics(
        predicted_positive_units_by_bridge={
            "ronin": {
                "cctx:2022-attack",
                "correlation:2025-benign-0",
                "correlation:2025-benign-1",
            }
        },
        cctx_analyzed_by_bridge={"ronin": 195},
        expected_positive_bridges=set(),
        complete_cctx_units_by_bridge={"ronin": {f"cctx:{index}" for index in range(193)}},
        predicted_positive_complete_counts_by_bridge={"ronin": 1},
        expected_positive_counts_by_bridge={"ronin": 2},
        predicted_positive_expected_window_counts_by_bridge={"ronin": 1},
    )

    assert metrics["true_positives"] == 1
    assert metrics["false_negatives"] == 1
    assert metrics["false_positives"] == 2
    assert metrics["true_negatives"] == 193
    assert metrics["total"] == 197


def test_partial_attack_count_extra_alerts_do_not_consume_complete_true_negatives():
    metrics = calculate_bridge_baseline_metrics(
        predicted_positive_units_by_bridge={"nomad": {f"alert:{index}" for index in range(679)}},
        cctx_analyzed_by_bridge={"nomad": 634},
        expected_positive_bridges=set(),
        complete_cctx_units_by_bridge={"nomad": {f"cctx:{index}" for index in range(634)}},
        predicted_positive_complete_counts_by_bridge={"nomad": 5},
        expected_positive_counts_by_bridge={"nomad": 167},
        predicted_positive_expected_window_counts_by_bridge={"nomad": 679},
    )

    assert metrics["true_positives"] == 167
    assert metrics["false_negatives"] == 0
    assert metrics["false_positives"] == 512
    assert metrics["true_negatives"] == 467
    assert metrics["total"] == 1146


def test_signature_expected_metrics_counts_expected_signatures_independently():
    metrics = calculate_signature_expected_metrics(
        predicted_positive_units_by_bridge_signature={
            "thorchain": {
                "CONTRACT_MISMATCH": {f"cctx:{index}" for index in range(9)},
                "AMOUNT_MISMATCH": {f"cctx:{index}" for index in range(9, 50)},
            }
        },
        cctx_analyzed_by_bridge={"thorchain": 50},
        expected_positive_signature_counts_by_bridge={
            "thorchain": {
                "CONTRACT_MISMATCH": 9,
                "AMOUNT_MISMATCH": 41,
            }
        },
        predicted_positive_complete_counts_by_bridge={"thorchain": 0},
    )

    assert metrics["true_positives"] == 50
    assert metrics["false_negatives"] == 0
    assert metrics["false_positives"] == 0
    assert metrics["true_negatives"] == 0
    assert metrics["total"] == 50


def test_signature_expected_metrics_keeps_benign_bridges_as_cctx_negatives():
    metrics = calculate_signature_expected_metrics(
        predicted_positive_units_by_bridge_signature={
            "ccip": {"MINT_WITHOUT_LOCK": {f"correlation:missing-{index}" for index in range(3)}}
        },
        cctx_analyzed_by_bridge={"ccip": 52},
        expected_positive_signature_counts_by_bridge={},
        predicted_positive_complete_counts_by_bridge={"ccip": 0},
    )

    assert metrics["true_positives"] == 0
    assert metrics["false_negatives"] == 0
    assert metrics["false_positives"] == 3
    assert metrics["true_negatives"] == 52
    assert metrics["total"] == 55


def test_signature_expected_metrics_uses_expected_window_for_true_positives():
    metrics = calculate_signature_expected_metrics(
        predicted_positive_units_by_bridge_signature={
            "ronin": {
                "MINT_WITHOUT_LOCK": {
                    "cctx:2022-attack",
                    "correlation:2025-benign-0",
                    "correlation:2025-benign-1",
                }
            }
        },
        cctx_analyzed_by_bridge={"ronin": 195},
        expected_positive_signature_counts_by_bridge={"ronin": {"MINT_WITHOUT_LOCK": 2}},
        predicted_positive_complete_counts_by_bridge={"ronin": 1},
        predicted_positive_expected_window_counts_by_bridge_signature={
            "ronin": {"MINT_WITHOUT_LOCK": 1}
        },
    )

    assert metrics["true_positives"] == 1
    assert metrics["false_negatives"] == 1
    assert metrics["false_positives"] == 2
    assert metrics["true_negatives"] == 193
    assert metrics["total"] == 197
