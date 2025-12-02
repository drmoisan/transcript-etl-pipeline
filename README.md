# Transcript ETL Pipeline

A Python tool for extracting, transforming, and formatting meeting transcripts with automatic speaker detection and multiple output formats (DOCX, RTF, Markdown).

[![Tests](https://img.shields.io/badge/tests-509%20passed-brightgreen)](https://github.com/drmoisan/transcript-etl-pipeline)
[![Coverage](https://img.shields.io/badge/coverage-87%25-brightgreen)](https://github.com/drmoisan/transcript-etl-pipeline)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000)](https://github.com/psf/black)
[![Type Checking](https://img.shields.io/badge/type%20checking-pyright%20strict-blue)](https://github.com/microsoft/pyright)

## Key Features

- **Extract** transcripts from clipboard or text files
- **Transform** with automatic:
  - Line ending normalization (CRLF)
  - Whitespace cleanup
  - Label detection and formatting
  - Paragraph detection using sentence endings and pause indicators
  - **Identity-aware speaker detection** with constraint enforcement:
    - Self-identification: "I'm [Name]" assigns sentences to [Name]
    - Address detection: "Thanks [Name]" prevents assignment to [Name]
    - Similarity grouping respects identity constraints
  - Speaker resolution with Dan Moisan identification
- **Load** to multiple formats:
  - Microsoft Word (DOCX) with proper spacing and fonts
  - Rich Text Format (RTF) 
  - Markdown (MD)
- **CLI** with argparse for automation
- **Interactive UI** with tkinter dialogs when arguments are missing
- **Configuration** storage for last output folder
- **Comprehensive Logging** with dual handlers (console INFO+, file DEBUG+) for diagnostics
- **Git Context Scripts** (PowerShell) for AI-assisted commit/PR message generation

## Installation

```bash
# Clone the repository
git clone https://github.com/drmoisan/transcript-etl-pipeline.git
cd transcript-etl-pipeline

# Install with Poetry
poetry install

# Or install for system-wide use
poetry build
pip install dist/transcript_etl_pipeline-0.1.0-py3-none-any.whl
```

## Quick Start

### CLI Usage

```bash
# Process a transcript file to DOCX
transcript-etl --source file --file transcript.txt --format docx --output-folder ~/Documents

# Process from clipboard to Markdown
transcript-etl --source clipboard --format md --output-name "meeting_notes.md" --output-folder ~/Documents

# Use interactive UI (prompts for missing arguments)
transcript-etl

# Show help
transcript-etl --help
```

### Programmatic Usage

```python
from transcript_etl_pipeline.extract.from_file import extract_from_file
from transcript_etl_pipeline.transform.normalize import normalize_text
from transcript_etl_pipeline.transform.enhance import enhance_text
from transcript_etl_pipeline.document.parser import parse_enhanced_text
from transcript_etl_pipeline.formatters.docx_formatter import format_to_docx

# Extract
raw_text = extract_from_file("transcript.txt")

# Transform
normalized = normalize_text(raw_text)
enhanced, speaker_map = enhance_text(normalized)

# Parse to document model
document = parse_enhanced_text(enhanced)

# Format and save
format_to_docx(document, "output.docx")
```

## Architecture

```
src/transcript_etl_pipeline/
├── extract/          # Input sources (file, clipboard)
├── transform/        # Normalization and enhancement
│   ├── normalize.py  # Line endings, whitespace, labels
│   ├── paragraphs.py # Paragraph detection
│   ├── identity_constraints.py  # Name extraction and constraint modeling
│   ├── speaker_helpers.py       # Constraint-aware similarity grouping
│   ├── speakerless.py           # NLTK-based speaker detection
│   ├── speakers.py   # Speaker resolution and Dan Moisan identification
│   └── enhance.py    # Orchestration
├── document/         # Document model
│   ├── model.py      # Data structures
│   ├── formatting_rules.py  # Spacing and font rules
│   └── parser.py     # Text to Document conversion
├── formatters/       # Output generators
│   ├── docx_formatter.py
│   ├── rtf_formatter.py
│   └── md_formatter.py
├── logging_config.py # Centralized logging configuration
├── cli.py           # Command-line interface
├── ui.py            # Interactive dialogs
└── config.py        # Configuration management

scripts/
├── collect-commit-context.ps1    # Generate Git context for commits
├── collect-pull-request-context.ps1  # Generate Git context for PRs
└── README.md                     # Scripts documentation
```

## Formatting Rules

All output formats follow consistent spacing and styling:

- **Font**: 10pt Calibri (DOCX, RTF) or bold markers (MD)
- **Labels**: Bold with single space after colon
- **Metadata**: No extra spacing between lines
- **Transcript label**: 12pt space above
- **Speaker paragraphs**: 12pt space above
- **Regular paragraphs**: 6pt space above
- **Line spacing**: Single (1.0)

## Testing

The project includes comprehensive test coverage with 509 tests:

- **Unit Tests**: 487 tests covering core functionality
  - Identity constraints extraction: 33 tests
  - Identity-aware speaker grouping: 17 tests
  - Speakerless transcript detection: 50+ tests with NLTK-based heuristics
  - Document formatting and parsing: 100+ tests
  - Transform pipeline (normalize, enhance, paragraphs): 150+ tests
- **Integration Tests**: 22 tests for end-to-end pipeline validation
- **Coverage**: 87% overall, 97%+ for core transformation logic
  - 100% coverage: formatters (RTF, MD), transform logic, document model, identity constraints
  - 97%+ coverage: parser, DOCX formatter, normalizer, speaker resolution, identity-aware grouping
  - Lower coverage: CLI/UI integration layers (tested via integration tests)

```bash
# Run all tests
poetry run pytest

# Run with coverage report
poetry run pytest --cov=src/transcript_etl_pipeline --cov-report=html
# Open htmlcov/index.html to view detailed coverage

# Run only unit tests
poetry run pytest tests/ -k "not integration"

# Run only integration tests
poetry run pytest tests/integration/

# Run with verbose output
poetry run pytest -v

# Run linters and type checking
poetry run black .
poetry run ruff check
poetry run pyright
```

### Test Organization

```
tests/
├── document/          # Document model and formatting rules
├── extract/           # File and clipboard extraction
├── formatters/        # DOCX, RTF, Markdown output
├── transform/         # Normalization, paragraphs, speakers
└── integration/       # End-to-end pipeline tests
    ├── test_parser.py           # Document parser integration
    ├── test_end_to_end_docx.py  # Full pipeline → DOCX
    ├── test_end_to_end_rtf.py   # Full pipeline → RTF
    └── test_end_to_end_md.py    # Full pipeline → Markdown
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/drmoisan/transcript-etl-pipeline.git
cd transcript-etl-pipeline

# Install dependencies with Poetry
poetry install

# Set up pre-commit hooks (optional)
poetry run pre-commit install
```

### Code Quality Tools

The project uses strict code quality standards:

```bash
# Format code with Black (line length 100)
poetry run black .

# Check code with Ruff linter
poetry run ruff check

# Fix auto-fixable Ruff issues
poetry run ruff check --fix

# Type checking with Pyright (strict mode)
poetry run pyright

# Run pre-commit hooks manually
poetry run pre-commit run --all-files
```

### Development Workflow

1. Make changes to code
2. Write/update tests for new functionality
3. Format code: `poetry run black .`
4. Check linting: `poetry run ruff check`
5. Check types: `poetry run pyright`
6. Run tests: `poetry run pytest`
7. Commit changes

All checks must pass before committing. Pre-commit hooks enforce this automatically.

## Troubleshooting

### tkinter Not Available

If you get "tkinter is not available" errors, provide all CLI arguments:

```bash
transcript-etl --source file --file input.txt --format docx \
  --output-name output.docx --output-folder ~/Documents
```

### Clipboard Access Issues

Ensure your system allows clipboard access. On Linux, you may need additional packages:

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora/RHEL
sudo dnf install python3-tkinter
```

### Speaker Resolution

The pipeline automatically identifies "Dan Moisan" by analyzing dialogue references. For other speakers:
- Names from metadata (Attendees line) are auto-detected
- Unknown speakers trigger UI prompt with sample utterances (if UI available)
- Use CLI with `--source` and all required arguments to skip UI prompts

### Logging and Diagnostics

Pipeline execution is logged to `~/.transcript_etl/pipeline.log` with:
- Stage-by-stage progress (Extract → Normalize → Enhance → Parse → Load)
- Character counts and speaker mappings
- Detailed error tracebacks
- Console output (INFO+) and file output (DEBUG+)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the code quality standards (Black, Ruff, Pyright)
4. Write tests for new functionality
5. Ensure all tests pass (`poetry run pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Project Status

✅ **Production Ready**

- Core ETL pipeline fully functional
- **Identity-aware speaker detection** with constraint enforcement (NEW)
- 509 tests with 87% coverage (all passing)
- All code quality checks passing (Black, Ruff, Pyright, Pytest)
- Multiple output formats supported (DOCX, RTF, MD)
- CLI and UI fully operational
- Comprehensive logging infrastructure
- PowerShell utilities for Git context collection

### Recent Enhancements (Dec 2025)

**Identity-Aware Speaker Detection**: The pipeline now enforces identity constraints during speaker assignment:
- ✅ Self-identification constraint: "I'm [Name]" correctly assigns sentences to [Name]
- ✅ Address detection: "Thanks [Name]" prevents assignment to [Name] (speaker cannot address themselves)
- ✅ Constraint-aware similarity grouping: Identity information overrides linguistic similarity
- ✅ Post-processing resolution: Conservative reassignment for addresses_other violations
- ✅ 50 new tests validating identity-aware behavior (33 extraction + 17 grouping)

This addresses critical flaws in multi-speaker scenarios where names are mentioned or self-identifications occur.

### Known Limitations

- Speaker resolution requires either metadata names or UI interaction
- UI dialogs require tkinter (can be bypassed with full CLI arguments)
- Best results with properly formatted transcript input
- Identity detection uses name extraction heuristics (e.g., "I'm [Name]", "Thanks [Name]")

## Acknowledgements

Built with:
- [python-docx](https://python-docx.readthedocs.io/) for DOCX generation
- [tkinter](https://docs.python.org/3/library/tkinter.html) for UI dialogs
- [Poetry](https://python-poetry.org/) for dependency management

