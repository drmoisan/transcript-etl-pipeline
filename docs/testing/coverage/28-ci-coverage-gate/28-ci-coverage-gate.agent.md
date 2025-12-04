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
- [x] Add coverage reporting to CI (artifact + summary), updating `.github/workflows/` as needed.
- [x] Introduce an initial `--fail-under` floor (e.g., ~40%) with a documented plan to increase as coverage improves.
- [x] Ensure CI surfaces coverage deltas per run (logs/artifacts).
- [x] Keep the gating configuration documented here and in issue #28.

## Acceptance Criteria
- [x] CI runs coverage reporting and produces an artifact/summary.
- [x] A fail-under threshold is enforced at the agreed initial floor; adjustment plan documented.
- [ ] Issue #28 updated with PR link, configuration notes, and evidence that gating works.

## Implementation Notes

### CI Workflow Configuration

The CI workflow is defined in `.github/workflows/ci.yml` and includes:

1. **Triggers**: Runs on push and pull requests to `main` branch
2. **Python Setup**: Uses Python 3.12 with Poetry 1.8.4
3. **Caching**: Poetry virtual environment is cached for faster builds
4. **Quality Checks**:
   - Black (formatting)
   - Ruff (linting)
   - Pyright (type checking)
5. **Testing & Coverage**:
   - Pytest with coverage reporting
   - `--cov-fail-under=15` enforcement
   - HTML and XML coverage reports as artifacts
   - Markdown coverage summary in GitHub Actions summary

### Coverage Threshold Configuration

Located in `pyproject.toml` under `[tool.coverage.report]`:

```toml
fail_under = 15
```

### Threshold Ratchet Plan

| Phase | Target | Trigger |
|-------|--------|---------|
| Initial | 15% | Current baseline (~16%) |
| Stabilization | 20% | After initial bug fixes |
| Core Coverage | 30% | After covering critical paths |
| Long-term Goal | 50%+ | As test coverage expands |

### Coverage Artifacts

Each CI run produces:
- `coverage-html-report`: Interactive HTML coverage report (retained 14 days)
- `coverage-xml-report`: XML report for external tools (retained 14 days)
- GitHub Step Summary: Markdown table of coverage by file
