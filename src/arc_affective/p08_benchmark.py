"""P08 deterministic virtual-clock queue replay: E0 simulation, not hardware timing."""
from __future__ import annotations

from dataclasses import dataclass
import argparse
import json
import math
import random
from pathlib import Path

POLICIES = ("fifo", "bounded_fifo", "latest_only", "deadline_quality")
SCENARIOS = ("nominal", "dropout", "reconnect", "delay", "corrupt", "combined")
MODALITIES = ("video", "hand", "application")
MIN_QUALITY = 0.35


@dataclass(frozen=True)
class Packet:
    event_id: str
    modality: str
    generated_ns: int
    arrival_ns: int
    service_ns: int
    deadline_ns: int
    quality: float = 0.9

    def validate(self):
        if not self.event_id or self.modality not in MODALITIES:
            raise ValueError("Invalid event identity/modality")
        timing = (self.generated_ns, self.arrival_ns, self.service_ns, self.deadline_ns)
        if any(type(value) is not int for value in timing):
            raise ValueError("Timing must be integer nanoseconds")
        if self.generated_ns < 0 or self.arrival_ns < self.generated_ns:
            raise ValueError("Incompatible virtual timestamps")
        if self.service_ns <= 0 or self.deadline_ns <= 0:
            raise ValueError("Service and deadline must be positive")
        if type(self.quality) not in (int, float) or not math.isfinite(self.quality):
            raise ValueError("Invalid quality")
        if not 0 <= self.quality <= 1:
            raise ValueError("Quality outside [0,1]")


