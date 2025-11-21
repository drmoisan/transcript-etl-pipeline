# Transcript ETL Pipeline - Implementation Status

## Completed Phases (1-3)

### Phase 1: Foundation & Data Models ✅
**Status**: Complete - 32 tests passing

**Implemented**:
- `src/transcript_etl_pipeline/document/model.py` - Core data structures:
  - `SectionType` enum for document sections
  - `Label` dataclass for labels (single-word capitalized tokens ending with colon)
  - `Paragraph` dataclass for paragraphs (with optional label)
  - `DocumentSection` for organizing paragraphs
  - `Document` for complete transcript representation
- `src/transcript_etl_pipeline/document/formatting_rules.py` - Formatting specifications:
  - Font styles (Calibri 10pt, bold for labels, normal for body)
  - Spacing rules (12pt before Transcript: and speaker labels, 6pt before regular paragraphs)
  - Helper functions to retrieve formatting rules

**Tests**: `tests/document/` - Full coverage of models and formatting rules

### Phase 2: Extract Stage ✅
**Status**: Complete - 18 tests passing

**Implemented**:
- `src/transcript_etl_pipeline/extract/from_file.py`:
  - Automatic encoding detection (UTF-8, UTF-16 with BOM, UTF-8 with BOM)
  - Support for .txt and .md files
  - Comprehensive error handling
- `src/transcript_etl_pipeline/extract/from_clipboard.py`:
  - Clipboard extraction using tkinter
  - Graceful handling when tkinter unavailable
  - Dependency injection for testability
  - Error handling for empty/inaccessible clipboard

**Tests**: `tests/extract/` - Full coverage with mocking for clipboard

### Phase 3: Transform Stage - Normalize ✅
**Status**: Complete - 27 tests passing

**Implemented**:
- `src/transcript_etl_pipeline/transform/normalize.py`:
  - Line ending normalization (all → CRLF)
  - Whitespace cleanup:
    - Remove duplicate spaces
    - Remove trailing spaces
    - Collapse multiple blank lines to single blank line
    - Remove trailing blank lines
  - Label normalization:
    - Detect single-word capitalized tokens ending with colon
    - Ensure labels at beginning of lines
    - Insert CRLF before mid-line labels
    - Ensure exactly one space after labels

**Tests**: `tests/transform/test_normalize.py` - Comprehensive coverage

---

## Remaining Phases (4-9)

### Phase 4: Transform Stage - Enhance
**Status**: Not started

**To Implement**:
1. `src/transcript_etl_pipeline/transform/paragraphs.py`:
   - Paragraph detection using heuristics:
     - Sentence endings (., ?, !)
     - Major pause indicators (line length analysis)
     - Label boundaries
     - Metadata termination (first label marks end of metadata)
   - Insert CRLF after each paragraph (but NOT at document end)

2. `src/transcript_etl_pipeline/transform/speakers.py`:
   - Speaker label detection and normalization
   - Dan Moisan identification logic:
     - Look for conversational references ("Dan, what do you think?")
     - Replace correct speaker label with "Dan Moisan:"
   - Auto-detection of other attendees using:
     - Names in metadata
     - Names in dialogue
     - Linguistic patterns (optional)
   - UI fallback for unresolved speakers (show samples, let user map)

3. `src/transcript_etl_pipeline/transform/enhance.py`:
   - Main enhancement orchestration
   - Call paragraphs and speakers modules in sequence

**Tests**: Create comprehensive tests for paragraph detection and speaker resolution

### Phase 5: Load Stage - Formatters
**Status**: Not started

**Dependencies to Add** (update `pyproject.toml`):
```toml
python-docx = "^1.0.0"  # For DOCX formatting
```

**To Implement**:
1. `src/transcript_etl_pipeline/formatters/docx_formatter.py`:
   - Use python-docx library
   - Apply spacing rules (before_pt, line_spacing)
   - Apply font rules (Calibri 10pt, bold labels)
   - Handle metadata (no extra spacing)
   - Handle Transcript: label (12pt above)
   - Handle speaker paragraphs (12pt above)
   - Handle regular paragraphs (6pt above)

