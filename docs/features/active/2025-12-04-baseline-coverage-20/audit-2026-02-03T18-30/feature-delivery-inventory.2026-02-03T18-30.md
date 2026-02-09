# Feature Delivery Inventory — 2025-12-04-baseline-coverage-20

**Audit Date:** 2026-02-03  
**Epic Root:** `docs/features/active/2025-12-04-baseline-coverage-20/`

## Summary Table

| Feature Folder | Issue | Versions | Current Version | Current Plan | Docs Present (issue/spec/user-story/plan) | AC Present | Dependencies Explicit | Requirements Delivered (Met/Total) | Notes / Risks |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `2025-12-04-enhance-tests-21` | #21 | None | Root | `plan.2026-02-02T11-49.md` | Yes/Yes/Yes/Yes | Yes | Partial (implicit) | 0/3 | Coverage evidence: [coverage.2026-02-03T18-30.txt](2025-12-04-enhance-tests-21/remediation-baseline/coverage.2026-02-03T18-30.txt); QA evidence: not yet captured |
| `2025-12-04-speakerless-heuristics-22` | #22 | None | Root | `plan.2026-02-02T12-24.md` | Yes/Yes/Yes/Yes | Yes | Partial (implicit) | 0/6 | Coverage evidence: [coverage.2026-02-03T18-30.txt](2025-12-04-speakerless-heuristics-22/remediation-baseline/coverage.2026-02-03T18-30.txt); QA evidence: [Black](2025-12-04-speakerless-heuristics-22/remediation-baseline/qa-black.2026-02-03T18-30.txt), [Ruff](2025-12-04-speakerless-heuristics-22/remediation-baseline/qa-ruff.2026-02-03T18-30.txt), [Pyright](2025-12-04-speakerless-heuristics-22/remediation-baseline/qa-pyright.2026-02-03T18-30.txt), [Pytest](2025-12-04-speakerless-heuristics-22/remediation-baseline/qa-pytest.2026-02-03T18-30.txt) |
| `2025-12-04-identity-normalize-23` | #23 | None | Root | `plan.2026-02-02T13-08.md` | Yes/Yes/Yes/Yes | Yes | Partial (implicit) | 0/5 | Coverage evidence: [coverage.2026-02-03T18-30.txt](2025-12-04-identity-normalize-23/remediation-baseline/coverage.2026-02-03T18-30.txt); QA evidence: [Black](2025-12-04-identity-normalize-23/remediation-baseline/qa-black.2026-02-03T18-30.txt), [Ruff](2025-12-04-identity-normalize-23/remediation-baseline/qa-ruff.2026-02-03T18-30.txt), [Pyright](2025-12-04-identity-normalize-23/remediation-baseline/qa-pyright.2026-02-03T18-30.txt), [Pytest](2025-12-04-identity-normalize-23/remediation-baseline/qa-pytest.2026-02-03T18-30.txt) |
| `2025-12-04-multi-speaker-fixtures-24` | #24 | None | Root | `plan.2026-02-02T13-09.md` | Yes/Yes/Yes/Yes | Yes | Partial (implicit) | 4/5 | Coverage evidence: [coverage.2026-02-03T18-30.txt](2025-12-04-multi-speaker-fixtures-24/remediation-baseline/coverage.2026-02-03T18-30.txt); QA evidence: [Black](2025-12-04-multi-speaker-fixtures-24/remediation-baseline/qa-black.2026-02-03T18-30.txt), [Ruff](2025-12-04-multi-speaker-fixtures-24/remediation-baseline/qa-ruff.2026-02-03T18-30.txt), [Pyright](2025-12-04-multi-speaker-fixtures-24/remediation-baseline/qa-pyright.2026-02-03T18-30.txt), [Pytest](2025-12-04-multi-speaker-fixtures-24/remediation-baseline/qa-pytest.2026-02-03T18-30.txt) |
| `2025-12-04-e2e-speakerless-notes-25` | #25 | None | Root | `plan.2026-02-02T12-45.md` | Yes/Yes/Yes/Yes | Yes | Partial (implicit) | 3/4 | Coverage evidence: [coverage.2026-02-03T18-30.txt](2025-12-04-e2e-speakerless-notes-25/remediation-baseline/coverage.2026-02-03T18-30.txt); QA evidence: not yet captured |
| `2025-12-04-notes-regressions-26` | #26 | None | Root | `plan.2026-02-02T13-09.md` | Yes/Yes/Yes/Yes | Yes | Partial (implicit) | 0/3 | Coverage evidence: [coverage.2026-02-03T18-30.txt](2025-12-04-notes-regressions-26/remediation-baseline/coverage.2026-02-03T18-30.txt); QA evidence: [Black](2025-12-04-notes-regressions-26/remediation-baseline/qa-black.2026-02-03T18-30.txt), [Ruff](2025-12-04-notes-regressions-26/remediation-baseline/qa-ruff.2026-02-03T18-30.txt), [Pyright](2025-12-04-notes-regressions-26/remediation-baseline/qa-pyright.2026-02-03T18-30.txt), [Pytest](2025-12-04-notes-regressions-26/remediation-baseline/qa-pytest.2026-02-03T18-30.txt) |
| `2025-12-04-formatters-parser-27` | #27 | None | Root | `plan.2026-02-02T13-08.md` | Yes/Yes/Yes/Yes | Yes | Partial (implicit) | 3/4 | Coverage evidence: [coverage.2026-02-03T18-30.txt](2025-12-04-formatters-parser-27/remediation-baseline/coverage.2026-02-03T18-30.txt); QA evidence: [Black](2025-12-04-formatters-parser-27/remediation-baseline/qa-black.2026-02-03T18-30.txt), [Ruff](2025-12-04-formatters-parser-27/remediation-baseline/qa-ruff.2026-02-03T18-30.txt), [Pyright](2025-12-04-formatters-parser-27/remediation-baseline/qa-pyright.2026-02-03T18-30.txt), [Pytest](2025-12-04-formatters-parser-27/remediation-baseline/qa-pytest.2026-02-03T18-30.txt) |
| `2025-12-04-ci-coverage-gate-28` | #28 | None | Root | `plan.2025-12-04T11-43.md` | Yes/Yes/Yes/Yes | Yes | Partial (implicit) | 2/5 | CI coverage gate spec + evidence: [ci-run.2026-02-03T18-30.md](2025-12-04-ci-coverage-gate-28/remediation-baseline/ci-run.2026-02-03T18-30.md); QA evidence: not yet captured |

