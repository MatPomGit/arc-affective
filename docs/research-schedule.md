# Conditional multi-publication execution schedule (not firm deadlines)
Version 1.0.0 · 2026-10-29

**Time origin:** T0 = first active research sprint after this plan is accepted. Estimates below are **planning bands** assuming focused work; blocked data rights, ethics and access to colleagues can extend them. Milestone dates are not committed and native GitHub due dates have not been set. Parallel work assumes agents can independently progress on non-sensitive, offline code; no requirement to reserve new hardware.

| Wave | Publications | Indicative active windows relative to T0 | Critical output |
|---|---|---|---|
| A | P08, P01, P04 | W1–W16 | Synthetic/signal benchmark, public-data audits, baseline algorithms |
| B | P02, P05 | W5–W24 | Paired fusion only after verified data; Leap task protocol and N-of-1 results |
| C | P03, P06, P07 | W9–W36 | Longitudinal self-study, game controller and simulated robot interface |
| Manuscript review | Each paper independently | As soon as that paper passes M5 | M6 evidence bundle; no pressure to claim unsupported positive result |

## Gate cadence inside each paper

- M0/M1: ~1–3 focused JRA per milestone, rights and protocol freeze.
- M2: ~2–5 JRA, software QA and compatibility; longer if a device SDK is inaccessible.
- M3/M4: ~2–6 JRA per milestone, strong comparators and novel method.
- M5: ~2–8 JRA plus participant scheduling/experiments where needed; number of windows does not increase N.
- M6: ~2–5 JRA, IEEE manuscript, figures, bibliography, independent reproduction and venue assessment.

JRA counts express **separable engineering activities, not working-day promises or automated background execution**. Distinguish throughput by **paper + stage + evidence status**, not issue volume.

## Weekly review checklist

- [ ] Audit new/closed issues and PRs, conflicts and failed tests; **finish active work before opening new PRs**.
- [ ] Check blockers #1–#4, confirm data/legal/ethics requirements per paper before acquisition.
- [ ] Confirm M0–M6 checklist links in eight epics; update evidence IDs and dependencies after a verified merge.
- [ ] Maintain novelty overlap matrix across the eight papers and related projects; revise if literature invalidates claim.
- [ ] Reprioritize only when gate evidence changes, not when an aspirational date passes.

**Decision rule:** If a data source or instrument cannot be legally accessed at zero cost, select a documented legal alternative before proceeding; if no alternative preserves the hypothesis, hold the paper without fabricating results.
