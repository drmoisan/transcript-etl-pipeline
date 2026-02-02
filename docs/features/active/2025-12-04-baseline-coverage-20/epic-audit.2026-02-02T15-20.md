# Epic Audit — 2025-12-04-baseline-coverage-20

Timestamp: 2026-02-02T15-20

## Executive summary

- Epic: `2025-12-04-baseline-coverage-20`
- Investment decision clarity: **PARTIAL**
- MVP definition clarity: **PARTIAL**
- Incremental delivery clarity: **PARTIAL**
- Overall readiness: **NEEDS REVISION** (delivery gaps + policy non-compliance)

### Assumptions & Not Found

- No `change-plan.md` found in repo root or epic folder.
- No epic-level README found in the epic root.
- Business-case templates are not present; documentation gaps noted but treated as non-blocking for merge readiness per delivery-first policy.

## Lean Business Case checklist

| Item | Status | Evidence | Missing / Risk |
| --- | --- | --- | --- |
| Problem / opportunity | PASS | `issue.md` → “Problem / Why”; `initiative.md` → “Goal & Outcomes” | — |
| Target customer / users / stakeholders | PARTIAL | Personas listed in feature `user-story.md` files; no consolidated epic-level stakeholders in `initiative.md` | Non-blocking doc gap; unclear primary decision owner. |
| Proposed approach | PASS | `initiative.md` → “Decomposition (Child Features/Workstreams)” | — |
| Alternatives considered | FAIL | No alternatives section in `initiative.md` or `issue.md` | Non-blocking doc gap; document alternatives when templates mature. |
| MVP definition (scope + done) | PARTIAL | `initiative.md` calls out core coverage goal but lacks explicit module list and evidence gates | Non-blocking doc gap; still affects decision clarity. |
| Leading indicators / success metrics | FAIL | No epic-level metrics table beyond “coverage must not decrease” | Non-blocking doc gap; reduces decision clarity. |
| Cost/effort envelope + constraints | FAIL | No effort estimates or capacity in `initiative.md` | Non-blocking doc gap. |
| Risks + mitigations | PARTIAL | Risks noted in epic/feature docs | Missing policy risk treatment (temporary files, NLTK downloads). |
| Dependencies and decision gates | PARTIAL | Dependencies noted in `initiative.md` + `orchestration.md` | Sequencing criteria for raising coverage gate not explicit. |

## MVP & incremental value mapping

### MVP definition (inferred)

**MVP (inferred):** Raise core logic coverage for transform + speakerless modules and prevent regressions without blocking on CLI/UI parity.

**Evidence:** `initiative.md` → “Goal & Outcomes”, “Milestones & Status”.

### Mapping to features

- **MVP-aligned features**
  - #21 `enhance-tests`
  - #22 `speakerless-heuristics`
  - #23 `identity-normalize`
- **Post-MVP increments**
  - #24 `multi-speaker-fixtures`
  - #25 `e2e-speakerless-notes`
  - #26 `notes-regressions`
  - #27 `formatters-parser`
  - #28 `ci-coverage-gate`

### Gaps impacting delivery

- Core-module coverage targets for #21–#23 are not met (coverage.xml line-rates: enhance 0.4615; identity_constraints 0.1852; normalize 0.1702; speakerless 0.0625; speaker_helpers 0.07008).
- Unit-test policy violations (temporary files, NLTK download) are present in existing tests, blocking merge readiness.

## Decision-quality risks (top 5)

1. **Core acceptance criteria not met for MVP features**
   - Evidence: Coverage below targets for `enhance.py`, `speakerless.py`, `speaker_helpers.py`, `identity_constraints.py`, `normalize.py` in `coverage.xml`.
   - Risk: MVP not deliverable; coverage gate lacks required baseline.
   - Fix: Implement missing tests and raise module coverage to targets.

2. **Policy violations in tests (temporary files + external downloads)**
   - Evidence: `tests/integration/test_cli_e2e_*.py` and formatter tests use `tmp_path`/`tempfile`; `tests/transform/test_speaker_helpers.py` uses `ensure_nltk_data()` which may download.
   - Risk: Non-compliance with unit-test policy; merge blocked.
   - Fix: Refactor tests to avoid filesystem and network dependencies or document an approved exception.

3. **Plan checklists mostly incomplete**
   - Evidence: Most `plan.<timestamp>.md` items remain unchecked; only partial auto-checks completed for #21/#23/#24/#28.
   - Risk: Execution readiness unclear; missing validation steps.
   - Fix: Complete plan tasks or document explicit scope changes.

4. **Epic milestone status mismatch**
   - Evidence: `initiative.md` marks M1 “complete issues #24–#27” while feature plans are “Planned” or “Draft”.
   - Risk: Incorrect sequencing decisions and reporting.
   - Fix: Align milestone status with actual delivery.

5. **CI gate sequencing not tied to acceptance criteria**
   - Evidence: `orchestration.md` suggests sequencing but no clear gate-raise criteria.
   - Risk: Gate increases may block progress or be delayed without metrics.
   - Fix: Add explicit gate ratchet criteria and sequence in orchestration docs.

## Overall recommendation

**NEEDS REVISION** — Documentation gaps are non-blocking, but **delivery gaps and policy violations block merge readiness** until acceptance criteria and plan items are completed and test-policy compliance is restored.