## Alignment Check (Per Feature)

- **#21 enhance-tests:** Supports core transform coverage objective. Acceptance criteria are testable. Dependencies implicit (none stated). Plan is actionable but includes unchecked evidence tasks.
- **#22 speakerless-heuristics:** Supports speakerless coverage objective. Acceptance criteria testable. Plan actionable; evidence tasks incomplete.
- **#23 identity-normalize:** Supports core transform coverage objective. Acceptance criteria testable. Plan actionable; issue update incomplete.
- **#24 multi-speaker-fixtures:** Supports regression/fixtures objective. Acceptance criteria testable. Plan actionable; prompt update and toolchain evidence incomplete.
- **#25 e2e-speakerless-notes:** Supports E2E objective. Acceptance criteria testable. Plan actionable; several scenarios incomplete.
- **#26 notes-regressions:** Supports regression objective. Acceptance criteria testable. Plan actionable; regression “fail-before” evidence missing.
- **#27 formatters-parser:** Supports formatter/parser coverage objective. Acceptance criteria testable. Plan actionable; issue update incomplete.
- **#28 ci-coverage-gate:** Supports CI gating objective. Acceptance criteria testable with CI evidence; missing CI run + docs update.

## Acceptance Criteria Delivery Verification

### Feature #21 — enhance-tests

**Acceptance Criteria Source:** `user-story.md`

| Criterion | Status | Evidence | Verification | Notes |
| --- | --- | --- | --- | --- |
| Tests fail before and pass after (previously untested behavior). | ❌ Not Met | No before/after evidence recorded in plan or issue. | N/A | Requires explicit regression reproduction evidence. |
| Speakerless routing and constraint handling scenarios are exercised. | ⚠️ Partially Met | `tests/transform/test_enhance.py` includes routing/constraint tests (e.g., lines 311, 343). | Not run in this audit. | Evidence: `tests/transform/test_enhance.py`. |
| Coverage report shows ≥ 70% for `transform/enhance.py`. | ⚠️ Partially Met (Reported, Stale) | Coverage output in plan `plan.2026-02-02T11-49.md` (no timestamp; Linux output). | Not verified in this audit. | Treat as Stale per evidence rules. |

