---
title: "2025-12-04-ci-coverage-gate - Plan"
issue: "28"
parent: "21"
owner: "drmoisan"
last_updated: "2026-02-02"
status: "Planned"
status_color: "blue"
version: "0.2"
---

# 2025-12-04-ci-coverage-gate - Plan

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

- **Issue:** [#28](https://github.com/drmoisan/transcript-etl-pipeline/issues/28)
- **Parent (optional):** [#21](https://github.com/drmoisan/transcript-etl-pipeline/issues/21)
- **Owner:** drmoisan
- **Last Updated:** 2026-02-02
- **Status:** Planned
- **Version:** 0.2

## Required References

- Copilot Instructions: [`.github/copilot-instructions.md`](../../../../.github/copilot-instructions.md)
- General Coding Standards: [`.github/instructions/general-code-change.instructions.md`](../../../../.github/instructions/general-code-change.instructions.md)
- General Unit Test Policy: [`.github/instructions/general-unit-test.instructions.md`](../../../../.github/instructions/general-unit-test.instructions.md)
- Python Coding Standards: [`.github/instructions/python-code-change.instructions.md`](../../../../.github/instructions/python-code-change.instructions.md)
- Python Unit Test Policy: [`.github/instructions/python-unit-test.instructions.md`](../../../../.github/instructions/python-unit-test.instructions.md)
- GitHub Actions Instructions: [`.github/instructions/github-actions.instructions.md`](../../../../.github/instructions/github-actions.instructions.md)
- GitHub Actions CI/CD Best Practices: [`.github/instructions/github-actions-ci-cd-best-practices.instructions.md`](../../../../.github/instructions/github-actions-ci-cd-best-practices.instructions.md)
- Developer Tooling: [`docs/developer-tooling.md`](../../../developer-tooling.md)

**All work must comply with these policies; do not duplicate their content here.**

## Requirements Traceability

| REQ-ID | Description | Source |
| --- | --- | --- |
| REQ-1 | Add coverage configuration in `pyproject.toml` with `fail_under = 15` and the ratchet plan comments. | `28-ci-coverage-gate.md` |
| REQ-2 | CI runs pytest with coverage reports and uploads HTML/XML artifacts plus a GitHub Actions summary. | `28-ci-coverage-gate.md` |
| REQ-3 | CI enforces the coverage threshold using `coverage report` and the `fail_under` setting. | `28-ci-coverage-gate.md` |
| REQ-4 | Document the gating configuration in the feature doc and update Issue #28 with evidence. | `28-ci-coverage-gate.md` |

## Implementation Plan (Atomic Tasks)

> **Instructions for this section:**
> - Break work into **Phases** (broad buckets) and **Atomic Tasks** (binary, 5-30 min units).
> - Use `- [ ] [P#-T#]` for every task.
> - Start every task with a **strong verb** (Implement, Create, Update, Verify).
> - No "bucket" tasks like "Refactor module" or "Write tests"; split them into specific, verifiable steps.
> - **Self-Validating Phases:** Include necessary test creation/update tasks *within* the phase that implements the code. Do not defer verification to a final "Testing" phase.

### Phase 0 — Context & Inputs
- [ ] [P0-T1] Read `.github/copilot-instructions.md` in the repo root to establish baseline agent rules (line references not applicable).
  - Acceptance: `powershell -Command "Test-Path .github/copilot-instructions.md"` exits with code 0.
- [ ] [P0-T2] Read `.github/instructions/general-code-change.instructions.md` to confirm the required workflow (line references not applicable).
  - Acceptance: `powershell -Command "Test-Path .github/instructions/general-code-change.instructions.md"` exits with code 0.
- [ ] [P0-T3] Read `.github/instructions/general-unit-test.instructions.md` to confirm unit test rules (line references not applicable).
  - Acceptance: `powershell -Command "Test-Path .github/instructions/general-unit-test.instructions.md"` exits with code 0.
- [ ] [P0-T4] Read `.github/instructions/python-code-change.instructions.md` to confirm Python-specific requirements (line references not applicable).
  - Acceptance: `powershell -Command "Test-Path .github/instructions/python-code-change.instructions.md"` exits with code 0.
- [ ] [P0-T5] Read `.github/instructions/python-unit-test.instructions.md` to confirm Python testing standards (line references not applicable).
  - Acceptance: `powershell -Command "Test-Path .github/instructions/python-unit-test.instructions.md"` exits with code 0.
- [ ] [P0-T6] Read `.github/instructions/github-actions.instructions.md` before editing `.github/workflows/ci.yml` (line references not applicable).
  - Acceptance: `powershell -Command "Test-Path .github/instructions/github-actions.instructions.md"` exits with code 0.
- [ ] [P0-T7] Read `.github/instructions/github-actions-ci-cd-best-practices.instructions.md` before editing `.github/workflows/ci.yml` (line references not applicable).
  - Acceptance: `powershell -Command "Test-Path .github/instructions/github-actions-ci-cd-best-practices.instructions.md"` exits with code 0.
- [ ] [P0-T8] Capture baseline formatter output for Python using `poetry run black .` from repo root.
  - Acceptance: Command exits with code 0.
- [ ] [P0-T9] Capture baseline lint output for Python using `poetry run ruff check` from repo root.
  - Acceptance: Command exits with code 0.
- [ ] [P0-T10] Capture baseline type-check output for Python using `poetry run pyright` from repo root.
  - Acceptance: Command exits with code 0.
- [ ] [P0-T11] Capture baseline test output for Python using `poetry run pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-report=html` from repo root.
  - Acceptance: Command exits with code 0.

### Phase 1 — Coverage Configuration (pyproject.toml)
- [x] [P1-T1] Add `[tool.coverage.run]` and `[tool.coverage.report]` sections in `pyproject.toml` (insert after `[tool.pyright]` around lines 53–78) with `source = ["src"]`, `omit = ["tests/*", "*/tests/*", "*/__pycache__/*", "*/site-packages/*"]`, `fail_under = 15`, and the ratchet plan comments exactly as listed in `28-ci-coverage-gate.md` (REQ-1).
  - Acceptance: `powershell -Command "Select-String -Path pyproject.toml -Pattern '\[tool.coverage.report\]'"` returns a match and `powershell -Command "Select-String -Path pyproject.toml -Pattern 'fail_under = 15'"` returns a match.

### Phase 2 — CI Coverage Reporting and Gating (.github/workflows/ci.yml)
- [x] [P2-T1] Add a `Run tests with coverage` step in `.github/workflows/ci.yml` (quality-checks job, after `Type check with Pyright`, around lines 70–73) that runs `poetry run pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-report=html` (REQ-2).
  - Acceptance: `powershell -Command "Select-String -Path .github/workflows/ci.yml -Pattern 'Run tests with coverage'"` returns a match and the following line contains the exact pytest command.
- [x] [P2-T2] Add a `Check coverage threshold` step in `.github/workflows/ci.yml` (after the coverage test step, around lines 74–76) that runs `poetry run coverage report` to enforce `fail_under` from `pyproject.toml` (REQ-3).
  - Acceptance: `powershell -Command "Select-String -Path .github/workflows/ci.yml -Pattern 'Check coverage threshold'"` returns a match and the following line contains `poetry run coverage report`.
- [x] [P2-T3] Add `Upload coverage HTML report` and `Upload coverage XML report` steps in `.github/workflows/ci.yml` (after the threshold step, around lines 78–90) using `actions/upload-artifact@v4` with `name: coverage-html-report`, `path: htmlcov/`, `name: coverage-xml-report`, and `path: coverage.xml`, `retention-days: 14` (REQ-2).
  - Acceptance: `powershell -Command "Select-String -Path .github/workflows/ci.yml -Pattern 'coverage-html-report'"` returns a match and `powershell -Command "Select-String -Path .github/workflows/ci.yml -Pattern 'coverage-xml-report'"` returns a match.
- [x] [P2-T4] Add a `Generate coverage summary` step in `.github/workflows/ci.yml` (after artifact uploads, around lines 92–96) that appends a Markdown report to `$GITHUB_STEP_SUMMARY` using `poetry run coverage report --format=markdown` (REQ-2).
  - Acceptance: `powershell -Command "Select-String -Path .github/workflows/ci.yml -Pattern 'Generate coverage summary'"` returns a match and the step includes `coverage report --format=markdown`.

### Phase 3 — Documentation and Issue Updates
- [ ] [P3-T1] Update `docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/28-ci-coverage-gate.md` to include the final `fail_under = 15` setting and the threshold ratchet plan table exactly as specified in the Implementation Notes section (REQ-4).
  - Acceptance: `powershell -Command "Select-String -Path docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-ci-coverage-gate-28/28-ci-coverage-gate.md -Pattern 'fail_under = 15'"` returns a match and the table includes the row `Initial | 15% | Current baseline (~16%)`.
- [ ] [P3-T2] Update GitHub Issue #28 with the PR link, the CI configuration summary, and a note confirming the coverage gate fails when coverage drops below 15% (REQ-4).
  - Acceptance: `gh issue view 28 --json body -q ".body"` output contains `fail_under = 15` and a PR URL matching `https://github.com/drmoisan/transcript-etl-pipeline/pull/`.

### Phase 4 — QA (Python Toolchain)
- [ ] [P4-T1] Run `poetry run black .` and confirm the formatter exits with code 0; if it modifies files or fails, repeat after fixing and restart from [P4-T1].
  - Acceptance: Command exits with code 0 on a pass where no files are modified.
- [ ] [P4-T2] Run `poetry run ruff check` and confirm the linter exits with code 0; if it fails, fix issues and restart from [P4-T1].
  - Acceptance: Command exits with code 0.
- [ ] [P4-T3] Run `poetry run pyright` and confirm type checking exits with code 0; if it fails, fix issues and restart from [P4-T1].
  - Acceptance: Command exits with code 0.
- [ ] [P4-T4] Run `poetry run pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-report=html` and confirm tests exit with code 0; if it fails, fix issues and restart from [P4-T1].
  - Acceptance: Command exits with code 0.

## Test Plan

- Unit: `poetry run pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-report=html`
- Integration: Not applicable (workflow and config-only change).
- Manual/CLI: `gh issue view 28 --json body -q ".body"` to verify the issue update content.

## Open Questions / Notes

- None.
