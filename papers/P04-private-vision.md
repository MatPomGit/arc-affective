# P04 — Privacy-Preserving Facial Behaviour Estimation on Commodity RGB Cameras

**Discipline:** computer vision, privacy-aware inference, edge ML. **Authors/participants:** up to 3 authors; prospective participants N<=3 (default N=0 or N=1).

## Research question
What performance and system costs remain when facial pixels are never persisted?

## Distinct technical contribution
Compare ephemeral landmarks-only pipelines with on-device image inference for privacy/utility/latency trade-offs.

## Data and feasible instrumentation
Licensed Aff-Wild2 or AFEW-VA annotations after access; optional local non-recorded webcam N=1 for deployment timing.

## Experimental design and baselines
Separate facial AU/landmark estimation from affect target inference; frame-private flow; compare landmarks-only, compact video model and no-video baseline; benchmark asynchrony, illumination and occlusion. Explicitly avoid face identity recognition.

## Primary evaluation metrics
CCC valence/arousal where labels valid, AU F1, p95 latency, RAM, energy when measurable, retention audit, privacy design verification.

## Threats to validity
Facial expressivity is not emotional ground truth; landmark streams can themselves be identifying; dataset use restrictions.

## Go/no-go publication gate
Verify all frame persistence disabled in default path, scientifically meaningful baseline and explicit facial proxy limitations.

## Agent-sized implementation steps (one JRA each)
- [ ] 1. Secure legally usable facial video benchmark and annotation semantics.
- [ ] 2. Implement no-persistence webcam landmarks flow and privacy threat model.
- [ ] 3. Benchmark accuracy/latency/occlusion and encrypted local outputs.
- [ ] 4. Audit privacy and write P04.

## Status
**PLANNED — no measurements, experiments or publication claims completed.** Follow [methods](../docs/methodology.md), [privacy](../docs/governance.md), [hardware limits](../docs/hardware.md), and [portfolio boundaries](../docs/portfolio.md).
