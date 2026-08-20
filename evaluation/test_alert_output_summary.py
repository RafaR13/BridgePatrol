from types import SimpleNamespace

from evaluation.markdown_report import build_markdown_report
from signature_detection.constants import SignatureType
from evaluation.evaluation_utils import summarize_alerts


def _alert(bridge: str, cctx_id: str, signature_type, title: str = "Alert title"):
    return SimpleNamespace(
        bridge=bridge,
        correlation_id=cctx_id,
        signature_type=signature_type,
        title=title,
    )


def test_summarize_alerts_groups_by_cctx_and_signature_type():
    summary = summarize_alerts(
        [
            _alert("chainswap", "chainswap:0xdst", SignatureType.MINT_WITHOUT_LOCK),
            _alert("chainswap", "chainswap:0xdst", SignatureType.UNEXPECTED_EVENT_CALLER),
            _alert("chainswap", "chainswap:0xother", SignatureType.MINT_WITHOUT_LOCK),
        ]
    )

    assert summary["alerts_detected"] == 3
    assert summary["alerts_by_cctx"] == {
        "chainswap": {
            "chainswap:0xdst": {
                "alert_count": 2,
                "signature_types": {
                    "MINT_WITHOUT_LOCK": 1,
                    "UNEXPECTED_EVENT_CALLER": 1,
                },
            },
            "chainswap:0xother": {
                "alert_count": 1,
                "signature_types": {"MINT_WITHOUT_LOCK": 1},
            },
        }
    }


def test_markdown_report_renders_alert_summary_by_cctx():
    markdown = build_markdown_report(
        [
            {
                "run_id": "run-1",
                "event_type": "performance_summary",
                "bridge": "chainswap",
                "alerts_detected": 2,
                "alerts_by_bridge": {"chainswap": 2},
                "alerts_by_signature_type": {
                    "MINT_WITHOUT_LOCK": 1,
                    "UNEXPECTED_EVENT_CALLER": 1,
                },
                "alerts_by_cctx": {
                    "chainswap": {
                        "chainswap:0xdst": {
                            "alert_count": 2,
                            "signature_types": {
                                "MINT_WITHOUT_LOCK": 1,
                                "UNEXPECTED_EVENT_CALLER": 1,
                            },
                        }
                    }
                },
            },
            {
                "run_id": "run-1",
                "event_type": "signature_check_timer",
                "bridge": "chainswap",
                "signature_check": "mint_without_lock",
                "alerts_detected": 1,
            },
        ],
        title="Evaluation",
        raw_jsonl_path="report.jsonl",
    )

    assert "| Bridge | CCTX | Alerts | Signature types |" in markdown
    assert "| chainswap | chainswap:0xdst | 2 | MINT_WITHOUT_LOCK, UNEXPECTED_EVENT_CALLER |" in markdown
    assert "| Bridge | Signature check | Unit | CCTX | Event groups | Events/logs | Transactions | Duration ms |" in markdown
