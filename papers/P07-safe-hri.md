# P07 — Intent-Aware Hand and Gaze Interaction With a Deterministic Robot Safety Governor

**Discipline:** robot control, multimodal HRI, safety-critical software. **Authors/participants:** up to 3 authors; prospective participants N<=3 (default N=0 or N=1).

## Research question
Can user hand/gaze commands improve task throughput in simulated teleoperation without exceeding safety constraints under dropout and ambiguity?

## Distinct technical contribution
Formal separation of probabilistic intent inference from deterministic speed/distance constraints, with induced sensor-fault tests.

## Data and feasible instrumentation
ROS 2 + Gazebo simulated mobile manipulator/humanoid; Leap (if verified), webcam gestures/face direction, Tobii 5 only as interactive input if licensed. N=1–3 interaction sessions.

## Experimental design and baselines
Multimodal intent estimate drives requests, not motor actuation directly; independent speed-limit, collision-zone, watchdog, e-stop and deadman control; benchmark scripted and human operator trials, injected packet loss and conflicting commands.

## Primary evaluation metrics
Constraint violation count (must be zero in defined simulator), near misses, action completion, command ambiguity, abort latency, p99 control-loop latency.

## Threats to validity
Simulation does not certify real-robot safety. Gaze tracker licence and intent ground truth remain limited.

## Go/no-go publication gate
No physical robot experiment necessary; simulated constraints and fault tests pass with independent monitor and reproducible logs.

## Agent-sized implementation steps (one JRA each)
- [ ] 1. Define ROS 2 scene, threat/fault model and motion safety invariants.
- [ ] 2. Integrate Leap/webcam intents into request-only topic schema.
- [ ] 3. Run failure injection and compare against single-modality/baseline controls.
- [ ] 4. Audit safety and prepare P07.

## Status
**PLANNED — no measurements, experiments or publication claims completed.** Follow [methods](../docs/methodology.md), [privacy](../docs/governance.md), [hardware limits](../docs/hardware.md), and [portfolio boundaries](../docs/portfolio.md).
