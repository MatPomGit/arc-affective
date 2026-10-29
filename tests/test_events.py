"""Standard-library offline tests: python -m unittest discover -s tests -v."""
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from arc_affective.events import Event, save_jsonl
from arc_affective.synthetic import generate


class EventTests(unittest.TestCase):
    def test_deterministic_generator(self):
        self.assertEqual(generate(4), generate(4))
        self.assertEqual([e.t_monotonic_ns for e in generate(3)], [0, 20_000_000, 40_000_000])

    def test_invalid_fields(self):
        for overrides in [
            {"quality": float("nan")}, {"quality": 1.5}, {"t_monotonic_ns": True},
            {"t_monotonic_ns": -1}, {"schema_version": 3}, {"source": "tobii"},
            {"synthetic": "yes"}, {"session_id": ""}
        ]:
            with self.subTest(overrides=overrides):
                event = Event("s", "synthetic", "marker", 1, {}, **{k:v for k,v in overrides.items() if k not in {"session_id", "source", "t_monotonic_ns"}}) if False else None
                fields = dict(session_id="s", source="synthetic", kind="marker", t_monotonic_ns=1, payload={})
                fields.update(overrides)
                with self.assertRaises(ValueError):
                    Event(**fields).validate()

    def test_persist_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "events.jsonl"
            save_jsonl(p, generate(3))
            self.assertEqual(len(p.read_text().splitlines()), 3)
            with self.assertRaises(FileExistsError):
                save_jsonl(p, generate(3))

    def test_out_of_order_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            e = generate(3)
            with self.assertRaises(ValueError):
                save_jsonl(Path(tmp) / "e.jsonl", [e[2], e[0]])

    def test_cross_session_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                save_jsonl(Path(tmp) / "e.jsonl", generate(1, "s1") + generate(1, "s2"))


if __name__ == "__main__":
    unittest.main()
