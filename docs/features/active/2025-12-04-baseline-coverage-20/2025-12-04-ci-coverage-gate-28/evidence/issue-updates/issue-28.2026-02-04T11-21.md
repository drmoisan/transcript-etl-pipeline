# Issue Update Mirror

Timestamp: 2026-02-04T11-21
IssueNumber: 28
IssueURL: https://github.com/drmoisan/transcript-etl-pipeline/issues/28
FeatureFolder: docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/

This file is the **local mirror** for GitHub Issue #28 updates, required even when GitHub access is available.

CapturedVia:
- `gh issue view 28 -R drmoisan/transcript-etl-pipeline --json url,title,updatedAt,body`
- `gh api repos/drmoisan/transcript-etl-pipeline/issues/28/comments`

RemoteVerification:
- GitHub CLI/auth available: Yes
- Comments found: 0

## Exact posted text (machine-preserved)

### Issue JSON (authoritative)

~~~json
{"body":"Scope:\n- Add coverage reporting and a fail-under threshold to CI.\n\nGoals:\n- Introduce coverage report in CI and set initial `--fail-under` (e.g., 40%), with a plan to ratchet up.\n- Ensure CI surfaces coverage deltas per run.\n\nAcceptance:\n- CI job runs coverage and fails below the configured floor.\n- Document how to adjust thresholds as coverage improves.\n\n## Documentation\n\nSpecification: https://github.com/carpenike/transcript-etl-pipeline/blob/main/docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/spec.md\n\n## CI run evidence\n\nCurrent state: https://github.com/carpenike/transcript-etl-pipeline/blob/main/docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/remediation-baseline/ci-run.2026-02-03T18-30.md","title":"Add CI coverage gate and reporting","updatedAt":"2026-02-04T12:36:29Z","url":"https://github.com/drmoisan/transcript-etl-pipeline/issues/28"}
~~~

### Comments JSON

~~~json
[]
~~~
