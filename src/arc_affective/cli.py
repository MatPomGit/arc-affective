"""Run a synthetic smoke test without hardware, cloud services or data downloads."""
import argparse
from .events import save_jsonl
from .synthetic import generate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="data/synthetic-demo.jsonl")
    parser.add_argument("--events", type=int, default=100)
    args = parser.parse_args()
    events = generate(args.events)
    save_jsonl(args.output, events)
    print(f"Wrote {len(events)} SYNTHETIC events to {args.output}; no affect inference performed.")


if __name__ == "__main__":
    main()
