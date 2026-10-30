# Technical architecture (target; not a claim of implemented hardware drivers)

```text
Public datasets ─────────────────────────────────────────────────┐
Muse Athena* ── adapter ─┐                                       │
Leap Motion ─── adapter ─┼─> validated events / monotonic clock ─┤
RGB webcam ──── adapter ─┘             │                          │
Slayo S9 (2 TX) ─ USB-C receiver ─ adapter (mono/stereo TBD) ────┤
Tobii 5 ─ gaming-only interactive output (no gaze-data logging)   │
                                       v                          v
                          QC + loss/jitter + provenance     offline loaders
                                       │                          │
                          modality features + quality masks <────┘
                                       │
                      held-out validation / uncertainty / abstain
                                       │
              ┌────────────────────────┼──────────────────────────┐
           game policy             robot intent              edge metrics
           (P06)                   + safety governor         (P08)
                                   (P07)
```

* Muse raw EEG/PPG/fNIRS adapters remain **blocked** until licence, SDK, approved data export and achievable clock/marker interfaces are demonstrated. Webcam and Leap are independent fallbacks. **Slayo S9 is an optional audio source only after capture and channel-isolation validation; two transmitters with a shared receiver do not imply stereo.** Tobii 5 research-data logging remains blocked under the stock licence. No device is assumed operational today.

## Event contract v0

Each event is one JSON object in UTF-8 JSONL: `schema_version`, `session_id`, `source`, `kind`, `t_monotonic_ns`, `payload`, `quality` (0..1), `synthetic` (bool). A session-specific monotonic origin is mandatory. UTC/timezone, device timestamp, nominal sampling rate, missing-rate, sample units, calibration ID, trigger ID and firmware/software versions belong in a **private session manifest**, not as arbitrary inference.

Production requirements before any real sensor recording: verified source timestamp semantics, clock-offset estimates and drift bounds; trigger-to-signal latency calibration; drop/duplicate/out-of-order counters; known missing-data mechanism; consent and storage policy; disconnect/reconnect handling. Never compare device sample numbers as if they were synchronized timestamps.

## Components to implement

- Ingestion: separate vendor-compatible plugins; `mock` only is implemented in foundation commit. An optional Slayo USB-audio adapter must advertise verified `mono` or `independent_lr` channel topology, never guess stereo from transmitter count.
- Transform: signal-/image-specific pipelines, metadata and artifact masking.
- Dataset: provenance, labels, subject IDs, sessions, trial IDs and group-safe splits.
- Inference: train-only calibration, uncertainty and abstention; disallow online training without protocol.
- Applications: Unity game adapter, ROS 2 simulation adapter, dashboard with only consented derived metrics.
- Evaluation: leak-safe reproducible scripts with manifests, seeds, CPU/GPU memory, latency p50/p95/p99, failures and confidence intervals.

## Interoperability

Prefer Python analysis (NumPy, SciPy, MNE as *optional user-installed dependencies*), MNE-BIDS where appropriate for EEG, OpenCV/MediaPipe for webcam-derived landmarks when locally permissible, Ultraleap LeapC-compatible bindings for hand tracking, Unity 6 and ROS 2/Gazebo for applications. Do not assume an SDK is compatible with a particular hardware revision before a local probe. Audio can use a local host PCM backend only after sample-rate, channel-map, latency, DSP and consent checks. A mixed mono stream must be treated as mono even if two microphones transmitted into it. Store research events locally; no new server-side API, queue or orchestrator is necessary for this repository.

Related projects: [arc-mobile-eyetracking](https://github.com/MatPomGit/arc-mobile-eyetracking), [arc-hri-safety](https://github.com/MatPomGit/arc-hri-safety), [research-autopilot](https://github.com/MatPomGit/research-autopilot). Integrations are proposed, not established.