def generate_trace(seed=7, cycles=60, scenario="combined"):
    """Missing events from dropout are NOT counted as attempted ingress."""
    if scenario not in SCENARIOS or cycles <= 0:
        raise ValueError("Invalid scenario or cycle count")
    rng = random.Random(seed)
    events = []
    period = 20_000_000
    for tick in range(cycles):
        for modality in MODALITIES:
            if scenario in ("dropout", "combined") and modality == "hand" and cycles // 3 <= tick < cycles // 2:
                continue
            generated = tick * period
            arrival = generated + rng.randrange(2_000_000)
            if scenario in ("delay", "combined") and modality == "video" and tick % 9 == 0:
                arrival += 3 * period
            if scenario in ("reconnect", "combined") and modality == "hand" and cycles // 2 <= tick < cycles // 2 + 5:
                arrival += (cycles // 2 + 5 - tick) * period
            quality = 0.05 if scenario in ("corrupt", "combined") and tick % 7 == 0 and modality == "video" else 0.9
            events.append(Packet(
                f"{modality}-{tick}", modality, generated, arrival,
                9_000_000 if modality == "video" else 8_000_000,
                100_000_000, quality
            ))
    if scenario == "combined" and events:
        events.append(events[0])  # Deliberate duplicate transport record.
    return events


def percentile(values, p):
    if not values:
        return None
    values = sorted(values)
    position = (len(values) - 1) * p
    low, high = math.floor(position), math.ceil(position)
    return (values[low] + (values[high] - values[low]) * (position - low)) / 1e6


def simulate(events, policy="bounded_fifo", queue_limit=4):
    """Single-server queue; processed+dropped+evicted+invalid == attempted."""
    if policy not in POLICIES or type(queue_limit) is not int or queue_limit <= 0:
        raise ValueError("Unsupported policy or queue limit")
    for event in events:
        event.validate()
    incoming = sorted(enumerate(events), key=lambda x: (x[1].arrival_ns, x[0]))
    waiting = []
    active = None
    finish = None
    seen = set()
    index = 0
    counts = dict(processed=0, dropped=0, evicted=0, invalid=0, on_time_valid=0, processed_late=0)
    latencies, ages = [], []
    peak_waiting = 0

    def dispatch(now):
        nonlocal active, finish
        if active is None and waiting:
            if policy == "deadline_quality":
                k = min(range(len(waiting)), key=lambda j: (
                    waiting[j].arrival_ns + waiting[j].deadline_ns,
                    -waiting[j].quality, waiting[j].event_id
                ))
                active = waiting.pop(k)
            else:
                active = waiting.pop(0)
            finish = max(now, active.arrival_ns) + active.service_ns

    while index < len(incoming) or active is not None or waiting:
        next_arrival = incoming[index][1].arrival_ns if index < len(incoming) else None
        if active is not None and (next_arrival is None or finish <= next_arrival):
            now = finish
            latency = now - active.arrival_ns
            counts["processed"] += 1
            latencies.append(latency)
            ages.append(now - active.generated_ns)
            if latency > active.deadline_ns:
                counts["processed_late"] += 1
            elif active.quality >= MIN_QUALITY:
                counts["on_time_valid"] += 1
            active, finish = None, None
            dispatch(now)
            continue

        item = incoming[index][1]
        index += 1
        now = item.arrival_ns
        if item.event_id in seen:
            counts["invalid"] += 1
            continue
        seen.add(item.event_id)
        if policy == "deadline_quality":
            if item.quality < MIN_QUALITY:
                counts["dropped"] += 1
                continue
            # Optimistic feasibility bound; not a full predictive scheduler.
            earliest = max(now, finish or now) + item.service_ns
            if earliest - now > item.deadline_ns:
                counts["dropped"] += 1
                continue

        if policy == "latest_only":
            old_count = sum(p.modality == item.modality for p in waiting)
            waiting = [p for p in waiting if p.modality != item.modality]
            counts["evicted"] += old_count
        limit = 100_000 if policy == "fifo" else queue_limit
        if len(waiting) >= limit:
            if policy == "latest_only":
                waiting.pop(0)
                counts["evicted"] += 1
            elif policy == "deadline_quality":
                worst = min(range(len(waiting)), key=lambda j: (
                    waiting[j].quality, -waiting[j].arrival_ns
                ))
                if item.quality > waiting[worst].quality:
                    waiting.pop(worst)
                    counts["evicted"] += 1
                else:
                    counts["dropped"] += 1
                    continue
            else:
                counts["dropped"] += 1
                continue
        waiting.append(item)
        peak_waiting = max(peak_waiting, len(waiting))
        dispatch(now)

    n = len(events)
    if sum(counts[key] for key in ("processed", "dropped", "evicted", "invalid")) != n:
        raise AssertionError("Broken ingress accounting")
    return {
        "policy": policy, "attempted": n, **counts,
        "goodput_fraction": counts["on_time_valid"] / n if n else None,
        "drop_fraction": (counts["dropped"] + counts["evicted"]) / n if n else None,
        "latency_ms": {f"p{p}": percentile(latencies, p / 100) for p in (50, 95, 99)},
        "age_p95_ms": percentile(ages, .95),
        "peak_waiting": peak_waiting,
    }


def experiment(seed=7, cycles=60, scenario="combined", queue_limit=4):
    events = generate_trace(seed, cycles, scenario)
    return {
        "schema_version": 1, "evidence": "E0_virtual_simulation_only",
        "timebase": "synthetic_virtual_nanoseconds",
        "host_latency_measured": False, "real_sensor_input": False,
        "scenario": scenario, "seed": seed, "cycles": cycles,
        "queue_limit": queue_limit,
        "attempted_events": len(events),
        "sensor_dropout_not_counted_as_attempted": True,
        "policies": [simulate(events, p, queue_limit) for p in POLICIES],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--cycles", type=int, default=60)
    parser.add_argument("--scenario", choices=SCENARIOS, default="combined")
    parser.add_argument("--queue-limit", type=int, default=4)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = experiment(args.seed, args.cycles, args.scenario, args.queue_limit)
    rendered = json.dumps(report, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if args.output:
        if args.output.exists():
            parser.error("Refusing to overwrite existing report")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
