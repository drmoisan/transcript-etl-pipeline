# 2025-11-30-speakerless_pipeline_integration - Spec

- Issue: N/A
- Owner: drmoisan
- Last Updated: 2025-12-03

## Overview

Integrate speakerless detection into the ETL pipeline so unlabeled transcripts are auto-assigned speakers and flow through normalize/format/output without manual labels.

## Behavior

- Entry point checks for speaker labels; if absent, runs speakerless detection to assign Speaker A/B/C/D.
- Supports 2–4 speaker scenarios with reasonable assignments.
- Downstream processing (parse/format) is unchanged for labeled inputs; no regression to labeled workflows.

## Inputs / Outputs

- Inputs: transcripts without explicit speaker labels (clipboard or file).
- Outputs: transcripts with assigned speaker labels flowing into DOCX/RTF/MD outputs; consistent formatting rules preserved.

## API / CLI Surface

- No new CLI flags; pipeline auto-detects speakerless input and applies detection. Uses existing CLI options for source/format/output.

## Data & State

- Uses existing speakerless heuristics for assignment; passes assigned labels into document model and formatters.

## Constraints & Risks

- Must not break labeled transcript processing.
- Accuracy expectations focused on 2–4 speaker scenarios; advanced refinements tracked elsewhere.
- Tooling (black/ruff/pyright/pytest) must remain green.

## Definition of Done

- [x] Speakerless detection invoked when no labels present.
- [x] Labeled transcripts remain unaffected.
- [x] Formats (DOCX/RTF/MD) render with assigned speakers.
- [x] Tests/tooling passing.

## Seeded Test Conditions

- [x] Integration tests for speakerless detection on sample transcripts (2–4 speakers).
- [x] Verify labeled transcripts bypass speakerless path.
