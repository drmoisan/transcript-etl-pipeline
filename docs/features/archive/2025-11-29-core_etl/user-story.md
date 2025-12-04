# 2025-11-29-core_etl - User Story

- Issue: N/A
- Owner: drmoisan
- Status: Complete
- Last Updated: 2025-12-03

## Problem / Why

We needed a production-grade transcript ETL pipeline that can ingest transcripts from clipboard/files, normalize/enhance them (including speakerless handling), and output consistent DOCX/RTF/Markdown documents with deterministic formatting and robust error handling.

## Personas & Scenarios

- Persona: Analyst preparing meeting transcripts
  - Scenario: Convert raw transcript text into a formatted document without manual cleanup.
- Persona: Operator handling varying inputs
  - Scenario: Ingest transcripts from clipboard or UTF-8/UTF-16 files and get predictable outputs with labels/paragraphs intact.

## User Stories

- As a user, I want to run a single CLI to ingest transcripts (clipboard/file) and produce formatted DOCX/RTF/MD output with correct labels and spacing.
- As a user, I want the pipeline to normalize/enhance text (labels, paragraphs, speaker/speakerless) so I don’t fix formatting manually.

## Acceptance Criteria

- [X] Extract from clipboard and files (UTF-8/UTF-16) with clear errors on unsupported types.
- [X] Normalize transcripts (line endings, whitespace, label normalization).
- [X] Enhance transcripts (paragraph detection, speaker handling, speakerless detection).
- [X] Parse into a document model with deterministic ordering and formatting rules.
- [X] Output DOCX, RTF, and Markdown with consistent spacing and fonts.
- [X] CLI supports source selection, output format, and filenames; thin UI prompts when flags are missing.
- [X] All unit/integration tests passing; pyright/ruff/black clean.

## Non-Goals

- Advanced future enhancements (notes, optional formatting ideas, distribution targets) are out of scope for the core ETL archive.
