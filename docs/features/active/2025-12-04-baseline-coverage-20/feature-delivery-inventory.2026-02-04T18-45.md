# Feature Delivery Inventory — 2025-12-04-baseline-coverage-20

**Audit Date:** 2026-02-04
**Epic Folder:** `docs/features/active/2025-12-04-baseline-coverage-20`

## Inventory Summary

| Feature Folder | Issue | Current Plan | Docs Complete? | AC Present? | Dependencies Declared? | Requirements Delivered | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `2025-12-04-enhance-tests-21` | #21 | `plan.2026-02-02T11-49.md` | ✅ | ✅ | N/A | 2 Met / 3 | Fail-before evidence incomplete. |
| `2025-12-04-speakerless-heuristics-22` | #22 | `plan.2026-02-02T12-24.md` | ✅ | ✅ | N/A | 5 Met / 6 | Issue update missing. |
| `2025-12-04-identity-normalize-23` | #23 | `plan.2026-02-02T13-08.md` | ✅ | ✅ | N/A | 4 Met / 5 | Issue update missing. |
| `2025-12-04-multi-speaker-fixtures-24` | #24 | `plan.2026-02-02T13-09.md` | ✅ | ✅ | N/A | 5 Met / 5 | XFAIL gaps documented. |
| `2025-12-04-e2e-speakerless-notes-25` | #25 | `plan.2026-02-02T12-45.md` | ✅ | ✅ | N/A | 4 Met / 4 | ACs met via integration tests. |
| `2025-12-04-notes-regressions-26` | #26 | `plan.2026-02-02T13-09.md` | ✅ | ✅ | N/A | 1 Met / 3 (2 Partial) | Fail-before exception needed; issue update missing. |
| `2025-12-04-formatters-parser-27` | #27 | `plan.2026-02-02T13-08.md` | ✅ | ✅ | N/A | 4 Met / 4 | Issue update missing (plan). |
| `2025-12-04-ci-coverage-gate-28` | #28 | `plan.2025-12-04T11-43.md` | ✅ | ✅ | ✅ (`orchestration.md`) | 0 Met / 5 | CI evidence for `ci.yml` not verified. |

## Evidence Classification Notes

- **Verified** evidence includes artifacts with `Timestamp`, `Command`, and `EXIT_CODE` (e.g., `evidence/remediation-baseline/*.txt`).
- **Reported** evidence is doc-only (e.g., `coverage-results.md`) without tool output and **cannot** be used for blocking decisions.
- **Stale** evidence refers to doc-only metrics older than this audit date or lacking commands.

## Acceptance Criteria Verification

### Feature #21 — enhance-tests

**Acceptance Criteria:**
1. Tests fail before and pass after (previously untested behavior).
2. Speakerless routing and constraint handling scenarios are exercised.
3. Coverage report shows $\ge 70\%$ for `transform/enhance.py`.

**Status:**
- AC1: **Partially Met** — pass-after evidence exists, fail-before is documentation-only.
  - Evidence: `evidence/remediation-baseline/pass-after.2026-02-03T18-30.txt` (Verified), `evidence/remediation-baseline/fail-before.2026-02-03T18-30.md` (documentation-only).
- AC2: **Met** — `tests/transform/test_enhance.py` contains characterization tests for speakerless routing/constraints.
- AC3: **Met** — coverage evidence shows 100%.
  - Evidence: `evidence/remediation-baseline/coverage.2026-02-03T18-30.txt` (Verified).

### Feature #22 — speakerless-heuristics

**Acceptance Criteria:**
1. Tests cover positive/negative heuristic cases for `detect_speaker_changes`.
2. Tests cover addressee reassignment follow-through in `resolve_addresses_other_violations`.
3. Tests cover similarity grouping boundary conditions.
4. Coverage for `speakerless.py` and `speaker_helpers.py` is $\ge 70\%$.
5. Tests are deterministic and avoid filesystem/temp files.
6. Issue #22 updated with coverage evidence and links.

**Status:**
- AC1–AC5: **Met** — tests in `tests/transform/test_speakerless.py` and `tests/transform/test_speaker_helpers.py` cover the targeted heuristics with no filesystem use.
- AC4 evidence: `evidence/remediation-baseline/coverage.2026-02-03T18-30.txt` (Verified) shows 92–95%.
- AC6: **Not Met** — issue update evidence not recorded.

### Feature #23 — identity-normalize

**Acceptance Criteria:**
1. Tests cover main branches and edge cases in `identity_constraints.py` and `normalize.py`.
2. Tests assert explicit constraints and normalized outputs for tricky inputs.
3. Combined coverage for the two modules is $\ge 75\%$.
4. Tests deterministic (no filesystem/external dependencies).
5. Issue #23 updated with coverage evidence and test/PR links.