### Feature #22 — speakerless-heuristics

**Acceptance Criteria Source:** `user-story.md`

| Criterion | Status | Evidence | Verification | Notes |
| --- | --- | --- | --- | --- |
| Tests cover positive/negative cases for `detect_speaker_changes` heuristics. | ⚠️ Partially Met | Tests exist in `tests/transform/test_speakerless.py` (e.g., line 147). | Not run in this audit. | Coverage not verified. |
| Tests cover addressee reassignment in `resolve_addresses_other_violations`. | ⚠️ Partially Met | Helper tests exist in `tests/transform/test_speaker_helpers.py` (e.g., line 301). | Not run in this audit. | Evidence from file only. |
| Tests cover similarity grouping behavior in `group_sentences_by_similarity`. | ⚠️ Partially Met | Plan indicates tests; not verified in this audit. | Not run in this audit. | Needs explicit evidence. |
| Coverage ≥ 70% for `speakerless.py` + `speaker_helpers.py`. | ❌ Not Met | No coverage report recorded. | N/A | Evidence missing. |
| Tests deterministic; no filesystem/temp files. | ⚠️ Partially Met | Plan/spec state tests are deterministic; no run evidence. | Not run in this audit. | Needs validation. |
| Issue #22 updated with coverage evidence and links. | ❌ Not Met | No issue update evidence. | N/A | Blocking for readiness. |

### Feature #23 — identity-normalize

**Acceptance Criteria Source:** `user-story.md`

| Criterion | Status | Evidence | Verification | Notes |
| --- | --- | --- | --- | --- |
| Tests cover main branches/edge cases. | ⚠️ Partially Met | Tests exist in `tests/transform/test_identity_constraints.py` and `tests/transform/test_normalize.py`. | Not run in this audit. | File evidence only. |
| Tests assert explicit constraints/normalized outputs. | ⚠️ Partially Met | Test names/fixtures indicate explicit assertions. | Not run in this audit. | File evidence only. |
| Combined coverage ≥ 75%. | ⚠️ Partially Met (Reported, Stale) | `coverage-results.md` shows 98–100% (no timestamp). | Not verified in this audit. | Treat as Stale. |
| Tests deterministic, no filesystem/temp files. | ⚠️ Partially Met | Spec claims deterministic tests. | Not run in this audit. | Needs validation. |
| Issue #23 updated with coverage evidence and links. | ❌ Not Met | No issue update evidence. | N/A | Blocking for readiness. |

### Feature #24 — multi-speaker-fixtures

**Acceptance Criteria Source:** `user-story.md`

| Criterion | Status | Evidence | Verification | Notes |
| --- | --- | --- | --- | --- |
| Shared fixture module provides deterministic 3+ speaker fixtures (incl. SpaceX). | ✅ Met | `tests/fixtures/multi_speaker.py` exists. | Not run in this audit. | File evidence only. |
| Regression tests reference fixtures and assert grouping outcomes. | ✅ Met | `tests/transform/test_multi_speaker_regression.py` imports fixtures (lines ~22–83). | Not run in this audit. | File evidence only. |
| Fixture validation tests fail fast on malformed definitions. | ✅ Met | Validation tests in `test_multi_speaker_regression.py` (lines ~37–69). | Not run in this audit. | File evidence only. |
| Known gaps captured as `xfail` with rationale. | ✅ Met | `pytest.mark.xfail` entries in `test_multi_speaker_regression.py` (multiple lines). | Not run in this audit. | File evidence only. |
| Tests run without external dependencies and are deterministic. | ⚠️ Partially Met | Spec indicates deterministic tests; no run evidence. | Not run in this audit. | Needs validation. |

### Feature #25 — e2e-speakerless-notes

**Acceptance Criteria Source:** `user-story.md`

