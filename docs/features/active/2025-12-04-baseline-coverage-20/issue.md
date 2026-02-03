# baseline-coverage (Issue [#20](https://github.com/drmoisan/transcript-etl-pipeline/issues/20))

- Date captured: 2025-12-04
- Author: Dan Moisan
- Status: Promoted -> docs/features/active/2025-12-04-baseline-coverage-20 (Issue #20)

> Automation note: Keep the section headings below unchanged; the promotion tooling maps each of them into the GitHub bug issue template.

- Issue: #20
- Issue URL: https://github.com/drmoisan/transcript-etl-pipeline/issues/20
- Last Updated: 2025-12-04

## Problem / Why

Coverage is ~16% with gaps in core transform and speakerless flows; CLI/UI paths are barely covered. The project needs a coordinated baseline to prevent regressions and steadily raise coverage on core logic without blocking on full CLI/UI parity.

## Proposed Behavior

Establish a baseline automated test/coverage initiative that prioritizes core logic, adds regression tests for bug-prone areas, and enforces “no merge without tests.”

## Acceptance Criteria (early draft)

- [ ] Reach 80% coverage on core logic without blocking on CLI/UI parity.
- [ ] Add regression tests for recent/known bug-prone areas.
- [ ] Enforce “no PR merges without tests” and “every bug fix ships with a regression test.”
- [ ] Coverage must not decrease; enforce locally and add CI coverage gate once baseline improves.

## Constraints & Risks

- Current coverage includes CLI/UI/legacy paths and is ~16% (snapshot on 2025-12-04).
- Avoid blocking on CLI/UI parity; focus on core transform and speakerless flows first.
- Coverage gate should be introduced after baseline improves to avoid blocking progress.

## Test Conditions to Consider

- [ ] Unit tests for core transform modules: `transform/enhance.py`, `identity_constraints.py`, `normalize.py`.
- [ ] Unit/regression tests for speakerless grouping heuristics.
- [ ] Fixtures and regression tests for 3+ speaker scenarios.
- [ ] End-to-end tests for speakerless + notes flows (CLI).
- [ ] Regression tests for notes conversion edge cases.
- [ ] Tests for formatters and document parser.

## Next Step

- [x] Promote to GitHub issue (Issue #20)
- [ ] Create `docs/features/active/baseline-coverage/` folder from the template

## Sync Summary (as of 2026-02-03T17-30)

- **Status:** In progress; acceptance criteria not fully evidenced.
- **Evidence highlights:** Core feature docs and plans exist under `docs/features/active/2025-12-04-baseline-coverage-20/` for #21–#28.
- **Open gaps:** Coverage >= 80% not evidenced; CI coverage gate documentation and run evidence pending; multiple feature issue updates remain outstanding.