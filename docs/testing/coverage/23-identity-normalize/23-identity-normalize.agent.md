Agent C Objective: Increase coverage for `transform/identity_constraints.py` and `transform/normalize.py` (name extraction, constraint application, normalization edge cases) to ~75% combined.

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
- Map key paths in `identity_constraints.py` (name extraction, constraint application) and `normalize.py` (edge cases).
- Add unit tests for primary branches and tricky inputs to reach ~75% combined coverage.
- Keep tests in `tests/transform/`; prefer small, deterministic cases.
- Run coverage to confirm lift (`poetry run pytest --cov=src_transcript_etl_pipeline --cov-report=term`).
- Document anomalies or unexpected behaviors here and in issue #23; link PR(s).

## Acceptance Criteria
- Tests added/updated to cover main branches and edge cases for both modules.
- Combined coverage ~75%+ (cite coverage report).
- Tests conform to unit-test policy and are deterministic.
- Issue #23 updated with findings, PR/test links, and coverage evidence.
