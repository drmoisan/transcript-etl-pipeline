# 2025-11-30-speakerless_pipeline_integration - User Story

- Issue: N/A
- Owner: drmoisan
- Status: Complete
- Last Updated: 2025-12-03

## Problem / Why

Need to integrate speakerless detection into the ETL pipeline so transcripts without speaker labels can be processed end-to-end with reliable speaker assignment and without breaking existing workflows.

## Personas & Scenarios

- Persona: User ingesting unlabeled transcripts  
  - Scenario: Clipboard/file input with no speaker labels; expects sensible speaker assignments and formatted outputs without manual labeling.

## User Stories

- As a user, I want unlabeled transcripts to get speaker assignments automatically so I can use the pipeline without pre-labeling.
- As a user, I want speakerless detection integrated into the pipeline without regressing existing labeled/speaker-aware flows.

## Acceptance Criteria

- [x] Speakerless detection integrated into pipeline entry points.
- [x] Handles 2–4 speakers with sensible assignment.
- [x] No regressions to existing labeled transcript processing.
- [x] Tooling/tests passing (black/ruff/pyright/pytest).

## Non-Goals

- Not covering advanced multi-speaker similarity refinements (tracked separately).
