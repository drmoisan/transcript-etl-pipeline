# Transcript ETL Pipeline

A Python tool for extracting, transforming, and formatting meeting transcripts with automatic speaker detection and multiple output formats (DOCX, RTF, Markdown).

## Key Features

- **Extract** transcripts from clipboard or text files
- **Transform** with automatic:
  - Line ending normalization (CRLF)
  - Whitespace cleanup
  - Label detection and formatting
  - Paragraph detection using sentence endings and pause indicators
  - Speaker resolution with Dan Moisan identification
- **Load** to multiple formats:
  - Microsoft Word (DOCX) with proper spacing and fonts
  - Rich Text Format (RTF) 
  - Markdown (MD)
- **CLI** with argparse for automation
- **Interactive UI** with tkinter dialogs when arguments are missing
- **Configuration** storage for last output folder

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
│   ├── speakers.py   # Speaker resolution
│   └── enhance.py    # Orchestration
├── document/         # Document model
│   ├── model.py      # Data structures
│   ├── formatting_rules.py  # Spacing and font rules
│   └── parser.py     # Text to Document conversion
├── formatters/       # Output generators
│   ├── docx_formatter.py
│   ├── rtf_formatter.py
│   └── md_formatter.py
├── cli.py           # Command-line interface
├── ui.py            # Interactive dialogs
└── config.py        # Configuration management
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

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src/transcript_etl_pipeline --cov-report=html

# Run linters
poetry run black .
poetry run ruff check
poetry run pyright
```

## Development

```bash
# Format code
poetry run black .

# Check linting
poetry run ruff check

# Type checking
poetry run pyright

# Run pre-commit hooks
poetry run pre-commit run --all-files
```

## Troubleshooting

### tkinter Not Available

If you get "tkinter is not available" errors, provide all CLI arguments:

```bash
transcript-etl --source file --file input.txt --format docx \
  --output-name output.docx --output-folder ~/Documents
```

### Clipboard Access Issues

Ensure your system allows clipboard access. On Linux, you may need additional packages.

## Acknowledgements

Built with:
- [python-docx](https://python-docx.readthedocs.io/) for DOCX generation
- [tkinter](https://docs.python.org/3/library/tkinter.html) for UI dialogs
- [Poetry](https://python-poetry.org/) for dependency management

