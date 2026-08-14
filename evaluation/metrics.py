from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable



TRUE_VALUES = {"1", "true", "yes", "y", "sim", "attack", "positive"}


@dataclass(frozen=True)
class AlertKey:
    bridge: str
    signature_type: str
    correlation_id: str


@dataclass(frozen=True)
class ConfusionMatrix:
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int

    @property
    def total(self) -> int:
        return (
            self.true_positives
            + self.false_positives
            + self.true_negatives
            + self.false_negatives
        )


def alert_key_from_alert(alert: Any) -> AlertKey:
    signature_type = getattr(alert.signature_type, "value", alert.signature_type)
    return AlertKey(
        bridge=str(alert.bridge),
        signature_type=str(signature_type),
        correlation_id=str(alert.correlation_id or ""),
    )


def load_expected_labels(path: str | Path) -> dict[AlertKey, bool]:
    labels: dict[AlertKey, bool] = {}
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"bridge", "signature_type", "correlation_id", "expected_alert"}
        missing = required - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"Label CSV is missing columns: {', '.join(sorted(missing))}")

        for row in reader:
            key = AlertKey(
                bridge=row["bridge"],
                signature_type=row["signature_type"],
                correlation_id=row["correlation_id"],
            )
            labels[key] = str(row["expected_alert"]).strip().lower() in TRUE_VALUES
    return labels


def build_confusion_matrix(
    predictions: Iterable[Any],
    labels: dict[AlertKey, bool],
) -> ConfusionMatrix:
    predicted_positive = {alert_key_from_alert(alert) for alert in predictions}
    expected_positive = {key for key, expected in labels.items() if expected}
    expected_negative = {key for key, expected in labels.items() if not expected}

    true_positives = len(predicted_positive & expected_positive)
    false_negatives = len(expected_positive - predicted_positive)
    true_negatives = len(expected_negative - predicted_positive)
    false_positives = len((predicted_positive & expected_negative) | (predicted_positive - set(labels)))

    return ConfusionMatrix(
        true_positives=true_positives,
        false_positives=false_positives,
        true_negatives=true_negatives,
        false_negatives=false_negatives,
    )


