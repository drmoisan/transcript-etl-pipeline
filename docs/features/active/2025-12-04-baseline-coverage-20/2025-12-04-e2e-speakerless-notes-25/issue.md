# e2e-speakerless-notes (Issue [#25](https://github.com/drmoisan/transcript-etl-pipeline/issues/25))

- Date captured: 2025-12-04
- Author: Dan Moisan
- Status: Promoted -> Promoted -> `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-e2e-speakerless-notes/` (Issue #25)

- Issue: #25
- Issue URL: [https://github.com/drmoisan/transcript-etl-pipeline/issues/25](https://github.com/drmoisan/transcript-etl-pipeline/issues/25)
- Last Updated: 2025-12-04

## Problem / Why

There is no end-to-end coverage for CLI speakerless + notes workflows, leaving output validation and integration behavior untested.

## Proposed Behavior

Add pytest integration tests that run CLI-driven speakerless and notes pipelines for DOCX/MD outputs and assert on key output structure/text markers.

## Acceptance Criteria (early draft)

- [ ] Tests run via the pytest integration suite and pass reliably.
- [ ] At least one speakerless transcript and one notes pipeline case are covered.
- [ ] Outputs are validated for expected structure/content using text markers (no golden DOCX required if impractical).

## Constraints & Risks

- End-to-end tests must remain deterministic and fast.
- Avoid fragile DOCX binary comparisons; prefer text marker assertions.

## Test Conditions to Consider

- [ ] CLI-driven speakerless run producing DOCX/MD and validated via markers.
- [ ] Notes pipeline CLI run with expected structure/content markers.
- [ ] Assert key output fields without brittle binary snapshots.

## Next Step

- [x] Promote to GitHub issue (Issue #25)
- [ ] Create `docs/features/active/e2e-speakerless-notes/` folder from the template

