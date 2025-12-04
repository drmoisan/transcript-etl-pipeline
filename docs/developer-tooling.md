# Developer Tooling

Summary of the core tooling and automation for `transcript-etl-pipeline`.

Prereqs (run from repo root):

- `poetry install` (managed `.venv`)
- `poetry run pre-commit install` (local hooks mirroring CI)

See `docs/code-change.instructions.md` for the end-to-end workflow.

## Formatting - Black

- Format: `poetry run black .`
- Check only: `poetry run black --check .`

## Linting - Ruff

- Lint: `poetry run ruff check`
- Config: `pyproject.toml` (`[tool.ruff]`, `[tool.ruff.lint]`)

## Type Checking - Pyright

- Type-check: `poetry run pyright`
- Config: `pyproject.toml` (`[tool.pyright]`, strict mode)

## Testing - Pytest

- Run tests: `poetry run pytest`
- Config: `pytest.ini`, `docs/unit-test-policy.md`

## Coverage

- With coverage: `poetry run pytest --cov=. --cov-report=term-missing`
- HTML report: `poetry run coverage html` → `htmlcov/index.html`

## Pre-commit Hooks

- Install: `poetry run pre-commit install`
- Manual run: `poetry run pre-commit run --all-files`
- Hooks include Black, Ruff, Pyright, plus guard rails.

## VS Code Tasks (`.vscode/tasks.json`)

- `Black: format` → `poetry run black .`
- `Ruff: lint` → `poetry run ruff check`
- `Pyright: type-check` → `poetry run pyright`
- `Pytest: run tests` → `poetry run pytest`
- `Run All Checks` → Black → Ruff → Pyright → Pytest
- `Fix All` → `scripts/fix-all.ps1`
- Feature helpers:
  - `Feature: New Potential Entry` → `scripts/new-potential-entry.ps1`
  - `GitHub: Feature Issue from Potential` → `scripts/potential-to-issue.ps1`
  - `Feature: Create Active Folder` → `scripts/new-active-feature-folder.ps1`
  - `GitHub: Link Feature Docs` → `scripts/link-feature-docs.ps1`
- Run via Terminal → Run Task (or Command Palette “Tasks: Run Task”).

## PowerShell Scripts (`scripts/`)

### fix-all.ps1

- Runs Black → Ruff → Pyright → Pytest; stops on first failure.

### collect-commit-context.ps1

- Builds `artifacts/commit_context.txt` with remotes, status, diffs, stats, and last commit info.

### collect-pull-request-context.ps1

- Builds `artifacts/pr_context.txt` for PR drafting (branch info, diffs, summaries).

### Feature workflow helpers

- `new-potential-entry.ps1`Create dated potential doc from template; opens the file + backlog.
- `potential-to-issue.ps1`Promote potential to GitHub issue via `gh`; moves doc to `docs/features/potential/promoted/` and stamps issue info.
- `new-active-feature-folder.ps1`Seed `docs/features/active/<feature>/` from templates; auto-fill headers; seed sections from matching potential/promoted doc; can auto-read issue number.
- `link-feature-docs.ps1`
  Add/update “Feature Docs” section in a GitHub issue with links to user-story/spec/plan; skips if issue body is empty.

## Profiling - VizTracer

- Profile a test: `poetry run viztracer -m pytest tests/path/to/test_module.py`
- Profile CLI: `poetry run viztracer python -m transcript_etl_pipeline.cli run --source clipboard --format docx`
- Open the generated trace in a browser to inspect timelines and call stacks.
