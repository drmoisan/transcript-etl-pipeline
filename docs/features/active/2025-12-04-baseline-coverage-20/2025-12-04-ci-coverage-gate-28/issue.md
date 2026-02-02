# ci-coverage-gate ([#28](https://github.com/drmoisan/transcript-etl-pipeline/issues/28))

- Date captured: 2025-12-04
- Author: Dan Moisan
- Status: Promoted -> docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-enhance-tests-28

> Automation note: Keep the section headings below unchanged; the promotion tooling maps each of them into the GitHub bug issue template.

- Issue: #28
- Issue URL: [https://github.com/drmoisan/transcript-etl-pipeline/issues/28](https://github.com/drmoisan/transcript-etl-pipeline/issues/28)
- Last Updated: 2025-12-04

## Problem / Why

CI does not currently enforce or surface coverage outcomes, so coverage can regress unnoticed. A CI coverage gate and reporting are needed to prevent regressions and make coverage deltas visible.

## Proposed Behavior

Add coverage reporting in CI and enforce a configurable minimum coverage threshold (initial floor around 40%) with a plan to ratchet up as coverage improves.

## Acceptance Criteria (early draft)

- [ ] CI runs coverage and fails below the configured floor (initial `--fail-under`, e.g., 40%).
- [ ] CI surfaces coverage results/deltas per run.
- [ ] Documentation explains how to adjust thresholds as coverage improves.

## Constraints & Risks

- Start with a conservative coverage floor to avoid blocking progress.
- Threshold should be easy to ratchet upward over time.
- Reporting should be CI-visible (logs and/or artifacts) without adding excessive runtime.

## Test Conditions to Consider

- [ ] Verify CI coverage command runs and produces a report.
- [ ] Confirm CI fails when coverage is below the configured threshold.
- [ ] Confirm CI passes when coverage meets/exceeds the threshold.

## Next Step

- [x] Promote to GitHub issue (Issue #28)
- [ ] Create `docs/features/active/ci-coverage-gate/` folder from the template