| Criterion | Status | Evidence | Verification | Notes |
| --- | --- | --- | --- | --- |
| Integration tests cover speakerless CLI DOCX/MD/RTF outputs and pass reliably. | ⚠️ Partially Met | Tests cover DOCX (3-speaker), MD (spacex), RTF (panel) in `tests/integration/test_cli_e2e_speakerless.py`. | Not run in this audit. | Some planned scenarios missing (panel DOCX, extra MD/RTF). |
| Tests cover notes-only and notes+transcript flows (incl. update mode). | ✅ Met | `tests/integration/test_cli_e2e_notes.py` includes notes-only, notes+transcript, update-mode flows. | Not run in this audit. | File evidence only. |
| Tests include error handling for missing files/invalid args. | ✅ Met | Error handling tests in `test_cli_e2e_speakerless.py` and `test_cli_e2e_notes.py` (error classes). | Not run in this audit. | File evidence only. |
| Output validation uses text markers (not binary). | ✅ Met | Tests assert text content from in-memory documents. | Not run in this audit. | File evidence only. |

### Feature #26 — notes-regressions

**Acceptance Criteria Source:** `user-story.md`

| Criterion | Status | Evidence | Verification | Notes |
| --- | --- | --- | --- | --- |
| Each known notes bug has fail-before/pass-after regression test. | ❌ Not Met | No before/after evidence captured. | N/A | Requires explicit regression evidence. |
| Regression tests demonstrate prior failures and now pass. | ❌ Not Met | No before/after evidence recorded. | N/A | Requires explicit evidence. |
| Coverage on notes-related paths improves. | ⚠️ Partially Met (Reported) | Plan references `coverage.xml` but no timestamp or command output. | Not verified in this audit. | Treat as Stale. |

### Feature #27 — formatters-parser

**Acceptance Criteria Source:** `user-story.md`

| Criterion | Status | Evidence | Verification | Notes |
| --- | --- | --- | --- | --- |
| Tests assert key formatting/spacing rules and parsed structures. | ✅ Met | Tests in `tests/formatters/` and `tests/document/test_parser_unit.py`. | Not run in this audit. | File evidence only. |
| Coverage ≥ 70% for formatters/parser modules. | ⚠️ Partially Met (Reported) | Plan reports coverage pass (P5-T1) but no output included. | Not verified in this audit. | Treat as Stale. |
| Tests avoid binary DOCX assertions. | ✅ Met | Fake/in-memory tests in formatter test files. | Not run in this audit. | File evidence only. |
| Tests deterministic without external deps. | ✅ Met | Test patterns use in-memory fakes/stubs. | Not run in this audit. | File evidence only. |

### Feature #28 — ci-coverage-gate

**Acceptance Criteria Source:** `user-story.md`

| Criterion | Status | Evidence | Verification | Notes |
| --- | --- | --- | --- | --- |
| CI runs pytest-cov and fails below floor (`fail_under = 15`). | ⚠️ Partially Met | `.github/workflows/ci.yml` contains coverage steps; `pyproject.toml` has `fail_under = 15`. | CI run not available in audit. | Needs CI run evidence. |
| CI passes when coverage meets/exceeds floor. | ❓ Unknown | No CI run evidence recorded. | N/A | Requires CI run. |
| CI surfaces coverage results in logs/step summary. | ⚠️ Partially Met | Step summary commands in `ci.yml` (coverage report). | CI run not available. | Needs CI run evidence. |
| CI uploads HTML/XML coverage artifacts. | ⚠️ Partially Met | Artifact upload steps in `ci.yml`. | CI run not available. | Needs CI run evidence. |
| Docs explain how to adjust `fail_under` as coverage improves. | ❌ Not Met | No doc update recorded in feature folder. | N/A | Blocking for readiness. |

## Plan Reconciliation Summary

No additional plan checkboxes were auto-checked during this audit. Several plans still have unchecked tasks in evidence/QA/update phases (e.g., issues #21–#28), which remain blocking for readiness.

## Merge Readiness Posture

**Status:** ❌ **BLOCKED**

**Blocking gaps:**
- Multiple acceptance criteria remain Not Met or Partially Met with stale/absent evidence.
- Coverage evidence is stale or missing across multiple features.
- Issue updates and documentation updates required by plans remain incomplete.
