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