def safe_divide(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def calculate_metrics(matrix: ConfusionMatrix) -> dict[str, float | int | None]:
    tp = matrix.true_positives
    fp = matrix.false_positives
    tn = matrix.true_negatives
    fn = matrix.false_negatives

    return {
        "total": matrix.total,
        "true_positives": tp,
        "false_positives": fp,
        "true_negatives": tn,
        "false_negatives": fn,
        "accuracy": safe_divide(tp + tn, matrix.total),
        "precision": safe_divide(tp, tp + fp),
        "recall": safe_divide(tp, tp + fn),
        "false_positive_rate": safe_divide(fp, fp + tn),
    }


def calculate_no_expected_attacks_metrics(
    predictions: Iterable[Any],
    cctx_analyzed: int | None,
) -> dict[str, float | int | None]:
    """Build metrics for benign runs where every analyzed CCTX is expected negative."""
    predicted_positive = {alert_key_from_alert(alert) for alert in predictions}
    false_positives = len(predicted_positive)
    total_negatives = cctx_analyzed or 0
    true_negatives = max(total_negatives - false_positives, 0)

    return calculate_metrics(
        ConfusionMatrix(
            true_positives=0,
            false_positives=false_positives,
            true_negatives=true_negatives,
            false_negatives=0,
        )
    )


def calculate_bridge_baseline_metrics(
    predicted_positive_units_by_bridge: dict[str, set[str]],
    cctx_analyzed_by_bridge: dict[str, int | None],
    expected_positive_bridges: set[str],
    complete_cctx_units_by_bridge: dict[str, set[str]] | None = None,
    predicted_positive_complete_counts_by_bridge: dict[str, int] | None = None,
    expected_positive_units_by_bridge: dict[str, set[str]] | None = None,
    expected_positive_counts_by_bridge: dict[str, int] | None = None,
    predicted_positive_expected_window_counts_by_bridge: dict[str, int] | None = None,
) -> dict[str, float | int | None]:
    """Calculate CCTX-level metrics from bridge-level ground truth.

    Bridges in expected_positive_bridges are treated as attack datasets, where
    every analyzed CCTX is expected positive. Every other bridge is treated as a
    benign dataset, where every analyzed CCTX is expected negative.
    """
    true_positives = 0
    false_positives = 0
    true_negatives = 0
    false_negatives = 0

    for bridge, cctx_count in cctx_analyzed_by_bridge.items():
        total = cctx_count or 0
        predicted_units = predicted_positive_units_by_bridge.get(bridge, set())
        predicted_positive = len(predicted_units)

        explicit_expected_units = (
            expected_positive_units_by_bridge.get(bridge, set())
            if expected_positive_units_by_bridge is not None
            else set()
        )
        explicit_expected_count = (
            expected_positive_counts_by_bridge.get(bridge, 0)
            if expected_positive_counts_by_bridge is not None
            else 0
        )
        if explicit_expected_count:
            expected_negative_count = max(total - explicit_expected_count, 0)
            predicted_on_complete_cctx = (
                predicted_positive_complete_counts_by_bridge.get(bridge, 0)
                if predicted_positive_complete_counts_by_bridge is not None
                else min(predicted_positive, total)
            )
            predicted_in_expected_window = (
                predicted_positive_expected_window_counts_by_bridge.get(
                    bridge,
                    predicted_positive,
                )
                if predicted_positive_expected_window_counts_by_bridge is not None
                else predicted_positive
            )
            bridge_tp = min(predicted_in_expected_window, explicit_expected_count)
            bridge_fp = max(predicted_positive - bridge_tp, 0)
            true_positives += bridge_tp
            false_negatives += max(explicit_expected_count - bridge_tp, 0)
            false_positives += bridge_fp

            true_negatives += max(
                expected_negative_count - max(predicted_on_complete_cctx - bridge_tp, 0),
                0,
            )
        elif explicit_expected_units:
            bridge_tp = len(predicted_units & explicit_expected_units)
            expected_negative_count = max(total - len(explicit_expected_units), 0)
            predicted_negative_units = predicted_units - explicit_expected_units
            true_positives += bridge_tp
            false_negatives += max(len(explicit_expected_units) - bridge_tp, 0)
            false_positives += len(predicted_negative_units)
            if complete_cctx_units_by_bridge is not None:
                complete_units = complete_cctx_units_by_bridge.get(bridge, set())
                predicted_on_expected_negative_cctx = len(
                    predicted_negative_units & complete_units
                )
            else:
                predicted_on_expected_negative_cctx = min(
                    len(predicted_negative_units),
                    expected_negative_count,
                )
            true_negatives += max(
                expected_negative_count - predicted_on_expected_negative_cctx,
                0,
            )
        elif bridge in expected_positive_bridges:
            bridge_tp = min(predicted_positive, total)
            true_positives += bridge_tp
            false_negatives += max(total - bridge_tp, 0)
        else:
            if predicted_positive_complete_counts_by_bridge is not None:
                predicted_on_complete_cctx = predicted_positive_complete_counts_by_bridge.get(
                    bridge,
                    0,
                )
                false_positives += predicted_positive
                true_negatives += max(total - predicted_on_complete_cctx, 0)
            elif complete_cctx_units_by_bridge is not None:
                complete_units = complete_cctx_units_by_bridge.get(bridge, set())
                predicted_on_complete_cctx = len(predicted_units & complete_units)
                false_positives += predicted_positive
                true_negatives += max(total - predicted_on_complete_cctx, 0)
            else:
                bridge_fp = min(predicted_positive, total) if total else predicted_positive
                false_positives += bridge_fp
                true_negatives += max(total - bridge_fp, 0)

    return calculate_metrics(
        ConfusionMatrix(
            true_positives=true_positives,
            false_positives=false_positives,
            true_negatives=true_negatives,
            false_negatives=false_negatives,
        )
    )


def calculate_signature_expected_metrics(
    predicted_positive_units_by_bridge_signature: dict[str, dict[str, set[str]]],
    cctx_analyzed_by_bridge: dict[str, int | None],
    expected_positive_signature_counts_by_bridge: dict[str, dict[str, int]],
    predicted_positive_complete_counts_by_bridge: dict[str, int] | None = None,
    predicted_positive_expected_window_counts_by_bridge_signature: (
        dict[str, dict[str, int]] | None
    ) = None,
) -> dict[str, float | int | None]:
    """Calculate metrics using expected alert counts per bridge and signature type.

    Bridges without expected positive signatures keep the benign bridge behavior:
    every analyzed complete CCTX is an expected negative, and every predicted
    alert is a false positive.
    """
    true_positives = 0
    false_positives = 0
    true_negatives = 0
    false_negatives = 0

    for bridge, cctx_count in cctx_analyzed_by_bridge.items():
        total = cctx_count or 0
        predicted_by_signature = predicted_positive_units_by_bridge_signature.get(
            bridge,
            {},
        )
        predicted_total = sum(len(units) for units in predicted_by_signature.values())
        expected_by_signature = expected_positive_signature_counts_by_bridge.get(
            bridge,
            {},
        )

        if expected_by_signature:
            bridge_tp = 0
            bridge_expected = 0
            bridge_expected_signatures = set(expected_by_signature)

            for signature_type, expected_count in expected_by_signature.items():
                bridge_expected += expected_count
                if predicted_positive_expected_window_counts_by_bridge_signature:
                    predicted_count = (
                        predicted_positive_expected_window_counts_by_bridge_signature
                        .get(bridge, {})
                        .get(signature_type, len(predicted_by_signature.get(signature_type, set())))
                    )
                else:
                    predicted_count = len(predicted_by_signature.get(signature_type, set()))
                bridge_tp += min(predicted_count, expected_count)

            unexpected_predictions = sum(
                len(units)
                for signature_type, units in predicted_by_signature.items()
                if signature_type not in bridge_expected_signatures
            )
            expected_signature_predictions = sum(
                len(predicted_by_signature.get(signature_type, set()))
                for signature_type in bridge_expected_signatures
            )

            true_positives += bridge_tp
            false_negatives += max(bridge_expected - bridge_tp, 0)
            false_positives += max(expected_signature_predictions - bridge_tp, 0)
            false_positives += unexpected_predictions

            expected_negative_count = max(total - bridge_expected, 0)
            predicted_on_complete_cctx = (
                predicted_positive_complete_counts_by_bridge.get(bridge, 0)
                if predicted_positive_complete_counts_by_bridge is not None
                else min(predicted_total, total)
            )
            true_negatives += max(
                expected_negative_count - max(predicted_on_complete_cctx - bridge_tp, 0),
                0,
            )
        else:
            false_positives += predicted_total
            predicted_on_complete_cctx = (
                predicted_positive_complete_counts_by_bridge.get(bridge, 0)
                if predicted_positive_complete_counts_by_bridge is not None
                else min(predicted_total, total)
            )
            true_negatives += max(total - predicted_on_complete_cctx, 0)

    return calculate_metrics(
        ConfusionMatrix(
            true_positives=true_positives,
            false_positives=false_positives,
            true_negatives=true_negatives,
            false_negatives=false_negatives,
        )
    )
