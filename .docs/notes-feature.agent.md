# Agent Instructions: Notes Feature Implementation

This document contains detailed instructions for implementing the Unified Notes + Transcript feature.
**Reference**: `docs/notes-feature-plan.md`
**User Story**: `docs/notes-feature-user-story.md`

## Policies
You must strictly adhere to:
1.  `docs/code-change.instructions.md` (Coding standards, Typing, Testing)
2.  `docs/unit-test-policy.md` (Test independence, AAA pattern)
3.  `docs/developer-tooling.md` (Use `poetry run ...`)

## Step-by-Step Implementation Guide

### Step 1: Domain Model Updates
**File**: `src/transcript_etl_pipeline/document/model.py`
1.  Update `SectionType` enum:
    *   Add `NOTES_HEADER = "notes_header"`
    *   Add `NOTES_BODY = "notes_body"`
2.  Update `Paragraph` dataclass:
    *   Add `is_bullet: bool = False`
3.  Update `Document` class:
    *   Implement `merge_notes(self, new_sections: list[DocumentSection], mode: str) -> None`.
        *   `mode` can be "add" or "replace".
        *   "add": Insert new sections before existing Notes (or at top if none). *Correction per User Story*: "New notes are added **at the top**, above all previous notes."
        *   "replace": Remove all existing `NOTES_*` sections, then insert new ones at top.
    *   Implement `merge_transcript(self, new_sections: list[DocumentSection], mode: str) -> None`.
        *   "add": Append to end.
        *   "replace": Remove all `TRANSCRIPT_*` and `SPEAKER_*` sections, then append.
4.  **Test**: Create `tests/document/test_model_merge.py` verifying add/replace behavior and section ordering.

### Step 2: Notes Transformation
**File**: `src/transcript_etl_pipeline/transform/notes.py` (Create new)
1.  Create function `transform_notes(text: str, label: str | None = None) -> list[DocumentSection]`.
2.  **Logic**:
    *   Create a `DocumentSection(type=NOTES_HEADER)`.
    *   Add a `Paragraph` with the label (e.g., "Notes – 2025-01-01"). If `label` arg is None, generate one with current timestamp.
    *   Create a `DocumentSection(type=NOTES_BODY)`.
    *   Parse `text` (Markdown):
        *   Lines starting with `- ` or `* ` -> `Paragraph(is_bullet=True)`.
        *   Other lines -> `Paragraph(is_bullet=False)`.
    *   Return the list of sections.
3.  **Test**: Create `tests/transform/test_notes.py`.

### Step 3: Document Reader (Re-ingestion)
**File**: `src/transcript_etl_pipeline/document/reader.py` (Create new)
1.  Define `DocumentReader` Protocol (optional but good for design).
2.  Implement `read_document(path: Path) -> Document`.
    *   Dispatch to `_read_markdown` or `_read_docx` based on extension.
3.  **Markdown Reader**:
    *   Read file.
    *   Split by headers (`# Notes`, `Transcript:`).
    *   Reconstruct `Document` with correct `SectionType`s.
4.  **DOCX Reader**:
    *   Use `python-docx`.
    *   Iterate paragraphs.
    *   Identify Headers -> Start new Section.
    *   Identify Bullets -> `Paragraph(is_bullet=True)`.
    *   **Note**: This is complex. Start with a robust "Best Effort" that relies on the specific headers we generate.
5.  **Test**: Create `tests/document/test_reader.py`. Use sample files (create them in test setup) to verify round-trip (Write -> Read -> Verify Model).

### Step 4: Formatters Update
**Files**: `src/transcript_etl_pipeline/formatters/*.py`
1.  **DOCX**:
    *   Handle `NOTES_HEADER`: Apply "Heading 1" or Bold + 14pt.
    *   Handle `NOTES_BODY`:
        *   If `is_bullet`: Set paragraph style to "List Bullet".
2.  **Markdown**:
    *   Handle `NOTES_HEADER`: Output `# {text}`.
    *   Handle `NOTES_BODY`:
        *   If `is_bullet`: Prefix with `- `.
3.  **RTF**:
    *   Add basic formatting for headers and bullets.
4.  **Test**: Update existing formatter tests or add `tests/formatters/test_notes_formatting.py`.

### Step 5: CLI & UI
**Files**: `src/transcript_etl_pipeline/cli.py`, `src/transcript_etl_pipeline/ui.py`
1.  **CLI**:
    *   Add `--mode {new,update}`.
    *   Add `--notes-source {file,clipboard}`.
    *   Add `--notes-file {path}`.
    *   Add `--update-file {path}` (for existing doc).
    *   Implement the logic to orchestrate Extract -> Transform -> Merge -> Load.
2.  **UI**:
    *   This is a larger task. Implement the "Decision Tree" from the User Story.
    *   Use `tkinter` dialogs.
    *   Ensure "Cancel" works gracefully at every step.

### Step 6: Integration
1.  Create `tests/test_end_to_end_notes.py`.
2.  Simulate the user story scenarios:
    *   Scenario 1: Create New (Notes + Transcript).
    *   Scenario 2: Update Existing (Add Notes).
    *   Scenario 3: Update Existing (Replace Transcript).

## Development Workflow
1.  **Read** the plan and these instructions.
2.  **Implement** one step at a time.
3.  **Verify** each step using the "After Making Changes" workflow defined in `docs/code-change.instructions.md`:
    *   Format (`poetry run black .`)
    *   Lint (`poetry run ruff check`)
    *   Type Check (`poetry run pyright`)
    *   Test (`poetry run pytest`)
4.  **Iterate** until all checks pass before moving to the next step.

**Crucial**: Do not break existing Transcript-only functionality. The new features must be additive or compatible.