2. `src/transcript_etl_pipeline/formatters/rtf_formatter.py`:
   - Generate RTF using string templates
   - Mirror DOCX formatting rules
   - RTF commands for spacing and fonts

3. `src/transcript_etl_pipeline/formatters/md_formatter.py`:
   - Simple Markdown output
   - Use **bold** for labels
   - Use blank lines for spacing approximation
   - Preserve paragraph structure

**Tests**: Verify each formatter produces correct output matching formatting rules

### Phase 6: CLI Implementation
**Status**: Not started

**To Implement**:
1. `src/transcript_etl_pipeline/config.py`:
   - Store last output folder in `~/.transcript_etl/last_output_folder.json`
   - Helper functions to read/write config

2. `src/transcript_etl_pipeline/cli.py`:
   - Use argparse for CLI
   - Commands:
     ```
     transcript-etl run [--source clipboard|file] [--file PATH] 
                        [--format docx|rtf|md] [--output-name NAME]
                        [--output-folder PATH]
     ```
   - If required args missing → launch thin UI
   - Default format: docx
   - Default output folder: from config or prompt
   - Default output name: auto-generate "YYYY MM DD <MeetingTitle>.ext"

**Tests**: Test CLI argument parsing and validation

### Phase 7: UI Implementation
**Status**: Not started

**To Implement**:
1. `src/transcript_etl_pipeline/ui.py`:
   - Source selection dialog (Clipboard / File)
   - File picker (if source=file)
   - Format selection (DOCX / RTF / MD)
   - Output name input dialog
   - Output folder picker
   - Speaker resolution dialog (show samples, let user map)
   - Graceful cancel handling with popup messages

**Tests**: Mock tkinter dialogs and test UI logic

### Phase 8: Integration & Testing
**Status**: Not started

**To Implement**:
1. Wire complete pipeline in main CLI entry point
2. End-to-end tests:
   - Sample transcript → DOCX with correct formatting
   - Sample transcript → RTF with correct formatting
   - Sample transcript → MD with correct formatting
3. Verify formatting consistency across all output types
4. Test full pipeline with various edge cases

### Phase 9: Final Validation
**Status**: Not started

**To Implement**:
1. Run full test suite with coverage:
   ```bash
   poetry run pytest --cov=src/transcript_etl_pipeline --cov-report=html
   ```
2. Verify all tooling passes:
   - Black formatting
   - Ruff linting
   - Pyright type checking
3. Update README.md with:
   - Project description
   - Installation instructions
   - Usage examples (CLI and programmatic)
   - Architecture overview
4. Security review with CodeQL

---

## Development Guidelines

### Always Follow
- **Unit Test Policy**: `docs/unit-test-policy.md`
- **Code Change Instructions**: `docs/code-change.instructions.md`
- **Developer Tooling**: `docs/developer-tooling.md`

### Testing Standards
- All new code must have tests
- Follow AAA pattern (Arrange-Act-Assert)
- Tests must be independent, isolated, deterministic
- Use mocks/stubs for external dependencies
- Clear docstrings explaining test purpose

### Code Quality
- Black formatting (line length 100)
- Ruff linting (enabled: E, F, B, I, UP, SIM)
- Pyright strict type checking
- Full type annotations
- Comprehensive docstrings

### Architecture Principles
1. Simplicity first
2. Separation of concerns (pure logic separate from I/O)
3. Testability (dependency injection where needed)
4. Reusability (DRY principle)
5. Extensibility (easy to add new formatters, extractors, etc.)

---

## Current Statistics
- **Total Tests**: 77 passing
- **Test Coverage**: High (document, extract, transform/normalize modules)
- **Code Quality**: All checks passing (Black, Ruff, Pyright)
- **Files Created**: 22 (9 source, 13 test/config files)

## Next Steps
1. Continue with Phase 4: Implement paragraph detection and speaker handling
2. Move to Phase 5: Implement formatters (DOCX first, then RTF, then MD)
3. Phase 6-7: Build CLI and UI
4. Phase 8-9: Integration testing and final validation
