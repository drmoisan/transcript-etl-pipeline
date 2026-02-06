# Epic Audit — 2025-12-04-baseline-coverage-20

Audit Timestamp: 2026-02-05T15-30
Epic Root: `docs/features/active/2025-12-04-baseline-coverage-20`

## Executive Summary

- **Epic:** 2025-12-04-baseline-coverage-20 (Issue #20)
- **Resource lockup clarity:** PASS
  - Evidence: Initiative includes estimate and review needs. (`initiative.md`)
- **Objective + scope clarity:** PASS
  - Evidence: Goal, MVP modules, and scope boundaries are explicit. (`initiative.md`)
- **Sequencing + dependency clarity:** PASS
  - Evidence: Orchestration lists parallel tracks and sequencing, with coverage-gate ratchet criteria. (`orchestration.md`)
- **Overall readiness:** NEEDS REVISION
  - Rationale: Multiple acceptance-criteria gaps remain (issue updates, fail-before evidence location, CI fail-below-threshold proof, notes regression evidence). See “Delivery-quality risks.”

## Assumptions & Not Found

- `change-plan.md`: Not found in repo (searched `**/change-plan*.md`).

## Work Planning Checklist

| Requirement | Status | Evidence | Missing / Risk |
| --- | --- | --- | --- |
| Objective / outcome (specific, testable) | PASS | Goal and MVP targets in `initiative.md`. | — |
| Stakeholders / users | PASS | Listed in `initiative.md`. | — |
| Proposed approach + tradeoffs | PASS | Approach and tradeoffs documented. (`initiative.md`) | — |
| Scope boundaries & definition of done | PASS | Module list + non-goals documented. (`initiative.md`) | — |
| Success signals / quality gates | PARTIAL | Coverage targets + CI gate strategy documented, but fail-below-threshold evidence missing. (`initiative.md`, `orchestration.md`, CI evidence) | Need CI failure evidence or documented exception. |
| Effort / capacity envelope | PASS | Resource lockup estimate in `initiative.md`. | — |
| Risks + mitigations | PASS | Risks/mitigations listed in `initiative.md`. | — |
| Dependencies + sequencing | PASS | Parallel/sequence plan in `orchestration.md`. | — |

## Scope & Delivery Mapping

**Primary objective:** Raise coverage on core logic without blocking on CLI/UI parity, enforce “no merge without tests,” and prevent regressions.

- **Core transform coverage** → #21 (enhance), #22 (speakerless), #23 (identity/normalize)
- **Regression & fixtures** → #24 (multi-speaker fixtures), #26 (notes regressions)
- **E2E CLI coverage** → #25 (speakerless + notes CLI)
- **Formatter/parser coverage** → #27 (formatters + parser)
- **CI gate + reporting** → #28 (CI coverage gate)

**Gaps:**
- Epic acceptance criteria require evidence for “no merge without tests” and coverage non-regression; current evidence does not explicitly demonstrate enforcement or historical guardrails.

## Delivery-Quality Risks (Top 5)

1. **Issue update evidence missing for multiple features**
   - Evidence: #22, #23, #26, #27, #28 plans show issue update tasks not completed.
   - Risk: Missing external synchronization and audit trail for delivered work.
   - Fix direction: Add local issue-update mirrors and (if GH access) post comments with evidence.

2. **Fail-before exception dossiers stored in non-canonical locations**
   - Evidence: `evidence/remediation-baseline/fail-before-exception.*.md` for #21 and #26 (should be under `evidence/regression-testing/`).
   - Risk: Auto-check eligibility blocked by location rules.
   - Fix direction: Copy dossiers into `evidence/regression-testing/` and record canonical path.

3. **Notes regressions coverage evidence fails overall threshold**
   - Evidence: `notes-regressions-26/evidence/remediation-baseline/coverage.2026-02-03T18-30.txt` shows `EXIT_CODE: 1` due to overall coverage < 15%.
   - Risk: Coverage evidence does not demonstrate a passing toolchain run for this scenario.
   - Fix direction: Capture notes-focused coverage evidence without failing the global gate or provide exception dossier.

4. **CI coverage gate lacks fail-below-threshold proof**
   - Evidence: CI success run recorded (`ci-run.2026-02-06T01-41.md`), but no negative run showing gate failure.
   - Risk: Enforcement claim not fully verified.
   - Fix direction: Run CI (or local coverage report) with `fail_under` temporarily above current coverage and capture failure evidence.

5. **Formatter/parser tests still include temp-file usage in existing suite**
   - Evidence: `tests/formatters/test_notes_formatting.py` uses `tmp_path` and writes outputs (violates unit-test policy). (`grep_search` hits in test file)
   - Risk: Unit-test policy non-compliance; long-term fragility.
   - Fix direction: Replace temp-file tests with in-memory fakes or request explicit exception.

## Orchestration Review

Not generated. Execution is underway with delivered tests and evidence across multiple feature folders.
