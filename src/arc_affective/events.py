"""Minimal versioned research-event contract. Not a physiological data format."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Mapping

SOURCES = frozenset({"synthetic", "webcam", "leap", "muse", "dataset", "application"})
KINDS = frozenset({"signal_quality", "marker", "gesture", "frame_metadata", "task_event", "system_metric"})


@dataclass(frozen=True)
class Event:
    session_id: str
    source: str
    kind: str
    t_monotonic_ns: int
    payload: Mapping[str, Any]
    quality: float = 1.0
    synthetic: bool = True
    schema_version: int = 1

    def validate(self) -> None:
        if self.schema_version != 1:
            raise ValueError("Unsupported schema version")
        if not self.session_id or any(c.isspace() for c in self.session_id):
            raise ValueError("Session ID must be nonempty and contain no whitespace")
        if self.source not in SOURCES or self.kind not in KINDS:
            raise ValueError("Unknown source or kind")
        if isinstance(self.t_monotonic_ns, bool) or not isinstance(self.t_monotonic_ns, int) or self.t_monotonic_ns < 0:
            raise ValueError("Timestamp must be a nonnegative integer")
        if isinstance(self.quality, bool) or not isinstance(self.quality, (float, int)) or not 0.0 <= self.quality <= 1.0:
            raise ValueError("Quality must be between 0 and 1")
        if not isinstance(self.synthetic, bool):
            raise ValueError("Synthetic flag must be a bool")
        if not isinstance(self.payload, Mapping):
            raise ValueError("Payload must be a mapping")

    def json_line(self) -> str:
        self.validate()
        return json.dumps(asdict(self), sort_keys=True, allow_nan=False, ensure_ascii=False)


def save_jsonl(path: str | Path, events: list[Event]) -> None:
    """Write a fully validated, monotonic synthetic or authorized stream locally."""
    path = Path(path)
    previous = -1
    sessions = set()
    lines = []
    for event in events:
        event.validate()
        if event.t_monotonic_ns < previous:
            raise ValueError("Out-of-order events")
        previous = event.t_monotonic_ns
        sessions.add(event.session_id)
        lines.append(event.json_line())
    if len(sessions) > 1:
        raise ValueError("One output file must belong to one session")
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
