from __future__ import annotations

import json
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4


class EvaluationReporter:
    def __init__(self, output_path: str | Path | None, run_id: str | None = None):
        self.output_path = Path(output_path) if output_path else None
        self.run_id = run_id or str(uuid4())

    def write(self, event_type: str, payload: dict[str, Any]) -> None:
        if self.output_path is None:
            return

        record = {
            "run_id": self.run_id,
            "event_type": event_type,
            "recorded_at_ns": time.time_ns(),
            **payload,
        }
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with self.output_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, default=str, sort_keys=True) + "\n")

    @contextmanager
    def timer(self, event_type: str, payload: dict[str, Any]) -> Iterator[dict[str, Any]]:
        start_ns = time.perf_counter_ns()
        timer_payload = dict(payload)
        try:
            yield timer_payload
        finally:
            end_ns = time.perf_counter_ns()
            timer_payload["duration_ns"] = end_ns - start_ns
            timer_payload["duration_ms"] = (end_ns - start_ns) / 1_000_000
            self.write(event_type, timer_payload)


def build_reporter(
    output_path: str | Path | None,
    run_id: str | None = None,
) -> EvaluationReporter | None:
    if output_path is None:
        return None
    return EvaluationReporter(output_path=output_path, run_id=run_id)
