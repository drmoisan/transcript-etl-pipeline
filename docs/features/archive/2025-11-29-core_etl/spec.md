# 2025-11-29-core_etl - Spec

- Issue: N/A
- Owner: drmoisan
- Last Updated: 2025-12-03

## Overview

Core transcript ETL pipeline that ingests transcripts from clipboard/files, normalizes/enhances them (including speakerless handling), parses into a document model, and outputs DOCX/RTF/Markdown with deterministic formatting rules.

## Behavior

- Extract: clipboard or file ingest with UTF-8/UTF-16 detection; clear errors on unsupported types.
- Transform: normalization (line endings, whitespace, label normalization); paragraph detection; speaker handling and speakerless detection.
- Document parsing: build Document model with metadata, labels, paragraphs; enforce ordering and spacing rules.
- Load: formatters for DOCX, RTF, and Markdown applying consistent fonts/spacing; deterministic headers/paragraph spacing.
- CLI/UI: CLI flags for source, file, format, output name/folder; thin UI prompts when flags are missing.

## Inputs / Outputs

- Inputs: clipboard text; transcript files (UTF-8/UTF-16); CLI flags for source (`--source`), file path, format (`--format docx|rtf|md`), output name/folder.
- Outputs: DOCX, RTF, MD files with metadata + transcript sections; spacing and label formatting per formatting rules.

## API / CLI Surface

- CLI examples:
  - `--source clipboard|file`
  - `--file <path>` (when source=file)
  - `--format docx|rtf|md`
  - `--output-name <name>`; `--output-folder <path>`
- Thin UI prompts for missing required flags.

## Data & State

- Document model (labels, paragraphs, sections, metadata) with deterministic ordering.
- Formatting rules define fonts (10pt Calibri), bold labels, spacing (metadata single-spaced; 12pt above labels, 6pt above paragraphs).
- Parser/formatter round-trip alignment for DOCX/RTF/MD.

## Constraints & Risks

- Must preserve deterministic formatting across outputs.
- Pyright strict, ruff/black compliance required.
- Speakerless detection and speaker handling must not regress two-speaker accuracy.
- Clipboard availability handled with graceful errors/fallbacks.

## Definition of Done

- [X] Behavior matches acceptance criteria (core ETL completed).
- [X] Tests updated/added (unit + integration + end-to-end) and passing.
- [X] Docs updated (core ETL status/instructions archived).
- [X] Tooling checks clean (black/ruff/pyright/pytest).

## Seeded Test Conditions

- [X] Unit: document model/parsing/formatting rules; normalization; extractors; speaker/speakerless handling.
- [X] Integration/E2E: clipboard/file inputs to DOCX/RTF/MD outputs with expected spacing/labels; error handling for bad inputs.
