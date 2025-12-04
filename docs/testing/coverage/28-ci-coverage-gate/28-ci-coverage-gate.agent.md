Agent H Objective: Add CI coverage reporting and fail-under gating, with a plan to ratchet thresholds upward.

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
- Add coverage reporting to CI (artifact + summary), updating `.github/workflows/` as needed.
- Introduce an initial `--fail-under` floor (e.g., ~40%) with a documented plan to increase as coverage improves.
- Ensure CI surfaces coverage deltas per run (logs/artifacts).
- Keep the gating configuration documented here and in issue #28.

## Acceptance Criteria
- CI runs coverage reporting and produces an artifact/summary.
- A fail-under threshold is enforced at the agreed initial floor; adjustment plan documented.
- Issue #28 updated with PR link, configuration notes, and evidence that gating works.
