# Issue Update Mirror

Timestamp: 2026-02-04T11-21
IssueNumber: 23
IssueURL: https://github.com/drmoisan/transcript-etl-pipeline/issues/23
FeatureFolder: docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-identity-normalize-23/

This file is the **local mirror** for GitHub Issue #23 updates, required even when GitHub access is available.

CapturedVia:
- `gh issue view 23 -R drmoisan/transcript-etl-pipeline --json url,title,updatedAt,body`
- `gh api repos/drmoisan/transcript-etl-pipeline/issues/23/comments`

RemoteVerification:
- GitHub CLI/auth available: Yes
- Comments found: 0

## Exact posted text (machine-preserved)

### Issue JSON (authoritative)

~~~json
{"body":"Scope:\n- Modules: transform/identity_constraints.py, transform/normalize.py.\n- Exercise name extraction, constraint application, normalization edge cases.\n\nGoals:\n- Unit tests that cover primary branches and edge cases.\n- Target: >=75% combined coverage across both modules.\n\nAcceptance:\n- Tests assert on extracted constraints and normalized outputs for tricky inputs.\n- Coverage report shows target met for both modules.\n## Coverage Evidence (Automated)\n\nCommand: `poetry run pytest --cov=src/transcript_etl_pipeline --cov-report=term-missing`\n\n| Module | Coverage |\n| --- | --- |\n| `src/transcript_etl_pipeline/transform/identity_constraints.py` | 98% |\n| `src/transcript_etl_pipeline/transform/normalize.py` | 100% |\n\nCombined coverage: 99% (≥ 75% target).\n\n## QA evidence\n- Black: [qa-black.2026-02-03T18-30.txt](docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-identity-normalize-23/remediation-baseline/qa-black.2026-02-03T18-30.txt)\n- Ruff: [qa-ruff.2026-02-03T18-30.txt](docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-identity-normalize-23/remediation-baseline/qa-ruff.2026-02-03T18-30.txt)\n- Pyright: [qa-pyright.2026-02-03T18-30.txt](docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-identity-normalize-23/remediation-baseline/qa-pyright.2026-02-03T18-30.txt)\n- Pytest: [qa-pytest.2026-02-03T18-30.txt](docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-identity-normalize-23/remediation-baseline/qa-pytest.2026-02-03T18-30.txt)\n\n","title":"Add tests for identity_constraints.py and normalize.py","updatedAt":"2026-02-04T03:49:14Z","url":"https://github.com/drmoisan/transcript-etl-pipeline/issues/23"}
~~~

### Comments JSON

~~~json
[]
~~~
