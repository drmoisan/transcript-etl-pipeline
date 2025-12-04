Agent D Objective: Build reusable 3+ speaker fixtures (e.g., SpaceX) and regression tests to prevent grouping regressions.

## Policies: Always Follow These

CRITICAL: When implementing any code, tests, or tasks, you must adhere to these repo policies without exception. These are not guidelines-they are requirements.

Read each policy document thoroughly before starting work. Implement them exactly as written. Do not interpret, modify, or skip any requirements.

* Coding Standards, Workflow, PR/commit procedures:  
  [code-change.instructions.md](../../../code-change.instructions.md)
  
  This document defines the complete development workflow including:  
  - Pre-implementation requirements (clarify objectives, document plans)  
  - Python coding standards (formatting, linting, typing, testing)  
  - Design principles (simplicity, reusability, extensibility, separation of concerns)  
  - Post-implementation requirements (quality checks, documentation updates)

* Developer Tooling: Poetry, Black, Ruff, Pyright, Pytest, pytest-cov, coverage, pre-commit, VSCode tasks:  
  [developer-tooling.md](../../../developer-tooling.md)
  
  This document covers all tooling setup and usage.

* Unit Test Policy (independence, determinism, clarity, AAA, etc.):  
  [unit-test-policy.md](../../../unit-test-policy.md)
  
  This document defines mandatory testing standards. Every test must comply.

Do not guess. Do not omit steps. Do not introduce inconsistencies. Follow the policies exactly.

## Workplan
- Create/reuse 3+ speaker fixtures (e.g., SpaceX discussion) suitable for regression tests.
- Add regression tests (likely under `tests/integration/` or `tests/transform/`) that fail-before/pass-after for known grouping issues.
- Ensure fixtures are reusable by other tests; document locations/usage here.
- Run coverage/tests to confirm stability; link PR(s) and results in issue #24.

## Acceptance Criteria
- Fixtures added and referenced by regression tests in `tests/...`.
- Regression tests capture previous failures and now pass.
- Documentation of fixture location and usage is present here and in issue #24.
- Issue #24 updated with PR/test links and evidence of improved robustness.
