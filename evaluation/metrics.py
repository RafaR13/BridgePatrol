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
        predicted_positive = len(predicted_positive_units_by_bridge.get(bridge, set()))

        if bridge in expected_positive_bridges:
            bridge_tp = min(predicted_positive, total)
            true_positives += bridge_tp
            false_negatives += max(total - bridge_tp, 0)
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
