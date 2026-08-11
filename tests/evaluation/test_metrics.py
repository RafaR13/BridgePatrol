from evaluation.metrics import calculate_bridge_baseline_metrics


def test_benign_bridge_extra_incomplete_alerts_do_not_consume_true_negatives():
    metrics = calculate_bridge_baseline_metrics(
        predicted_positive_units_by_bridge={
            "ccip": {f"correlation:missing-{index}" for index in range(108)}
        },
        cctx_analyzed_by_bridge={"ccip": 52},
        expected_positive_bridges=set(),
        complete_cctx_units_by_bridge={
            "ccip": {f"cctx:{index}" for index in range(52)}
        },
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
        predicted_positive_units_by_bridge={
            "nomad": {f"cctx:{index}" for index in range(382)}
        },
        cctx_analyzed_by_bridge={"nomad": 481},
        expected_positive_bridges=set(),
        complete_cctx_units_by_bridge={
            "nomad": {f"cctx:{index}" for index in range(481)}
        },
        predicted_positive_complete_counts_by_bridge={"nomad": 382},
        expected_positive_counts_by_bridge={"nomad": 382},
    )

    assert metrics["true_positives"] == 382
    assert metrics["false_negatives"] == 0
    assert metrics["false_positives"] == 0
    assert metrics["true_negatives"] == 99
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
        complete_cctx_units_by_bridge={
            "ronin": {f"cctx:{index}" for index in range(193)}
        },
        predicted_positive_complete_counts_by_bridge={"ronin": 1},
        expected_positive_counts_by_bridge={"ronin": 2},
    )

    assert metrics["true_positives"] == 2
    assert metrics["false_negatives"] == 0
    assert metrics["false_positives"] == 1
    assert metrics["true_negatives"] == 192
    assert metrics["total"] == 195
