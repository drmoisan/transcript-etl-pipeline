# `2025-12-04-ci-coverage-gate` — User Story

- Issue: #28
- Owner: drmoisan
- Status: Draft
- Last Updated: 2026-02-02T11-43

## Story Statement

- As a repo maintainer, I want CI to enforce a minimum coverage floor, so that coverage regressions are blocked before merge.
- As a contributor, I want CI to surface coverage results and deltas, so that I can see the impact of my changes and adjust tests quickly.

## Problem / Why

CI does not currently enforce or surface coverage outcomes, so coverage can regress unnoticed. A CI coverage gate and reporting are needed to prevent regressions and make coverage deltas visible.


## Personas & Scenarios

- Persona: Repo maintainer
  - Responsible for CI health, release readiness, and code quality
  - Cares about preventing regressions without blocking progress unnecessarily
  - Constrained by existing low baseline coverage and a multi-issue test plan
  - Goal: enforce a floor and provide clear feedback while coverage ratchets up
- Scenario: Raise coverage floor without breaking the workflow
  - Trigger: A contributor opens a PR that reduces coverage
  - Steps: CI runs tests with coverage, compares results to the fail-under threshold, and reports the coverage summary
  - Decision: If coverage is below the floor, the PR is blocked; otherwise it passes with visible coverage output
  - Outcome: The contributor sees the coverage delta and updates tests before merge


## Acceptance Criteria

- [ ] CI runs pytest-cov and fails when total coverage is below the configured floor in `pyproject.toml` (`[tool.coverage.report] fail_under = 15`).
- [ ] CI passes when total coverage meets/exceeds the configured floor.
- [ ] CI surfaces coverage results in logs and the GitHub Actions step summary for each run.
- [ ] CI uploads coverage artifacts (HTML report and `coverage.xml`) for each run.
- [ ] Documentation explains how to adjust `fail_under` in `pyproject.toml` as coverage improves.


## Non-Goals

- Defining new production features or refactors unrelated to coverage reporting.
- Achieving full CLI/UI parity coverage as part of this change.
- Introducing external coverage services beyond CI logs/artifacts.
