# notes-regressions (Issue [#26](https://github.com/drmoisan/transcript-etl-pipeline/issues/26))

- Date captured: 2025-12-04
- Author: Dan Moisan
- Status: Promoted -> docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-notes-regressions-26/ (Issue #26)

- Issue: #26
- Issue URL: [https://github.com/drmoisan/transcript-etl-pipeline/issues/26](https://github.com/drmoisan/transcript-etl-pipeline/issues/26)
- Last Updated: 2025-12-04

## Problem / Why

Known notes conversion edge cases lack regression tests, allowing past bugs to reappear and leaving transform/notes.py under-covered.

## Proposed Behavior

Capture known notes conversion issues and add regression tests that document the prior failure and validate current behavior, improving coverage in notes-related paths.

## Acceptance Criteria (early draft)

- [ ] Each known notes conversion bug has a failing-before/passing-after regression test.
- [ ] Regression tests demonstrate prior failures and now pass.
- [ ] Coverage on notes-related paths measurably improves.

## Constraints & Risks

- Tests must be deterministic and avoid external dependencies.
- Keep scope limited to notes conversion edge cases and related code paths.

## Test Conditions to Consider

- [ ] Unit/regression tests for transform/notes.py edge cases from prior reports.
- [ ] Coverage checks for notes-related paths.
- [ ] Representative inputs reflecting known failure modes.

## Next Step

- [x] Promote to GitHub issue (Issue #26)
- [ ] Create `docs/features/active/notes-regressions/` folder from the template

## Sync Summary (as of 2026-02-03T17-30)

- **Status:** Partially delivered; acceptance criteria not fully evidenced.
- **Evidence highlights:** Regression tests in `tests/transform/test_notes.py`; coverage evidence referenced in plan (coverage.xml mention).
- **Open gaps:** Issue #26 update not recorded; QA toolchain steps not verified; pre/post failure evidence not documented.

