# Implementation Plan: Unified Notes + Transcript Feature

## 1. Objective
Enable the ETL pipeline to ingest, process, and merge both **Transcripts** and **Markdown Notes** into a single consolidated document. Support creating new documents or updating existing ones (DOCX/MD) by adding or replacing sections.

## 2. Architecture Changes

### 2.1 Data Model (`src/transcript_etl_pipeline/document/model.py`) ✅ COMPLETE
*   **`SectionType` Enum**: Add `NOTES_HEADER` and `NOTES_BODY`. ✅
*   **`Paragraph` Dataclass**: Add `is_bullet: bool` field to support bulleted notes. ✅
*   **`Document` Class**: ✅
    *   Add methods for content management:
        *   `merge_notes(sections: list[DocumentSection], mode: MergeMode)` ✅
        *   `merge_transcript(sections: list[DocumentSection], mode: MergeMode)` ✅
    *   Ensure strict ordering: Metadata -> Notes -> Transcript. ✅

### 2.2 Extraction & Transformation ✅ COMPLETE
*   **Extract**: New logic to read Notes from Clipboard or File. ✅ (reuses existing extractors)
*   **Transform**: ✅
    *   New `transform/notes.py` module. ✅
    *   Parse Markdown notes into `DocumentSection` objects. ✅
    *   Handle "Notes Differentiation" (auto-generating headers with timestamps). ✅

### 2.3 Document Re-ingestion (Reader) ✅ COMPLETE
*   New `src/transcript_etl_pipeline/document/reader.py` module. ✅
*   **Purpose**: Parse *existing* output files (DOCX, MD) back into the `Document` model to support the "Add to Existing" workflow. ✅
*   **Strategies**:
    *   **Markdown**: Parse headers (`# Notes...`, `# Transcript...`) to identify sections. ✅
    *   **DOCX**: Use `python-docx` to iterate paragraphs, identify headers by text/style, and reconstruct the `Document`. ✅

### 2.4 Formatters ✅ COMPLETE
*   Update `docx_formatter.py`, `md_formatter.py`, `rtf_formatter.py`. ✅
*   Handle `SectionType.NOTES_HEADER` (e.g., Bold, Larger font). ✅
*   Handle `SectionType.NOTES_BODY` (e.g., Bullet points if `is_bullet` is True). ✅

### 2.5 CLI & UI ✅ COMPLETE
*   **CLI**: Add flags for `--notes-source`, `--mode` (new/update), `--update-file`. ✅
*   CLI orchestration via `run_unified_pipeline()`. ✅
*   **UI**:
    *   Basic prompts integrated with CLI for missing arguments. ✅
    *   Note: Full UI decision tree dialogs are a future enhancement.

## 3. Implementation Phases

### Phase 1: Core Domain Model ✅ COMPLETE
*   Update `model.py` with new types and fields. ✅
*   Implement `Document.merge_*` logic with unit tests. ✅ (20 tests)

### Phase 2: Notes Pipeline (Extract/Transform) ✅ COMPLETE
*   Reuse existing file/clipboard patterns for extraction. ✅
*   Implement `transform/notes.py` to convert raw Markdown string -> `list[DocumentSection]`. ✅
*   **Key Logic**: ✅
    *   Detect if input has a header. If not, generate `# Notes – YYYY-MM-DD` header. ✅
    *   Convert markdown bullets to `Paragraph(is_bullet=True)`. ✅
*   Unit tests. ✅ (23 tests)

### Phase 3: Document Reader (Re-ingestion) ✅ COMPLETE
*   Implement `document/reader.py`. ✅
*   Create `read_document(path: Path) -> Document`. ✅
*   Support MD and DOCX parsing. ✅
*   Unit tests. ✅ (30 tests)

### Phase 4: Formatters ✅ COMPLETE
*   Update all formatters to render Notes sections correctly. ✅
*   Ensure visual distinction for Notes Headers. ✅
*   Unit tests. ✅ (10 tests)

### Phase 5: CLI & UI Wiring ✅ COMPLETE
*   Update `cli.py` to support the new arguments. ✅
*   Implement `run_unified_pipeline()` for notes + transcript workflows. ✅

### Phase 6: End-to-End Testing ✅ COMPLETE
*   Create tests simulating the full workflow: ✅ (11 tests)
    *   Ingest Notes -> Create Doc. ✅
    *   Ingest Transcript -> Update Doc (Add Transcript). ✅
    *   Ingest Notes -> Update Doc (Replace Notes). ✅

## 4. Risk Management
*   **DOCX Parsing**: Reading DOCX back into the model can be lossy.
    *   *Mitigation*: Rely on strict header text matching (`# Notes`, `Transcript:`) to identify section boundaries. Treat everything between headers as generic paragraphs if structure is ambiguous.
*   **Clipboard Reliability**:
    *   *Mitigation*: Reuse existing clipboard abstraction.

## 5. Verification ✅ COMPLETE
*   All new code must pass `pyright` (strict). ✅
*   Unit tests for Merge logic and Readers are critical. ✅

## 6. Summary
**Total new tests added: 94**
- Model merge tests: 20
- Notes transformation tests: 23
- Document reader tests: 30
- Formatter tests: 10
- End-to-end tests: 11

**All 500 tests pass with pyright, black, and ruff checks passing.**
