# CI Coverage Configuration Evidence — coverage-gate-28

This evidence captures the configured CI coverage gate, artifact uploads, and documentation references to fail_under.

## CI workflow coverage steps

Command: Select-String -Path /workspaces/transcript-etl-pipeline/.github/workflows/ci.yml -Pattern 'Run tests with coverage|Check coverage threshold|Upload coverage HTML report|Upload coverage XML report|Generate coverage summary'

Output:
```
.github/workflows/ci.yml:70:      - name: Run tests with coverage
.github/workflows/ci.yml:74:      - name: Check coverage threshold
.github/workflows/ci.yml:78:      - name: Upload coverage HTML report
.github/workflows/ci.yml:85:      - name: Upload coverage XML report
.github/workflows/ci.yml:92:      - name: Generate coverage summary
```

Timestamp: 2026-02-05T13:55:35Z
Command: Select-String -Path /workspaces/transcript-etl-pipeline/.github/workflows/ci.yml -Pattern 'Run tests with coverage|Check coverage threshold|Upload coverage HTML report|Upload coverage XML report|Generate coverage summary'
EXIT_CODE: 0

## Coverage threshold in pyproject.toml

Command: Select-String -Path /workspaces/transcript-etl-pipeline/pyproject.toml -Pattern 'fail_under'

Output:
```
pyproject.toml:68:fail_under = 15
```

Timestamp: 2026-02-05T13:55:35Z
Command: Select-String -Path /workspaces/transcript-etl-pipeline/pyproject.toml -Pattern 'fail_under'
EXIT_CODE: 0

## Feature documentation fail_under guidance

Command: Select-String -Path /workspaces/transcript-etl-pipeline/docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/spec.md -Pattern 'fail_under|ratchet|coverage'

Output:
```
docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/spec.md:1:# 2025-12-04-ci-coverage-gate — Spec
docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/spec.md:12:CI does not currently enforce or surface coverage outcomes, so coverage can regress unnoticed. Add a CI coverage gate in `.github/workflows/ci.yml` that uses the configured `fail_under` threshold from `pyproject.toml` and publishes coverage outputs for each run.
docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/spec.md:17:Add coverage reporting in CI and enforce a configurable minimum coverage threshold sourced from `pyproject.toml` (initial floor aligned to current baseline). The CI quality-checks job runs Pytest with coverage, uploads HTML/XML artifacts, and publishes a GitHub Actions step summary. The job fails when total coverage is below the configured floor, with a documented ratchet plan to raise the floor over time.
docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/spec.md:30:## Fail-Under Ratchet Strategy
docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/spec.md:32:The `fail_under` threshold in `pyproject.toml` enforces a minimum coverage floor in CI. This threshold should be ratcheted upward as coverage improves:
docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/spec.md:36:- Initial value: `fail_under = 15` (aligned to baseline coverage ~16%)
docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/spec.md:39:1. **Measure** — Run pytest-cov locally and in CI to confirm current total coverage.
docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/spec.md:40:2. **Update** — When sustained coverage exceeds the current floor by 5+ percentage points, update `fail_under` in `pyproject.toml` to the new floor.
docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/spec.md:57:   - Coverage threshold in `pyproject.toml` under `[tool.coverage.report] fail_under = 15` (initial floor; ratchet plan below).
docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/spec.md:73:   - Expected: CI logs include coverage summary; job fails if total coverage < `fail_under`.
docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/spec.md:105:  - CI logs include the coverage summary; upload HTML and XML artifacts.
```

Timestamp: 2026-02-05T13:55:35Z
Command: Select-String -Path /workspaces/transcript-etl-pipeline/docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/spec.md -Pattern 'fail_under|ratchet|coverage'
EXIT_CODE: 0

EvidenceSchemaAddendum:
Timestamp: 2026-02-05T13:55:35Z
Command: Select-String -Path /workspaces/transcript-etl-pipeline/.github/workflows/ci.yml -Pattern 'Run tests with coverage|Check coverage threshold|Upload coverage HTML report|Upload coverage XML report|Generate coverage summary'
EXIT_CODE: 0
