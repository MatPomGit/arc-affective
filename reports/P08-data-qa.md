# P08 M2 virtual replay: implementation evidence

Version 0.1.0, 2026-10-30. Status: **E0 synthetic simulation; NOT real-clock data or an M2 completion claim**. Relates to #41, #29, #12.

The new standard-library module `src/arc_affective/p08_benchmark.py` constructs timestamped metadata for video, hand, and application event types. These are **fabricated events with prescribed service durations**, not sensor recordings or neural-inference measurements. Four policies operate on exactly the same seeded trace: finite emergency-cap FIFO, bounded FIFO, latest-only, and candidate deadline/quality admission. Fault scenarios: nominal, sensor dropout, reconnect arrival burst, transport delay, quality degradation and combined with duplicate ID. During dropout, absent sensor events do not count as attempted ingress; the rate of missing source events requires a separate expected-schedule metric in the later real study.

**Reproduce locally** (Python >=3.10):

```bash
PYTHONPATH=src python -m arc_affective.p08_benchmark --seed 7 --cycles 75 --scenario combined --queue-limit 4
PYTHONPATH=src python -m arc_affective.p08_benchmark --seed 7 --output results/p08-virtual-run.json
python -m unittest discover -s tests -p test_p08_benchmark.py -v
```

PowerShell: `$env:PYTHONPATH="src"; python -m arc_affective.p08_benchmark --seed 7`.

**Measurement semantics:** simulated latency = virtual completion minus virtual arrival, in milliseconds; virtual age = completion minus virtual generation. Goodput = on-time processed events with synthetic quality at least 0.35 / all attempted ingress. Processed+dropped+evicted+invalid must equal attempted. Processed-late is a subset of processed. The percentile is linearly interpolated (type 7). Dropping many events may lower conditional latency while worsening goodput. Results stay in the ignored `results/` directory; output never overwrites existing files.

**Not yet done:** physical clock integration, real dispatch loop, profiling on host, true CPU inference, observable memory/energy, paired independent repeat experiments, queue-aware future deadline estimation, rights/ethics for physical sensors. The candidate algorithm and deadlines are not frozen or demonstrated novel. Do not promote E0 virtual timestamps as measured p99 on Raspberry Pi/Windows. Keep #41 open.
