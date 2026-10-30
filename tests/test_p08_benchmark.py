"""Offline invariants for P08 virtual-time simulation."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from arc_affective.p08_benchmark import (
    Packet, POLICIES, SCENARIOS, generate_trace, simulate, experiment,
)


def packet(id_, t=0, service=7, deadline=20, quality=.9):
    return Packet(id_, "video", t, t, service, deadline, quality)


class TestP08(unittest.TestCase):
    def test_conservation_and_bounds(self):
        for scenario in SCENARIOS:
            events = generate_trace(7, 75, scenario)
            for policy in POLICIES:
                with self.subTest(scenario=scenario, policy=policy):
                    r = simulate(events, policy, queue_limit=2)
                    self.assertEqual(r["attempted"], sum(r[k] for k in (
                        "processed", "dropped", "evicted", "invalid")))
                    self.assertLessEqual(r["on_time_valid"], r["processed"])
                    self.assertLessEqual(r["peak_waiting"], 100000 if policy == "fifo" else 2)

    def test_determinism_and_evidence_label(self):
        self.assertEqual(experiment(12), experiment(12))
        self.assertNotEqual(generate_trace(12), generate_trace(13))
        self.assertEqual(experiment()["evidence"], "E0_virtual_simulation_only")
        self.assertFalse(experiment()["host_latency_measured"])

    def test_duplicates_and_finite_queue(self):
        p = packet("one")
        r = simulate([p, p], "fifo")
        self.assertEqual((r["processed"], r["invalid"]), (1, 1))
        events = [packet(str(i)) for i in range(7)]
        self.assertGreater(simulate(events, "bounded_fifo", 1)["dropped"], 0)
        self.assertGreater(simulate(events, "latest_only", 1)["evicted"], 0)

    def test_quality_goodput_and_latency(self):
        r = simulate([packet("low", quality=.1)], "fifo")
        self.assertEqual(r["processed"], 1)
        self.assertEqual(r["on_time_valid"], 0)
        self.assertEqual(simulate([packet("low", quality=.1)],
                                  "deadline_quality")["dropped"], 1)
        self.assertEqual(simulate([packet("on", 10, service=5, deadline=5)],
                                  "fifo")["latency_ms"]["p99"], 5e-6)
        self.assertEqual(simulate([packet("late", 10, service=6, deadline=5)],
                                  "fifo")["processed_late"], 1)

    def test_empty_and_reject_invalid(self):
        self.assertIsNone(simulate([], "fifo")["goodput_fraction"])
        with self.assertRaises(ValueError):
            experiment(cycles=0)
        with self.assertRaises(ValueError):
            simulate([], "not_a_policy")
        for overrides in ({"quality": float("nan")}, {"quality": -1},
                          {"arrival_ns": -1}, {"deadline_ns": 0},
                          {"source": "tobii"}, {"service_ns": True}):
            fields = dict(event_id="x", modality="video", generated_ns=0,
                          arrival_ns=0, service_ns=1, deadline_ns=1,
                          quality=.9)
            fields.update(overrides)
            if "source" in fields:
                fields["modality"] = fields.pop("source")
            with self.assertRaises(ValueError):
                simulate([Packet(**fields)])


if __name__ == "__main__":
    unittest.main()
