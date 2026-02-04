# Fail-before evidence

Issue: #26 - Add regression tests for notes conversion edge cases

## Context

This remediation adds NEW regression tests for previously untested edge cases in notes conversion. The "fail-before" state is that these specific regression tests did not exist, leaving edge cases uncovered.

## Baseline State (Commit: 3ab288535f1eecea32a940806044ce63afa63f9a)

Prior to this remediation:
- No regression tests existed for markdown cleanup edge cases (escaped dollars, formatting markers)
- No tests validated bullet indentation level mapping consistency
- No tests verified heading level detection with leading whitespace
- No tests checked notes label insertion as H2 after H1
- No tests validated mixed heading/bullet ordering preservation

Coverage for `transform/notes.py` was present but these specific edge case scenarios were not explicitly tested.

## Evidence Type

**New regression tests** (not fixing failing tests) - The "before" state is the absence of these tests.

## Reference Baseline

- Baseline commit: `3ab288535f1eecea32a940806044ce63afa63f9a`
- Baseline coverage: See `baseline/pytest_cov.txt`
- No GitHub Actions workflow run available showing explicit test failures (tests did not exist)

## Artifact Location

File: `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-notes-regressions-26/remediation-baseline/fail-before.2026-02-03T18-30.md`
