Timestamp: 2026-02-07T00-36
PostedAs: body
IssueUrl: https://github.com/drmoisan/transcript-etl-pipeline/issues/28
IssueUpdatedAt: 2026-02-08T03:38:53Z

Body:
Scope:
- Add coverage reporting and a fail-under threshold to CI.

Goals:
- Introduce coverage report in CI and set initial `--fail-under` (e.g., 40%), with a plan to ratchet up.
- Ensure CI surfaces coverage deltas per run.

Acceptance:
- CI job runs coverage and fails below the configured floor.
- Document how to adjust thresholds as coverage improves.

## Documentation

Specification: https://github.com/carpenike/transcript-etl-pipeline/blob/main/docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/spec.md

## CI run evidence

Current state: https://github.com/carpenike/transcript-etl-pipeline/blob/main/docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/remediation-baseline/ci-run.2026-02-03T18-30.md

## CI coverage gate update (baseline-coverage-#20)

- PR: https://github.com/drmoisan/transcript-etl-pipeline/pull/33
- Coverage gate: `fail_under = 15`
- Failing run evidence: https://github.com/drmoisan/transcript-etl-pipeline/blob/master/docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/evidence/qa-gates/ci-run.2026-02-06T22-29.md
- Passing run evidence: https://github.com/drmoisan/transcript-etl-pipeline/blob/master/docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/evidence/qa-gates/ci-run-pass.2026-02-08T00-07.md
