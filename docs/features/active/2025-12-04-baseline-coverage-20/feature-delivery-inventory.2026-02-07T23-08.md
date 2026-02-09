# Feature Delivery Inventory — 2025-12-04-baseline-coverage-20

Timestamp: 2026-02-07T23-08
Reviewer: epic_review_agent

## Summary Table

| Feature Folder | Issue | Versions | Current Version | Current Plan | Doc Completeness | AC Present? | Dependencies Declared? | Requirements Delivered | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `2025-12-04-enhance-tests-21` | #21 | none | root | `plan.2026-02-02T11-49.md` | complete | Yes | No explicit deps | 3/3 | Coverage evidence + fail-before exception dossier recorded. |
| `2025-12-04-speakerless-heuristics-22` | #22 | none | root | `plan.2026-02-02T12-24.md` | complete | Yes | No explicit deps | 6/6 | Coverage ≥70% for both modules evidenced. |
| `2025-12-04-identity-normalize-23` | #23 | none | root | `plan.2026-02-02T13-08.md` | complete | Yes | No explicit deps | 5/5 | Coverage evidence in `qa-pytest.2026-02-03T18-30.txt`. |
| `2025-12-04-multi-speaker-fixtures-24` | #24 | none | root | `plan.2026-02-02T13-09.md` | complete | Yes | N/A | 5/5 | Fixtures + regression tests + xfail mapping present. |
| `2025-12-04-e2e-speakerless-notes-25` | #25 | none | root | `plan.2026-02-02T12-45.md` | complete | Yes | No explicit deps | 4/4 | In-memory CLI integration tests satisfy unit-test policy constraints. |
| `2025-12-04-notes-regressions-26` | #26 | none | root | `plan.2026-02-02T13-09.md` | complete | Yes | No explicit deps | 3/3 | Fail-before exception dossier + pass-after + coverage evidence recorded. |
| `2025-12-04-formatters-parser-27` | #27 | none | root | `plan.2026-02-02T13-08.md` | complete | Yes | No explicit deps | 4/4 | Coverage ≥70% evidenced with `--cov-fail-under=70`. |
| `2025-12-04-ci-coverage-gate-28` | #28 | none | root | `plan.2025-12-04T11-43.md` | complete | Yes | Yes (ratchet plan) | 5/5 | CI pass/fail evidence captured; ruleset enforcement documented. |

## Alignment Check (Per Feature)

- **#21** supports core transform coverage targets; coverage evidence is schema-valid.
- **#22** supports speakerless heuristic coverage targets and matches initiative core scope.
- **#23** supports identity/normalize coverage targets with evidence from full test run.
- **#24** provides multi-speaker regression fixtures and xfail documentation.
- **#25** provides CLI E2E coverage for speakerless + notes flows with in-memory stubs.
- **#26** provides notes regression coverage with fail-before exception dossier and notes coverage report.
- **#27** provides formatter/parser coverage with explicit coverage floor enforcement.
- **#28** provides CI coverage gating and reporting with pass/fail run evidence and configuration evidence.

## Acceptance Criteria Delivery Verification

### Feature #21 — enhance-tests

**Acceptance Criteria:**
1) Tests fail before and pass after (for previously untested behavior).
2) Speakerless routing and constraint handling scenarios are exercised.
3) Coverage report shows ≥70% for `transform/enhance.py`.

**Status & Evidence:**
- **AC1: Met (Exception accepted)** — Fail-before exception dossier recorded. Evidence: `evidence/regression-testing/fail-before-exception.2026-02-05T13-05.md`.
- **AC2: Met** — Tests in `tests/transform/test_enhance.py` cover routing and constraint scenarios. Evidence: `evidence/regression-testing/pass-after.2026-02-03T18-30.txt`.
- **AC3: Met** — Coverage 100% for module. Evidence: `evidence/remediation-baseline/coverage.2026-02-03T18-30.txt`.

### Feature #22 — speakerless-heuristics

**Acceptance Criteria:**
1) Positive/negative cases for `detect_speaker_changes` heuristics.
2) Addressee reassignment behavior in `resolve_addresses_other_violations`.
3) Similarity grouping behavior in `group_sentences_by_similarity`.
4) Coverage ≥70% for `speakerless.py` and `speaker_helpers.py`.
5) Tests deterministic and avoid filesystem/temp files.
6) Issue #22 updated with evidence.

**Status & Evidence:**
- **AC1–AC3: Met** — Tests in `tests/transform/test_speakerless.py` and `tests/transform/test_speaker_helpers.py`. Evidence: `evidence/remediation-baseline/coverage.2026-02-03T18-30.txt`.
- **AC4: Met** — Coverage 95%/92%. Evidence: `evidence/remediation-baseline/coverage.2026-02-03T18-30.txt`.
- **AC5: Met** — Tests operate on in-memory strings; no file I/O in modules.
- **AC6: Met** — Issue mirror recorded. Evidence: `evidence/issue-updates/issue-22.2026-02-04T11-21.md`.

### Feature #23 — identity-normalize

**Acceptance Criteria:**
1) Unit tests cover main branches and edge cases in `identity_constraints.py` and `normalize.py`.
2) Tests assert explicit constraints and normalized outputs for tricky inputs.
3) Combined coverage ≥75% across both modules.
4) Tests deterministic and avoid filesystem/temp files.
5) Issue #23 updated with evidence.

