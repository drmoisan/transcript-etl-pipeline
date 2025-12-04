Agent F Objective: Add regression tests for notes conversion edge cases and lift coverage for notes-related paths.

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
- Identify known/prior notes conversion bugs (from history/feature_status) to turn into regression tests.
- Add failing-before/passing-after tests in `tests/transform/` or `tests/integration/` as appropriate.
- Cover edge cases to raise coverage for notes-related paths.
- Run coverage to confirm improvement; keep tests deterministic.
- Record cases and outcomes here and in issue #26; link PR(s).

## Acceptance Criteria
- Regression tests added that reproduce prior notes bugs and now pass.
- Coverage for notes-related paths measurably improves (cite report).
- Tests adhere to unit-test policy and are deterministic.
- Issue #26 updated with PR/test links and brief outcomes.
