# 2025-12-04-baseline-coverage - Initiative Overview

- Issue: #20 (Tracking Issue: Establish baseline automated tests & coverage)
- Owner: Dan Moisan
- Last Updated: 2026-02-02T11-30

## Goal & Outcomes

Raise test coverage on core logic while preventing regressions. Target 80% coverage on core transform/speakerless flows without blocking on full CLI/UI parity, and enforce a “no merge without tests” standard with regression coverage for bug-prone areas.

## MVP Scope & Metrics

MVP scope focuses on core transformation and formatting modules needed for deterministic transcript and notes processing:

- `src/transcript_etl_pipeline/transform/enhance.py`
- `src/transcript_etl_pipeline/transform/speakerless.py`
- `src/transcript_etl_pipeline/transform/speaker_helpers.py`
- `src/transcript_etl_pipeline/transform/identity_constraints.py`
- `src/transcript_etl_pipeline/transform/normalize.py`
- `src/transcript_etl_pipeline/transform/notes.py`
- `src/transcript_etl_pipeline/document/parser.py`
- `src/transcript_etl_pipeline/formatters/docx_formatter.py`
- `src/transcript_etl_pipeline/formatters/md_formatter.py`
- `src/transcript_etl_pipeline/formatters/rtf_formatter.py`

Coverage targets (MVP):

| Module / Group | Target |
| --- | --- |
| `enhance.py` | ≥ 70% |
| `speakerless.py` + `speaker_helpers.py` | ≥ 70% each |
| `identity_constraints.py` + `normalize.py` | ≥ 75% combined |
| `notes.py` | ≥ 70% |
| `docx_formatter.py`, `md_formatter.py`, `rtf_formatter.py`, `document/parser.py` | ≥ 70% each |

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

## Resource Lockup (Estimate)

- Primary: 1 engineer at ~0.5–1.0 FTE for 2–3 weeks to close evidence gaps and complete #24–#27.
- Review/approval: lightweight reviewer availability (~1–2 hours per milestone) for evidence and doc updates.
- Note: timeline assumes no new scope additions and stable CI/tooling.

## Stakeholders & Users

- Primary user: maintainer/developer responsible for pipeline quality gates.
- Secondary users: contributors who add new transforms/formatters and need clear coverage expectations.
- Stakeholders: repo owner, CI maintainers, and reviewers who validate evidence and coverage thresholds.

## Proposed Approach & Tradeoffs

- Approach: prioritize deterministic unit tests for core transforms, then expand to regression/E2E coverage and CI gating.
- Tradeoff: defer full CLI/UI parity to avoid blocking core coverage improvements.
- Tradeoff: allow incremental coverage increases per module rather than a single repo-wide target.

## Risks & Mitigations

- Risk: CI gate blocks progress due to existing low coverage.
	- Mitigation: ratchet `fail_under` upward only after baseline evidence is captured.
- Risk: E2E tests become flaky due to fixture or environment variance.
	- Mitigation: keep fixtures deterministic and isolate external dependencies.
- Risk: Evidence files overwrite pre-development baselines.
	- Mitigation: capture remediation evidence in `remediation-baseline/` folders.

## Milestones & Status

- M1 Core coverage to 80% (transform + speakerless) - Planned
- M2 Regression suite stabilized (notes, 3+ speakers, parser/formatters) - Planned
- M3 CI coverage gate + reporting - Planned (Issue #28)
- CLI/UX alignment: end-to-end speakerless + notes CLI tests - Planned (Issue #25)

## Initiative-Level Validation

- End-to-end: CLI tests for speakerless + notes flows covering representative transcripts.
- Integration: formatters + document parser tests over enhanced transcript output.
- Determinism/Regression: coverage must not decrease; regression tests for bug-prone transforms and notes conversion.
- Error handling/Resilience: edge-case notes conversion and 3+ speaker scenarios should remain stable.

## Notes / Follow-Ups

- Coverage snapshot reference (2025-12-04): 617 passed, 1 xfail (3-speaker SpaceX), 16% coverage.
- Baseline command: `poetry run pytest --maxfail=1 --disable-warnings --cov=src/transcript_etl_pipeline --cov-report=term`.
