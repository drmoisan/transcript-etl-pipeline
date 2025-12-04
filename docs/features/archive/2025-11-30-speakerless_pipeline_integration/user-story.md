# 2025-11-30-speakerless_pipeline_integration - User Story

- Issue: N/A
- Owner: drmoisan
- Status: Complete
- Last Updated: 2025-12-03

## Story Statement

- As a user with unlabeled transcripts, I want automatic speaker detection and assignment, so that I can process transcripts without manually adding speaker labels.
- As a user, I want speakerless detection to work seamlessly alongside labeled transcripts, so that my existing workflows aren't disrupted.

## Problem / Why

Need to integrate speakerless detection into the ETL pipeline so transcripts without speaker labels can be processed end-to-end with reliable speaker assignment and without breaking existing workflows.

## Personas & Scenarios

- **Persona: Interview Transcriber**
  - **Who they are**: A researcher who transcribes interview recordings where speaker labels aren't provided by the transcription service
  - **What they care about**: Getting usable transcripts with correct speaker assignments without manual labeling work
  - **Their constraints**: Works with 2-4 speaker conversations; no time to manually label speakers before processing
  - **Their goals**: Process raw transcripts end-to-end with automatic speaker detection; maintain quality of existing labeled transcript workflows
  - **Their frustrations**: Many transcription services provide raw text without speaker labels; manual speaker labeling is tedious and error-prone
  - **Their context**: Processes 10-15 interview transcripts monthly; needs automation to handle both labeled and unlabeled inputs

- **Scenario: Processing Unlabeled Interview Transcript**
  - **Who is acting?** Marcus, a UX researcher transcribing customer interviews
  - **What triggered the action?** Marcus received a raw transcript from an automated transcription service with no speaker labels
  - **What steps do they take?**
    1. Marcus pastes the unlabeled transcript into the ETL pipeline
    2. The tool automatically detects that no speaker labels are present
    3. The speakerless detection algorithm analyzes conversation patterns
    4. Speaker labels (A, B, C, etc.) are assigned based on detected speaker changes
    5. The formatted document outputs with sensible speaker assignments
  - **What obstacles or decisions occur?**
    - Transcript has no explicit speaker markers
    - Algorithm must handle 2-4 speakers reliably
    - Existing labeled transcript workflows must continue working
  - **What outcome do they expect?**
    - Automatic speaker assignments for unlabeled transcripts (2-4 speakers)
    - Formatted output with speaker labels even though input had none
    - No regression to existing labeled transcript processing
    - End-to-end pipeline integration without workflow changes

## Acceptance Criteria

- [x] Speakerless detection integrated into pipeline entry points.
- [x] Handles 2–4 speakers with sensible assignment.
- [x] No regressions to existing labeled transcript processing.
- [x] Tooling/tests passing (black/ruff/pyright/pytest).

## Non-Goals

- Not covering advanced multi-speaker similarity refinements (tracked separately).
