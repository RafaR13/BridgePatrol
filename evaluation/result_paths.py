from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


DEFAULT_RESULTS_ROOT = Path("evaluation/results")


@dataclass(frozen=True)
class EvaluationResultPaths:
    timestamp: str
    directory: Path
    details_jsonl: Path

    def artifact_path(self, bridge: str, suffix: str) -> Path:
        safe_bridge = (
            bridge.strip().lower().replace("/", "_").replace(" ", "_").replace(":", "_")
        )
        return self.directory / f"evaluation_{safe_bridge}_{self.timestamp}.{suffix}"


def build_evaluation_result_paths(
    results_dir: str | Path | None = None,
    details_output: str | Path | None = None,
    evaluation_type: str | None = None,
) -> EvaluationResultPaths:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    directory_name = (
        f"evaluation_results_{timestamp}_{evaluation_type}"
        if evaluation_type
        else f"evaluation_results_{timestamp}"
    )
    directory = (
        Path(results_dir)
        if results_dir is not None
        else DEFAULT_RESULTS_ROOT / directory_name
    )
    details_jsonl = (
        Path(details_output)
        if details_output is not None
        else directory / f"evaluation_details_{timestamp}.jsonl"
    )
    directory.mkdir(parents=True, exist_ok=True)
    details_jsonl.parent.mkdir(parents=True, exist_ok=True)

    return EvaluationResultPaths(
        timestamp=timestamp,
        directory=directory,
        details_jsonl=details_jsonl,
    )
