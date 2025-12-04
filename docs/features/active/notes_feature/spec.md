# notes_feature - Spec

- Issue: #14
- Owner: drmoisan
- Last Updated: 2025-12-03

## Overview

Enable the pipeline to ingest, process, and merge both transcripts and markdown notes into a single consolidated document. Support creating new documents or updating existing ones by adding or replacing notes/transcript sections, while maintaining deterministic ordering (Metadata → Notes → Transcript).

## Behavior

- Start-of-operation prompt: choose New Document vs Update Existing.
- New Document:
  - Notes only: ingest from clipboard or markdown file; normalize; place at top with header (user label or timestamp).
  - Transcript only: ingest from clipboard or file; normalize; place at bottom.
  - Both: notes at top, transcript at bottom in one output.
- Update Existing Document:
  - Detect existing sections (notes/transcript) in DOCX/MD.
  - Options: Add Notes (prepend with label/timestamp), Replace Notes, Add Transcript (append), Replace Transcript.
- Notes differentiation: each imported notes block gets user-provided label or auto-generated timestamp.
- Output formats: DOCX and Markdown (RTF if already supported) use existing ETL formatting conventions.

## Inputs / Outputs

- Inputs:
  - Notes source: clipboard or file (markdown).
  - Transcript source: clipboard or file (text).
  - Mode: new vs update.
  - Update actions: add/replace for notes and transcript.
  - Optional labels for notes blocks; otherwise auto timestamp.
- Outputs:
  - Consolidated document (DOCX/MD/RTF if enabled) with Notes above Transcript.
  - Headers to anchor sections (e.g., “# Notes - <timestamp>”, “# Transcript - Part 1”).

## API / CLI Surface

- CLI flags (examples):
  - `--notes-source clipboard|file`
  - `--notes-file <path>`
  - `--transcript-source clipboard|file`
  - `--transcript-file <path>`
  - `--mode new|update`
  - `--update-action-notes add|replace`
  - `--update-action-transcript add|replace`
  - `--notes-label <string>` (optional; else timestamp)
- UI: mirrors missing flags with prompts.

## Data & State

- Document model gains Notes sections (header/body), bullet support for notes paragraphs, and deterministic ordering (Metadata → Notes → Transcript).
- Reader re-ingests existing DOCX/MD to detect Notes/Transcript boundaries via headers/styles.
- Merge logic:
  - Add notes: prepend new notes block with label/timestamp.
  - Replace notes: remove existing notes blocks, insert new.
  - Add transcript: append to bottom.
  - Replace transcript: remove existing transcript blocks, insert new.

## Constraints & Risks

- Reuse normalization/formatting conventions; avoid regressions to transcript-only flows.
- Deterministic headers/anchors required for parsing existing docs.
- DOCX re-ingestion can be lossy; rely on strict header text/style matching.
- Clear errors: non-markdown notes, empty clipboard, unparsable existing document.
- Performance/compat: keep behavior consistent across DOCX/MD (and RTF if present).

## Definition of Done

- [ ] Behavior matches acceptance criteria (user story).
- [ ] Tests updated/added (unit + integration + end-to-end).
- [ ] Docs updated (README/examples and feature folder).
- [ ] Telemetry/logging if applicable.

## Seeded Test Conditions

- [ ] Unit: notes normalization; add/replace merge logic; label generation; document reader boundaries.
- [ ] Integration: new vs existing flows; notes-only, transcript-only, both; multi-import scenarios.
- [ ] CLI examples: notes source/file flags, modes (add/replace), new vs existing document paths.
