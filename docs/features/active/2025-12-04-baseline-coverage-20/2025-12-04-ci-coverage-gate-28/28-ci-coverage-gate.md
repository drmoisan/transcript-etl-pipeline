# CI Coverage Gate (Issue #28)

## Summary

This feature adds CI coverage reporting, artifacts, and a gating threshold using `fail_under` from `pyproject.toml`. It also documents the ratchet plan for increasing coverage over time.

## Coverage Threshold Configuration

The coverage threshold is defined in `pyproject.toml` under `[tool.coverage.report]`:

```toml
fail_under = 15
```

## Threshold Ratchet Plan

| Phase | Target | Trigger |
| --- | --- | --- |
| Initial | 15% | Current baseline (~16%) |
| Stabilization | 20% | After initial bug fixes |
| Core Coverage | 30% | After covering critical paths |
| Long-term Goal | 50%+ | As test coverage expands |

## CI Coverage Artifacts

Each CI run produces:
- `coverage-html-report-<python-version>`: HTML coverage report
- `coverage-xml-report-<python-version>`: XML coverage report
- GitHub Actions step summary: Markdown coverage report

## Evidence

- Failing CI run: `evidence/qa-gates/ci-run.2026-02-06T22-29.md`
- Passing CI run: `evidence/qa-gates/ci-run-pass.2026-02-08T00-07.md`
