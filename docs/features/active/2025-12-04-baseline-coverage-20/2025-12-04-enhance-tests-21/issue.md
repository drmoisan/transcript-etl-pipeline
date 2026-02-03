# enhance-tests (Issue [#21](https://github.com/drmoisan/transcript-etl-pipeline/issues/21))

- GitHub Title: Add characterization + unit tests for transform/enhance.py
- Date captured: 2025-12-04
- Author: Dan Moisan
- Status: Promoted -> docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-enhance-tests-21

> Automation note: Keep the section headings below unchanged; the promotion tooling maps each of them into the GitHub bug issue template.

- Issue: #21
- Issue URL: [https://github.com/drmoisan/transcript-etl-pipeline/issues/21](https://github.com/drmoisan/transcript-etl-pipeline/issues/21)
- Last Updated: 2025-12-04

## Problem / Why

transform/enhance.py lacks sufficient unit coverage, leaving speakerless routing, identity constraints, and normalization interactions under-tested. This creates risk of regressions in core transformation logic.

## Proposed Behavior

Characterize current enhance behavior and add unit tests around key helpers and branching paths, targeting at least 80% coverage for transform/enhance.py.

## Acceptance Criteria (early draft)

- [ ] Tests fail before and pass after (for previously untested behavior).
- [ ] Speakerless routing and constraint handling scenarios are exercised.
- [ ] Coverage report shows >=80% for transform/enhance.py.

## Constraints & Risks

- Focus on characterization tests that reflect current behavior to avoid unintended changes.
- Keep coverage improvements within transform/enhance.py; avoid scope creep into unrelated modules.

## Test Conditions to Consider

- [ ] Unit tests for speakerless routing decisions and branches.
- [ ] Identity constraints + normalization interaction cases.
- [ ] Key helper function branching paths in transform/enhance.py.

## Next Step

- [x] Promote to GitHub issue (Issue #21)
- [ ] Create `docs/features/active/enhance-tests/` folder from the template

## Sync Summary (as of 2026-02-03T17-30)

- **Status:** Partially delivered; acceptance criteria not fully evidenced.
- **Evidence highlights:** Tests present in `tests/transform/test_enhance.py`; coverage evidence captured in `plan.2026-02-02T11-49.md` (Open Questions / Notes).
- **Open gaps:** Issue update with coverage evidence not recorded; targeted test-run commands and toolchain proof not verified in this sync.

