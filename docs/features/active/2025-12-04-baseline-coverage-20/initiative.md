# 2025-12-04-baseline-coverage - Initiative Overview

- Issue: #20 (Tracking Issue: Establish baseline automated tests & coverage)
- Owner: TBD
- Last Updated: 2026-02-02T11-30

## Goal & Outcomes

Raise test coverage on core logic while preventing regressions. Target 80% coverage on core transform/speakerless flows without blocking on full CLI/UI parity, and enforce a “no merge without tests” standard with regression coverage for bug-prone areas.

## Decomposition (Child Features/Workstreams)

- [x] Enhance core transform coverage (Issue #21) - `../2025-12-04-baseline-coverage/`
- [x] Speakerless grouping heuristics tests (Issue #22) - `../2025-12-04-baseline-coverage/`
- [x] Identity constraints + normalize tests (Issue #23) - `../2025-12-04-baseline-coverage/`
- [ ] 3+ speaker fixtures and regression tests (Issue #24) - `../2025-12-04-baseline-coverage/`
- [ ] End-to-end speakerless + notes CLI tests (Issue #25) - `../2025-12-04-baseline-coverage/`
- [ ] Notes conversion edge case regressions (Issue #26) - `../2025-12-04-baseline-coverage/`
- [ ] Formatter + document parser tests (Issue #27) - `../2025-12-04-baseline-coverage/`
- [x] CI coverage gate + reporting (Issue #28) - `../2025-12-04-baseline-coverage/`

Dependencies: Core logic tests (#21–#23) unblock higher-level regression and E2E coverage (#24–#27). CI gating (#28) should follow stabilization of the new baseline to avoid blocking progress.

## Cross-Cutting Constraints & Assumptions

- Coverage baseline currently ~16% (CLI/UI/legacy paths included); focus on core logic first.
- Do not block on CLI/UI parity while raising core coverage to the target.
- Enforce “no new feature without tests” and “every bug fix ships with a regression test.”
- Coverage must not decrease; enforce locally, add/keep CI gate once baseline improves.
- Use the repo toolchain (Black → Ruff → Pyright → Pytest) for validation.

## Milestones & Status

- M1 Core coverage to 80% (transform + speakerless) - In progress (complete issues #24–#27)
- M2 Regression suite stabilized (notes, 3+ speakers, parser/formatters) - Not started
- M3 CI coverage gate + reporting - Done (Issue #28)
- CLI/UX alignment: end-to-end speakerless + notes CLI tests - Not started (Issue #25)

## Initiative-Level Validation

- End-to-end: CLI tests for speakerless + notes flows covering representative transcripts.
- Integration: formatters + document parser tests over enhanced transcript output.
- Determinism/Regression: coverage must not decrease; regression tests for bug-prone transforms and notes conversion.
- Error handling/Resilience: edge-case notes conversion and 3+ speaker scenarios should remain stable.

## Notes / Follow-Ups

- Coverage snapshot reference (2025-12-04): 617 passed, 1 xfail (3-speaker SpaceX), 16% coverage.
- Baseline command: `poetry run pytest --maxfail=1 --disable-warnings --cov=src/transcript_etl_pipeline --cov-report=term`.
