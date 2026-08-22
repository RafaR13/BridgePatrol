from types import SimpleNamespace

from evaluation.evaluation_utils import _prediction_unit_for_alert
from signature_detection.constants import SignatureType


def test_proof_replay_prediction_unit_prefers_destination_cctx():
    alert = SimpleNamespace(
        signature_type=SignatureType.PROOF_REPLAY,
        src_event_id=1,
        dst_event_id=2,
        correlation_id="shared-correlation",
    )

    assert (
        _prediction_unit_for_alert(alert, {1: "source-cctx", 2: "destination-cctx"})
        == "cctx:destination-cctx"
    )


def test_non_replay_prediction_unit_keeps_source_cctx_priority():
    alert = SimpleNamespace(
        signature_type=SignatureType.AMOUNT_MISMATCH,
        src_event_id=1,
        dst_event_id=2,
        correlation_id="shared-correlation",
    )

    assert (
        _prediction_unit_for_alert(alert, {1: "source-cctx", 2: "destination-cctx"})
        == "cctx:source-cctx"
    )
