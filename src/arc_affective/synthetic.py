"""Deterministic synthetic event stream for I/O tests only."""
from .events import Event


def generate(n: int, session_id: str = "synthetic-test") -> list[Event]:
    if n < 0:
        raise ValueError("n must be nonnegative")
    return [
        Event(
            session_id=session_id,
            source="synthetic",
            kind="signal_quality",
            t_monotonic_ns=i * 20_000_000,
            payload={"channel": "mock", "index": i, "value": (i % 11) / 10},
            quality=1.0,
            synthetic=True,
        )
        for i in range(n)
    ]
