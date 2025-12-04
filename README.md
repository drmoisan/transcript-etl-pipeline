# Transcript ETL Pipeline

A Python toolkit for extracting, transforming, and formatting meeting transcripts with speaker-aware processing and multiple output formats (DOCX, RTF, Markdown).

[![Tests](https://img.shields.io/badge/tests-617%20passed-brightgreen)](https://github.com/drmoisan/transcript-etl-pipeline)
[![Coverage](https://img.shields.io/badge/coverage-16%25-red)](https://github.com/drmoisan/transcript-etl-pipeline)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000)](https://github.com/psf/black)
[![Type Checking](https://img.shields.io/badge/type%20checking-pyright%20strict-blue)](https://github.com/microsoft/pyright)

## What it does

- **Extract** from clipboard or text files.
- **Transform** with normalization, label cleanup, paragraph detection, and identity-aware speaker handling:
  - Self-identification (“I’m <Name>”) and addressee detection (“Thanks <Name>”) inform grouping.
  - Speakerless heuristics plus constraint-aware similarity grouping to reduce over/under-splitting.
- **Load** to DOCX, RTF, or Markdown with consistent spacing and styling.
- **Operate** via CLI (argparse) or interactive UI (tkinter) when arguments are missing.
- **Log** to console and file for diagnostics.

## Install

```bash
git clone https://github.com/drmoisan/transcript-etl-pipeline.git
cd transcript-etl-pipeline
poetry install
```

## Quick start

```bash
# Process a transcript file to DOCX
transcript-etl --source file --file transcript.txt --format docx --output-folder ~/Documents

# Process from clipboard to Markdown
transcript-etl --source clipboard --format md --output-name meeting_notes.md --output-folder ~/Documents

# Interactive UI (prompts for missing args)
transcript-etl

# Help
transcript-etl --help
```

### Programmatic use

```python
from transcript_etl_pipeline.extract.from_file import extract_from_file
from transcript_etl_pipeline.transform.normalize import normalize_text
from transcript_etl_pipeline.transform.enhance import enhance_text
from transcript_etl_pipeline.document.parser import parse_enhanced_text
from transcript_etl_pipeline.formatters.docx_formatter import format_to_docx

raw_text = extract_from_file("transcript.txt")
normalized = normalize_text(raw_text)
enhanced, speaker_map = enhance_text(normalized)
document = parse_enhanced_text(enhanced)
format_to_docx(document, "output.docx")
```

## Repo map

- `src/transcript_etl_pipeline/`: core pipeline (extract, transform, document model, formatters, CLI/UI, logging).
- `tests/`: unit and integration coverage for pipeline behaviors and formatters.
- `docs/features/`: feature workflow (potential, promoted, active, archive) with templates.
- `scripts/`: PowerShell automation
  - `new-potential-entry.ps1`: create potential feature docs.
  - `potential-to-issue.ps1`: open a GitHub issue from a potential and promote it.
  - `new-active-feature-folder.ps1`: create/seed active feature folders from templates plus potential/promoted docs.
  - `link-feature-docs.ps1`: add feature doc links to an issue.
  - `collect-commit-context.ps1`, `collect-pull-request-context.ps1`: gather Git context for AI-assisted messages.
- `.vscode/tasks.json`: tasks to run checks, manage features, and call the scripts above.

## Development workflow

```bash
# Format
poetry run black .

# Lint
poetry run ruff check

# Type-check
poetry run pyright

# Tests
poetry run pytest
```

VS Code tasks (Terminal → Run Task):
- `Run All Checks` (Black, Ruff, Pyright, Pytest)
- `Fix All` (repo script)
- Feature helpers: `Feature: New Potential Entry`, `GitHub: Feature Issue from Potential`, `Feature: Create Active Folder`, `GitHub: Link Feature Docs`

## Testing status (latest run)

- Command: `poetry run pytest --maxfail=1 --disable-warnings --cov=src/transcript_etl_pipeline --cov-report=term`
- Result: 617 passed, 1 xfailed (expected: 3-speaker SpaceX fixture), 0 failed
- Coverage: 16% (includes CLI/UI and legacy modules)

## Feature workflow (docs/features/)

- Potential ideas in `docs/features/potential/` (or `.../promoted/` after an issue is created).
- Active work in `docs/features/active/<feature>/` with `user-story.md`, `spec.md`, and `plan.md` from templates.
- Archive completed features under `docs/features/archive/<date>-<feature>/`.
- Backlog overview in `docs/features/backlog.md`.

## Troubleshooting

- **tkinter missing**: supply all CLI args to avoid UI, or install tkinter for your OS.
- **Clipboard access**: ensure OS clipboard permissions; on Linux install `python3-tk`.
- **Speaker resolution quirks**: best results with well-formatted transcripts; identity hints (names/attendees) improve grouping.
- Logs: `~/.transcript_etl/pipeline.log` (console INFO+, file DEBUG+).

## Contributing

1. Branch from `development`.
2. Keep Black/Ruff/Pyright clean and add/adjust tests.
3. Run `poetry run pytest` (or `Run All Checks` task).
4. Open a PR referencing the relevant feature/issue.

## License

MIT (see `LICENSE`).
