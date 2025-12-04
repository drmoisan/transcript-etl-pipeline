# 2025-11-29-core_etl - Plan

- Issue: N/A
- Owner: drmoisan
- Last Updated: 2025-12-03

## Required References (read, do not restate)

- Coding workflow and standards: [`docs/code-change.instructions.md`](../../../code-change.instructions.md)
- Unit test policy: [`docs/unit-test-policy.md`](../../../unit-test-policy.md)

**All work must comply with these policies; do not duplicate their content here.**

## Phases

### Phase 1: Foundation & Data Models [100%] 🟩

- [X] Build document model (labels, paragraphs, sections) and formatting rules.
- [X] Implement parser for metadata/sections/paragraphs.
- [X] Unit tests for model/parsing/formatting rules.

### Phase 2: Extract Stage [100%] 🟩

- [X] Clipboard and file ingestion with UTF-8/UTF-16 detection.
- [X] Error handling for unsupported types/empty clipboard.
- [X] Unit tests for extractors.

### Phase 3: Transform (Normalize/Enhance) [100%] 🟩

- [X] Normalization (line endings, whitespace, label normalization).
- [X] Paragraph detection and speaker handling; speakerless detection.
- [X] Unit/integration tests for transform logic.

### Phase 4: Document Parsing/Reader [100%] 🟩

- [X] Parse enhanced text into Document model; metadata detection; section inference.
- [X] Tests for parser boundaries and ordering.

### Phase 5: Formatters (DOCX/RTF/MD) [100%] 🟩

- [X] Apply fonts/spacing/labels consistently across DOCX, RTF, MD.
- [X] Unit tests for formatter output.

### Phase 6: CLI/UI & End-to-End [100%] 🟩

- [X] CLI flags for source/file/format/output; thin UI prompts for missing flags.
- [X] End-to-end flows from clipboard/file to DOCX/RTF/MD outputs.
- [X] All checks passing (black/ruff/pyright/pytest).

## Test Plan

- Unit: extractors, normalization/enhance, parser, document model/formatting, speaker/speakerless logic.
- Integration/E2E: clipboard/file inputs to DOCX/RTF/MD outputs; spacing/label assertions; error handling paths.

## Open Questions / Notes

- Archived as completed core ETL implementation (510 tests passing, pyright/ruff/black clean).