**Status:**
- AC1–AC4: **Met** — tests present in `tests/transform/test_identity_constraints.py` and `tests/transform/test_normalize.py`; no filesystem dependency.
- AC3 evidence: `epic-toolchain.2026-02-04T16-53/pytest-cov.final.txt` (Verified) shows 98% and 100% respectively.
- AC5: **Not Met** — issue update evidence not recorded.

### Feature #24 — multi-speaker-fixtures

**Acceptance Criteria:**
1. Shared fixture module provides deterministic 3+ speaker fixtures (incl. SpaceX).
2. Regression tests reference shared fixtures and assert grouping outcomes.
3. Fixture validation tests fail fast on malformed definitions.
4. Known algorithmic gaps captured as `xfail` with rationale.
5. Tests deterministic without external dependencies.

**Status:** **All Met**
- Evidence: `tests/fixtures/multi_speaker.py` and `tests/transform/test_multi_speaker_regression.py` (code inspection); XFAILs appear in toolchain evidence (`pytest-cov.final.txt`, Verified).

### Feature #25 — e2e-speakerless-notes

**Acceptance Criteria:**
1. Integration tests cover speakerless CLI flows for DOCX/MD/RTF outputs.
2. Integration tests cover notes-only and notes+transcript flows (including update mode).
3. Tests include explicit error cases (missing files, invalid args).
4. Output validation asserts stable text markers (not binary diff).

**Status:** **All Met**
- Evidence: `tests/integration/test_cli_e2e_speakerless.py` and `tests/integration/test_cli_e2e_notes.py` (code inspection) + full suite pass in `epic-toolchain.2026-02-04T16-53/pytest-cov.final.txt` (Verified).

### Feature #26 — notes-regressions

**Acceptance Criteria:**
1. Each known notes bug has a fail-before/passing-after regression test.
2. Regression tests demonstrate prior failures and now pass.
3. Coverage on notes-related paths measurably improves.

**Status:**
- AC1: **Partially Met** — pass-after evidence exists; fail-before relies on an exception dossier.
  - Evidence: `evidence/remediation-baseline/fail-before-exception-dossier.2026-02-04T16-53.md` (Verified) + `evidence/remediation-baseline/pass-after.2026-02-03T18-30.txt` (Verified).
- AC2: **Partially Met** — pass-after evidence exists; fail-before is exception-based.
- AC3: **Met** — `transform/notes.py` shows 99% coverage in notes regression run.
  - Evidence: `evidence/remediation-baseline/coverage.2026-02-03T18-30.txt` (Verified, though the command failed overall coverage).

### Feature #27 — formatters-parser

**Acceptance Criteria:**
1. Tests assert key formatting/spacing rules and parsed structures.
2. Coverage report shows $\ge 70\%$ for formatter and parser modules.
3. Tests avoid binary DOCX assertions (text/structure checks).
4. Tests are deterministic and avoid external dependencies.

**Status:** **All Met**
- Evidence: `tests/formatters/` and `tests/document/` coverage evidence in `evidence/remediation-baseline/coverage.2026-02-03T18-30.txt` (Verified).

### Feature #28 — ci-coverage-gate

**Acceptance Criteria:**
1. CI runs pytest-cov and fails below configured floor.
2. CI passes when coverage meets/exceeds floor.
3. CI surfaces coverage results in logs and step summary.
4. CI uploads HTML and XML coverage artifacts.
5. Documentation explains how to adjust `fail_under` as coverage improves.

**Status:** **Partially Met (Configured; CI run unverified)**
- Evidence: `evidence/qa-gates/ci-config.2026-02-05T14-40.md` confirms coverage steps, artifact uploads, and `fail_under = 15` configuration in `.github/workflows/ci.yml` + `pyproject.toml`.
- Evidence: `evidence/qa-gates/ci-run.2026-02-04T16-53.md` confirms GitHub Actions does not list `ci.yml` on the default branch; no verified CI run demonstrates coverage gate or artifacts yet.

## Plan Reconciliation Notes

- **Auto-checks applied:** None. Existing evidence was sufficient to validate acceptance criteria, but plan tasks requiring exact commands or issue updates remain unchecked.
- **Canon evidence order used:** feature `evidence/regression-testing/` → feature `evidence/qa-gates/` → feature `evidence/remediation-baseline/` → feature `evidence/baseline/` → epic `evidence/regression-testing/` → epic `evidence/qa-gates/` → epic `evidence/remediation-baseline/` → epic `evidence/baseline/`.

## Merge Readiness Posture

**Blocked** due to unmet acceptance criteria in #21, #22, #23, #26, and #28. Remediation inputs are required.
