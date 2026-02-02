# multi-speaker-fixtures (Issue [#24](https://github.com/drmoisan/transcript-etl-pipeline/issues/24))

- Date captured: 2025-12-04
- Author: Dan Moisan
- Status: Promoted -> docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-multi-speaker-fixtures-24/ (Issue #24)

- Issue: #24
- Issue URL: [https://github.com/drmoisan/transcript-etl-pipeline/issues/24](https://github.com/drmoisan/transcript-etl-pipeline/issues/24)
- Last Updated: 2025-12-04

## Problem / Why

3+ speaker scenarios lack reusable fixtures and regression coverage, leaving grouping behavior under-tested and prone to regressions (e.g., SpaceX discussion).

## Proposed Behavior

Add reusable multi-speaker fixtures and regression tests that validate expected grouping outcomes for speakerless and helper logic.

## Acceptance Criteria (early draft)

- [ ] Fixture assets for 3+ speaker cases are checked in and referenced by tests.
- [ ] Regression tests fail on known bad behavior and pass after fixes.
- [ ] Fixtures are reusable across speakerless and speaker_helpers test suites.

## Constraints & Risks

- Fixtures must be deterministic and stable across runs.
- Keep fixtures reusable without embedding sensitive data.
- Avoid test flakiness by anchoring to clear expected groupings.

## Test Conditions to Consider

- [ ] Fixture-driven tests for speakerless grouping and speaker_helpers logic.
- [ ] Integration assertions for expected grouping in 3+ speaker transcripts.
- [ ] Regression checks for known mis-grouping patterns (e.g., SpaceX).

## Next Step

- [x] Promote to GitHub issue (Issue #24)
- [ ] Create `docs/features/active/multi-speaker-fixtures/` folder from the template