**Status & Evidence:**
- **AC1–AC2: Met** — Tests in `tests/transform/test_identity_constraints.py` and `tests/transform/test_normalize.py`.
- **AC3: Met** — Coverage: identity_constraints 98%, normalize 100%. Evidence: `evidence/qa-gates/qa-pytest.2026-02-03T18-30.txt`.
- **AC4: Met** — Tests use in-memory strings only.
- **AC5: Met** — Issue mirror recorded. Evidence: `evidence/issue-updates/issue-23.2026-02-04T11-21.md`.

### Feature #24 — multi-speaker-fixtures

**Acceptance Criteria:**
1) Shared fixture module provides deterministic 3+ speaker fixtures (including SpaceX discussion).
2) Regression tests reference shared fixtures and assert grouping/speaker assignment outcomes.
3) Fixture validation tests fail fast on malformed definitions.
4) Known algorithmic gaps captured as `xfail` with documented rationale.
5) Tests deterministic and avoid external dependencies.

**Status & Evidence:**
- **AC1: Met** — Fixtures in `tests/fixtures/multi_speaker.py` (SPACEX, GENERIC_MEETING, TEAM_STANDUP, PANEL).
- **AC2: Met** — `tests/transform/test_multi_speaker_regression.py` uses shared fixtures.
- **AC3: Met** — Fixture validation tests in `TestMultiSpeakerFixtureValidation`.
- **AC4: Met** — `pytest.mark.xfail` with documented reasons in regression suite.
- **AC5: Met** — Tests are in-memory only.

### Feature #25 — e2e-speakerless-notes

**Acceptance Criteria:**
1) Integration tests cover speakerless CLI flows for DOCX/MD/RTF outputs.
2) Integration tests cover notes-only and notes+transcript flows (including update mode).
3) Error handling cases for missing files/invalid args.
4) Output validation asserts stable text markers instead of binary comparisons.

**Status & Evidence:**
- **AC1–AC2: Met** — `tests/integration/test_cli_e2e_speakerless.py` and `tests/integration/test_cli_e2e_notes.py`.
- **AC3: Met** — Error-path tests in both modules (missing files, invalid format).
- **AC4: Met** — In-memory documents validated via text markers in `_document_text` helpers.
- **Run evidence:** `evidence/qa-gates/pytest.2026-02-06T21-54.md`.

### Feature #26 — notes-regressions

**Acceptance Criteria:**
1) Each known notes conversion bug has a failing-before/passing-after regression test.
2) Regression tests demonstrate prior failures and now pass.
3) Coverage on notes-related paths measurably improves.

**Status & Evidence:**
- **AC1: Met (Exception accepted)** — Fail-before exception dossier. Evidence: `evidence/regression-testing/fail-before-exception.2026-02-05T13-15.md`.
- **AC2: Met** — Pass-after run recorded. Evidence: `evidence/regression-testing/pass-after.2026-02-03T18-30.txt`.
- **AC3: Met** — Notes coverage 99%. Evidence: `evidence/regression-testing/notes-coverage.2026-02-05T16-10.txt`.

### Feature #27 — formatters-parser

**Acceptance Criteria:**
1) Tests assert key formatting/spacing rules and parsed structures.
2) Coverage ≥70% for formatter and parser modules.
3) Tests avoid brittle binary DOCX assertions using text/structure checks.
4) Tests deterministic without external dependencies.

**Status & Evidence:**
- **AC1: Met** — Tests in `tests/formatters/` and `tests/document/test_parser_unit.py`.
- **AC2: Met** — Coverage 93.83% with `--cov-fail-under=70`. Evidence: `evidence/remediation-baseline/coverage.2026-02-03T18-30.txt`.
- **AC3: Met** — Assertions use text/structure checks, not binary DOCX diffs.
- **AC4: Met** — Tests are in-memory and deterministic.

### Feature #28 — ci-coverage-gate

**Acceptance Criteria:**
1) CI runs pytest-cov and fails when coverage is below configured floor.
2) CI passes when coverage meets/exceeds the configured floor.
3) CI surfaces coverage results in logs and the GitHub Actions step summary.
4) CI uploads coverage artifacts (HTML report and `coverage.xml`).
5) Documentation explains how to adjust `fail_under` as coverage improves.

**Status & Evidence:**
- **AC1: Met** — Failure evidence shows coverage gate behavior. Evidence: `evidence/qa-gates/ci-run.2026-02-06T22-29.md` (coverage failure message in run output).
- **AC2: Met** — Pass run recorded. Evidence: `evidence/qa-gates/ci-run.2026-02-06T22-28.md`.
- **AC3–AC4: Met** — CI configuration includes coverage summary and artifact upload steps. Evidence: `evidence/qa-gates/ci-config.2026-02-05T14-40.md`.
- **AC5: Met** — Ratchet guidance documented in `spec.md` and `28-ci-coverage-gate.md`.

## Plan Reconciliation

- **Auto-check updates:** None. All plan tasks are already checked and have supporting evidence in canonical folders.
- **Incomplete plan items:** None identified.

## Merge Readiness Posture

- **Ready to execute:** #21–#28.
- **Needs doc/evidence work:** None blocking. (Non-blocking: `28-ci-coverage-gate.md` references a non-canonical pass-evidence filename while canonical pass evidence exists.)
- **Blocked:** None.
