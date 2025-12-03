# Developer Tooling

This document summarizes the core developer tooling for `transcript-etl-pipeline`: what it is for, and the basic commands you should run during everyday development.

All commands below assume you are in the project root and have run:

- `poetry install` – create the managed `.venv` with runtime + dev dependencies.
- `poetry run pre-commit install` – install local git hooks that mirror CI behavior.

You can either activate the Poetry virtualenv (`poetry shell`) or prefix commands with `poetry run`.

**Note**: For the complete development workflow including when to run these tools, see [code-change.instructions.md](code-change.instructions.md).

## Formatting – Black

- **Purpose**: Enforce a consistent, automatic code style across the project.
- **Primary command**:
  - Format in place: `poetry run black .`
  - Check only (no writes): `poetry run black --check .`
- **When to use**: Before committing, or whenever you touch Python code.

## Linting – Ruff

- **Purpose**: Catch common bugs and style issues (imports, unused variables, etc.).
- **Primary command**: `poetry run ruff check`
  - Configuration lives in `pyproject.toml` under `[tool.ruff]` and `[tool.ruff.lint]`.
- **When to use**: After formatting and before committing or opening a PR.

## Type Checking – Pyright

- **Purpose**: Enforce strict typing (`typeCheckingMode = "strict"`) for the `transcript_etl_pipeline` package.
- **Primary command**: `poetry run pyright`
  - Configuration: `[tool.pyright]` in `pyproject.toml`.
  - All source code and tests are type-checked in strict mode.
- **When to use**: Before any non-trivial change is merged. Avoid adding new Pyright errors.

## Testing – Pytest

- **Purpose**: Run the automated test suite to validate behavior.
- **Primary command**: `poetry run pytest`
  - Test configuration: `pytest.ini` and `docs/unit-test-policy.md`.
- **When to use**: Before pushing changes, and after any change to production code or tests.

## Coverage – Coverage.py / pytest-cov

- **Purpose**: Measure and report how much of the codebase is exercised by tests.
- **Typical commands**:
  - Run tests with coverage: `poetry run pytest --cov=. --cov-report=term-missing`
  - Generate HTML report: `poetry run coverage html` (open `htmlcov/index.html`).
- **When to use**: When validating how well new or refactored code is covered by tests.

## Pre-commit Hooks

- **Purpose**: Automatically run checks on changed files before every commit.
- **Configuration**: `.pre-commit-config.yaml` (Black, Ruff, Pyright, plus custom grep hooks).
- **Setup (once per machine)**: `poetry run pre-commit install`
- **Manual run** (optional): `poetry run pre-commit run --all-files`
- **Behavior**:
  - Reject commits that contain `DELETE_ME` or `REMOVE_BEFORE_MERGE` markers in Python code.
  - Format, lint, and type-check Python files according to project configuration.

## VS Code Tasks

If you use VS Code, `.vscode/tasks.json` defines one-click tasks that wrap the commands above:

- `Black: format` – runs `poetry run black .`
- `Ruff: lint` – runs `poetry run ruff check`
- `Pyright: type-check` – runs `poetry run pyright`
- `Pytest: run tests` – runs `poetry run pytest`
- `Run All Checks` – runs all quality checks sequentially (Black → Ruff → Pyright → Pytest)
- `Fix All` – runs the automated fix script (`scripts/fix-all.ps1`)

You can invoke these via **Terminal → Run Task…** (or the Command Palette: "Tasks: Run Task").

## PowerShell Scripts

The repository includes several PowerShell scripts in the `scripts/` directory for automation:

### fix-all.ps1

- **Purpose**: Automated fix-and-validate workflow that runs all quality checks sequentially.
- **Command**: `.\scripts\fix-all.ps1` or via VS Code task: "Fix All"
- **Behavior**:
  1. Runs Black formatter
  2. Runs Ruff linter
  3. Runs Pyright type checker
  4. Runs Pytest test suite
  5. Exits on first failure, providing clear error messages
- **When to use**: Quick validation before committing or when you want to run the full quality check sequence.

### collect-commit-context.ps1

- **Purpose**: Generate comprehensive commit context for creating detailed commit messages.
- **Command**: `.\scripts\collect-commit-context.ps1`
- **Output**: Creates `artifacts/commit_context.txt` with:
  - Repository remotes and branch information
  - Git status (staged and unstaged files)
  - Full unified diffs of all changes
  - Diff statistics
  - List of changed Python files
  - Last commit information
- **When to use**: Before committing significant changes to generate context for commit messages.

## Profiling – VizTracer

- **Purpose**: Profile and visualize performance hotspots in the codebase.
- **Usage examples**:
  - Profile a specific test module:
    `poetry run viztracer -m pytest tests/path/to/test_module.py`
  - Profile the CLI entry point:
    `poetry run viztracer python -m transcript_etl_pipeline.cli run --source clipboard --format docx`
- **Output**: VizTracer produces a trace file that you can open in a browser to inspect timelines and call stacks.
- **When to use**: When investigating performance issues or optimizing critical paths.
