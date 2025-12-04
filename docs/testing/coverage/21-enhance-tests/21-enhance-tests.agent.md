Agent A Objective: Characterize and raise coverage for `transform/enhance.py` (speakerless routing, identity constraints, normalization interactions) to a solid baseline.

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
- Inspect current behavior of `transform/enhance.py`; note key branches (speakerless routing, identity constraints, normalization interplay).
- Add characterization tests to lock current outputs for representative inputs.
- Add focused unit tests for helpers/branches to drive coverage toward the target (≈70%+ on the module).
- Keep tests in `tests/transform/` (or appropriate area); no code in this folder.
- Run `poetry run pytest --cov=src/transcript_etl_pipeline --cov-report=term` (or the VS Code tasks) to confirm coverage lift.
- Document any surprising behaviors/edge cases here and in issue #21; link PR(s).

## Acceptance Criteria
- Failing-before/passing-after tests added for the targeted behaviors.
- Module coverage for `transform/enhance.py` reaches roughly 70% or higher (cite report).
- Tests follow unit-test policy (deterministic, clear assertions, AAA).
- Issue #21 updated with findings, links to tests/PR, and coverage evidence.
