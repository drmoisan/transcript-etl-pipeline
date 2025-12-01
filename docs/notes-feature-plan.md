# Implementation Plan: Unified Notes + Transcript Feature

## 1. Objective
Enable the ETL pipeline to ingest, process, and merge both **Transcripts** and **Markdown Notes** into a single consolidated document. Support creating new documents or updating existing ones (DOCX/MD) by adding or replacing sections.

## 2. Architecture Changes

### 2.1 Data Model (`src/transcript_etl_pipeline/document/model.py`)
*   **`SectionType` Enum**: Add `NOTES_HEADER` and `NOTES_BODY`.
*   **`Paragraph` Dataclass**: Add `is_bullet: bool` field to support bulleted notes.
*   **`Document` Class**:
    *   Add methods for content management:
        *   `merge_notes(sections: list[DocumentSection], mode: MergeMode)`
        *   `merge_transcript(sections: list[DocumentSection], mode: MergeMode)`
    *   Ensure strict ordering: Metadata -> Notes -> Transcript.

### 2.2 Extraction & Transformation
*   **Extract**: New logic to read Notes from Clipboard or File.
*   **Transform**:
    *   New `transform/notes.py` module.
    *   Parse Markdown notes into `DocumentSection` objects.
    *   Handle "Notes Differentiation" (auto-generating headers with timestamps).

### 2.3 Document Re-ingestion (Reader)
*   New `src/transcript_etl_pipeline/document/reader.py` module.
*   **Purpose**: Parse *existing* output files (DOCX, MD) back into the `Document` model to support the "Add to Existing" workflow.
*   **Strategies**:
    *   **Markdown**: Parse headers (`# Notes...`, `# Transcript...`) to identify sections.
    *   **DOCX**: Use `python-docx` to iterate paragraphs, identify headers by text/style, and reconstruct the `Document`.

### 2.4 Formatters
*   Update `docx_formatter.py`, `md_formatter.py`, `rtf_formatter.py`.
*   Handle `SectionType.NOTES_HEADER` (e.g., Bold, Larger font).
*   Handle `SectionType.NOTES_BODY` (e.g., Bullet points if `is_bullet` is True).

### 2.5 CLI & UI
*   **CLI**: Add flags for `--notes-source`, `--mode` (new/update), `--update-file`.
*   **UI**:
    *   "Start" dialog: Create New vs Update Existing.
    *   "Create New" dialog: Select content (Notes, Transcript, Both).
    *   "Update Existing" dialog: Select action (Add/Replace Notes/Transcript).

## 3. Implementation Phases

### Phase 1: Core Domain Model
*   Update `model.py` with new types and fields.
*   Implement `Document.merge_*` logic with unit tests.

### Phase 2: Notes Pipeline (Extract/Transform)
*   Implement `extract/notes.py` (reuse existing file/clipboard patterns).
*   Implement `transform/notes.py` to convert raw Markdown string -> `list[DocumentSection]`.
*   **Key Logic**:
    *   Detect if input has a header. If not, generate `# Notes – YYYY-MM-DD` header.
    *   Convert markdown bullets to `Paragraph(is_bullet=True)`.

### Phase 3: Document Reader (Re-ingestion)
*   Implement `document/reader.py`.
*   Create `read_document(path: Path) -> Document`.
*   Support MD and DOCX parsing.
*   **Crucial**: Must reliably detect "Notes" vs "Transcript" sections based on headers defined in the User Story.

### Phase 4: Formatters
*   Update all formatters to render Notes sections correctly.
*   Ensure visual distinction for Notes Headers.

### Phase 5: CLI & UI Wiring
*   Update `cli.py` to support the new arguments.
*   Update `ui.py` to implement the decision tree defined in the User Story.

### Phase 6: End-to-End Testing
*   Create tests simulating the full workflow:
    *   Ingest Notes -> Create Doc.
    *   Ingest Transcript -> Update Doc (Add Transcript).
    *   Ingest Notes -> Update Doc (Replace Notes).

## 4. Risk Management
*   **DOCX Parsing**: Reading DOCX back into the model can be lossy.
    *   *Mitigation*: Rely on strict header text matching (`# Notes`, `Transcript:`) to identify section boundaries. Treat everything between headers as generic paragraphs if structure is ambiguous.
*   **Clipboard Reliability**:
    *   *Mitigation*: Reuse existing clipboard abstraction.

## 5. Verification
*   All new code must pass `pyright` (strict).
*   Unit tests for Merge logic and Readers are critical.
