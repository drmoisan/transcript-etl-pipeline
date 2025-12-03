# Speakerless Detection Integration - Mitigation Plan

**Created**: December 3, 2025  
**Status**: 🔴 **CRITICAL** - Production functionality lost  
**Priority**: P0 - Immediate fix required

---

## Executive Summary

The speakerless detection feature was developed and tested in isolation but **never integrated into the main pipeline**. The entry point that should route speakerless transcripts through `assign_speaker_labels()` before speaker resolution is missing. This means the feature exists and works correctly in unit tests, but is completely bypassed in production usage.

### Impact
- Users providing transcripts without speaker labels will receive errors or poor results
- The NLTK-based speakerless detection (50+ tests, 100% passing) is unused
- Silent failure: No error messages indicate speakerless transcripts aren't supported

---

## Root Cause Analysis

### 1. Where Was the Entry Point Lost?

**Answer**: It was **never created**.

- **Commit b3e10e9** (Nov 21, 2025): Created `enhance.py` with direct call to `resolve_speakers()`
- **Commit c20cf33** (Nov 23, 2025): Added `speakerless.py` with `has_speaker_labels()` and `assign_speaker_labels()`
- **No subsequent commit** integrated speakerless detection into `enhance.py`

The speakerless feature development focused on:
- ✅ Detection algorithms (`has_speaker_labels`, `detect_speaker_changes`)
- ✅ Label assignment (`assign_speaker_labels`)
- ✅ Identity-aware constraints
- ✅ Comprehensive unit and integration tests
- ❌ **Integration into the enhance pipeline**

### 2. Why Features Were Developed Independently

Timeline analysis shows parallel development:

```
Nov 21: enhance.py created (main pipeline)
    ↓
Nov 23: speakerless.py created (parallel feature)
    ↓
Dec 1-2: Identity-aware constraints added (enhancing speakerless)
    ↓
Dec 3: Notes feature merged (different feature, no conflict)
```

The speakerless feature was developed in a branch and never explicitly integrated into `enhance_text()`.

### 3. Expected Behavior (Per Documentation)

From `.github/copilot-instructions.md`:

> **Section 5.2.2 Speaker Handling**
> 
> Rules:
> 1. If a line begins with a Speaker label, detect which person it represents.
> 2. **Determine who "Dan Moisan" is.**
> 3. **Other attendees** - Attempt auto-detection...

The instructions describe what to do **if speakers exist**, but don't explicitly mention:
- Detecting whether speakers exist
- Routing to speakerless pipeline if they don't

This documentation gap contributed to the missing integration.

---

## Why Tests Didn't Catch This

### Test Coverage Analysis

| Test Category | Coverage | Catches Integration Issue? |
|--------------|----------|---------------------------|
| Unit tests for `speakerless.py` | ✅ Extensive (40+ tests) | ❌ No - tests functions directly |
| Integration tests for speakerless | ✅ Good (16+ tests) | ❌ No - tests functions directly |
| End-to-end pipeline tests | ✅ Exists (22 tests) | ❌ No - **all use transcripts with speaker labels** |
| CLI tests | ⚠️ Via integration tests | ❌ No - no speakerless scenarios |

### Critical Gap: No End-to-End Speakerless Tests

**None of the end-to-end tests** (`test_end_to_end_docx.py`, `test_end_to_end_rtf.py`, `test_end_to_end_md.py`) include scenarios where:

1. A speakerless transcript is provided as input
2. The full pipeline is executed: `extract → normalize → enhance → parse → format`
3. The output is validated to contain assigned speaker labels

**Example**: `test_simple_transcript_to_docx()` uses:
```python
"Alice: Hello everyone.\n"
"Bob: Thanks for the meeting.\n"
```

**What should exist but doesn't**:
```python
"Hello everyone.\n"  # No speaker labels
"Thanks for the meeting.\n"  # No speaker labels
```

### Why Integration Tests Passed

The integration tests in `test_speakerless_integration.py` call functions **directly**:

```python
# This works - but bypasses the pipeline
text = fixture_path.read_text()
changes = detect_speaker_changes(text)  # Direct call
result = assign_speaker_labels(text)    # Direct call
```

These tests validate the algorithms work correctly, but don't validate:
- `enhance_text()` routes to speakerless detection
- The CLI handles speakerless transcripts
- End-to-end pipeline produces correct output

---

## Required Changes

### Change 1: Modify `enhance.py` to Route Speakerless Transcripts

**File**: `src/transcript_etl_pipeline/transform/enhance.py`

**Current code**:
```python
def enhance_text(
    normalized_text: str, ui_callback: SpeakerResolutionUI | None = None
) -> tuple[str, dict[str, str]]:
    # Step 1: Resolve speakers first
    text_with_speakers, speaker_map = resolve_speakers(normalized_text, ui_callback)
    
    # Step 2: Detect and format paragraphs
    enhanced_text = detect_paragraphs(text_with_speakers)
    
    return enhanced_text, speaker_map
```

**Required changes**:
```python
from transcript_etl_pipeline.transform.speakerless import (
    has_speaker_labels,
    assign_speaker_labels,
)

def enhance_text(
    normalized_text: str, 
    ui_callback: SpeakerResolutionUI | None = None,
    num_speakers: int | None = None,
) -> tuple[str, dict[str, str]]:
    """Enhance normalized transcript text.
    
    Applies paragraph detection and speaker resolution to create a well-formatted
    transcript with resolved speaker names.
    
    Args:
        normalized_text: Text that has been normalized (CRLF, whitespace, labels)
        ui_callback: Optional UI callback for resolving unknown speakers
        num_speakers: Optional number of speakers for speakerless detection
        
    Returns:
        Tuple of (enhanced text with paragraphs and resolved speakers, speaker mapping)
    """
    # Step 0: Check if transcript has speaker labels
    if not has_speaker_labels(normalized_text):
        logger.info("No speaker labels detected, using speakerless detection")
        # Apply speakerless detection to add generic speaker labels
        text_with_speakers = assign_speaker_labels(normalized_text, num_speakers)
        speaker_map = {}  # No name resolution for generic speakers
    else:
        # Step 1: Resolve speakers (transcript already has labels)
        text_with_speakers, speaker_map = resolve_speakers(normalized_text, ui_callback)
    
    # Step 2: Detect and format paragraphs
    enhanced_text = detect_paragraphs(text_with_speakers)
    
    return enhanced_text, speaker_map
```

**Key points**:
- Add `num_speakers` parameter for user control
- Check `has_speaker_labels()` before processing
- Route to `assign_speaker_labels()` if no speakers detected
- Preserve existing behavior for transcripts with speakers
- Add logging for observability

### Change 2: Update CLI to Support `--num-speakers` Flag

**File**: `src/transcript_etl_pipeline/cli.py`

Add argument:
```python
parser.add_argument(
    "--num-speakers",
    type=int,
    default=None,
    help="Number of speakers for speakerless transcripts (default: auto-detect 2-4)",
)
```

Pass to enhance:
```python
enhanced_text, speaker_map = enhance_text(
    normalized_text, 
    ui_callback=ui_callback,
    num_speakers=args.num_speakers,
)
```

### Change 3: Add End-to-End Tests for Speakerless Pipeline

**File**: `tests/integration/test_end_to_end_speakerless.py` (NEW)

```python
"""End-to-end integration tests for speakerless transcript pipeline."""

import tempfile
from pathlib import Path

import pytest

from transcript_etl_pipeline.document.parser import parse_enhanced_text
from transcript_etl_pipeline.extract.from_file import extract_from_file
from transcript_etl_pipeline.formatters.docx_formatter import format_to_docx
from transcript_etl_pipeline.transform.enhance import enhance_text
from transcript_etl_pipeline.transform.normalize import normalize_text


class TestEndToEndSpeakerless:
    """Test the complete pipeline with speakerless transcripts."""

    def test_simple_speakerless_to_docx(self, tmp_path: Path) -> None:
        """Test converting a speakerless transcript to DOCX."""
        # Create a temporary input file WITHOUT speaker labels
        input_file = tmp_path / "input.txt"
        input_file.write_text(
            "Date: 2025-12-03\n"
            "Attendees: Alice Smith, Bob Johnson\n"
            "\n"
            "Transcript:\n"
            "Hello everyone, thanks for joining.\n"
            "Thank you for having me.\n"
            "Let's get started with the agenda.\n"
        )

        # Extract
        raw_text = extract_from_file(str(input_file))
        assert raw_text is not None

        # Transform: Normalize
        normalized = normalize_text(raw_text)
        assert normalized is not None

        # Transform: Enhance (should detect no speakers and apply speakerless)
        enhanced, speaker_map = enhance_text(normalized)
        assert enhanced is not None
        
        # Verify speaker labels were added
        assert "Speaker A:" in enhanced or "Speaker B:" in enhanced
        
        # Parse
        doc = parse_enhanced_text(enhanced)
        assert len(doc.sections) > 0

        # Load: Format as DOCX
        output_file = tmp_path / "output.docx"
        format_to_docx(doc, str(output_file))

        # Verify output file exists
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_speakerless_with_fixture(self, tmp_path: Path) -> None:
        """Test pipeline with actual speakerless fixture file."""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "sample_transcripts" / "pure_dialogue_no_speakers.txt"
        
        # Extract
        raw_text = extract_from_file(str(fixture_path))
        
        # Transform
        normalized = normalize_text(raw_text)
        enhanced, speaker_map = enhance_text(normalized)
        
        # Verify speakers were assigned
        assert "Speaker A:" in enhanced
        
        # Parse and format
        doc = parse_enhanced_text(enhanced)
        output_file = tmp_path / "output.docx"
        format_to_docx(doc, str(output_file))
        
        assert output_file.exists()
```

**Additional test files to update**:
- `test_end_to_end_rtf.py` - Add speakerless RTF test
- `test_end_to_end_md.py` - Add speakerless Markdown test

### Change 4: Update Documentation

**File**: `.github/copilot-instructions.md`

Add to **Section 5.2 Enhance Requirements**:

```markdown
### **5.2.0 Speakerless Detection (Entry Point)**

**Before** processing speakers, check if the transcript has speaker labels:

```python
if not has_speaker_labels(normalized_text):
    # Apply speakerless detection
    text_with_speakers = assign_speaker_labels(normalized_text, num_speakers)
else:
    # Proceed with speaker resolution
    text_with_speakers, speaker_map = resolve_speakers(...)
```

This ensures transcripts without explicit speaker labels are handled correctly.
```

---

## Testing Strategy

### Test Execution Plan

1. **Unit tests**: Verify `enhance_text` routing logic
   ```bash
   pytest tests/transform/test_enhance.py -v
   ```

2. **Integration tests**: Verify speakerless functions still work
   ```bash
   pytest tests/integration/test_speakerless_integration.py -v
   ```

3. **End-to-end tests**: Verify full pipeline with speakerless input
   ```bash
   pytest tests/integration/test_end_to_end_speakerless.py -v
   ```

4. **Regression tests**: Verify existing tests still pass
   ```bash
   pytest tests/integration/test_end_to_end_*.py -v
   ```

5. **Full suite**: All 510+ tests should pass
   ```bash
   pytest tests/ -v
   ```

### Acceptance Criteria

- ✅ All existing tests pass (510+ tests)
- ✅ New end-to-end speakerless tests pass (3+ tests)
- ✅ CLI accepts `--num-speakers` flag
- ✅ Speakerless transcripts produce valid output (DOCX/RTF/MD)
- ✅ Transcripts with speakers still work correctly (no regression)
- ✅ Black, Ruff, Pyright all pass
- ✅ Documentation updated

---

## Implementation Sequence

### Phase 1: Core Integration (Critical Path)
1. ✅ Analyze and document the issue (this document)
2. Modify `enhance.py` to add speakerless routing
3. Add unit tests for `enhance_text` routing logic
4. Verify existing tests still pass

### Phase 2: CLI Enhancement
1. Add `--num-speakers` argument to CLI
2. Pass parameter through to `enhance_text`
3. Update CLI help text

### Phase 3: End-to-End Testing
1. Create `test_end_to_end_speakerless.py`
2. Add speakerless tests to RTF and MD test files
3. Verify all end-to-end tests pass

### Phase 4: Documentation & Validation
1. Update `.github/copilot-instructions.md`
2. Update `README.md` if needed
3. Run full test suite
4. Run all quality checks (Black, Ruff, Pyright)

---

## Risks & Mitigation

### Risk 1: Breaking Existing Functionality
**Likelihood**: Medium  
**Impact**: High  
**Mitigation**: 
- Comprehensive regression testing
- Preserve existing code path for transcripts with speakers
- Use feature flag if needed during rollout

### Risk 2: Performance Impact
**Likelihood**: Low  
**Impact**: Low  
**Mitigation**:
- `has_speaker_labels()` is fast (regex check)
- Only adds one conditional check to pipeline
- Speakerless detection only runs when needed

### Risk 3: False Negatives in Speaker Detection
**Likelihood**: Medium  
**Impact**: Medium  
**Mitigation**:
- `has_speaker_labels()` is well-tested (8+ unit tests)
- Heuristic requires 2+ labels AND 10% of lines
- Can add `--force-speakerless` flag if needed

---

## Lessons Learned

### What Went Wrong

1. **Integration gap in development process**
   - Feature developed in isolation
   - No explicit integration task in change plan
   - Assumed integration would be obvious

2. **Documentation gap**
   - copilot-instructions.md didn't explicitly require speakerless check
   - No diagram showing full pipeline flow including decision points

3. **Test coverage gap**
   - No end-to-end tests with speakerless input
   - Integration tests called functions directly, bypassing pipeline

### Process Improvements

1. **Change plans must include integration tasks**
   - Explicit task: "Wire feature into pipeline at [location]"
   - Integration test requirements specified upfront

2. **Documentation must show decision points**
   - Add pipeline flow diagram to README
   - Explicitly document routing logic in instructions

3. **End-to-end tests must cover all input variants**
   - Test matrix: with/without speakers, with/without metadata, etc.
   - Add template: `test_e2e_[feature]_[variant].py`

4. **Code review checklist**
   - [ ] Entry point identified and wired
   - [ ] End-to-end tests cover new code paths
   - [ ] Documentation updated with routing logic
   - [ ] CLI arguments added if needed

---

## Next Steps

1. **Immediate (Today)**:
   - Implement Phase 1 (core integration)
   - Run regression tests
   
2. **Short-term (This week)**:
   - Complete Phases 2-4
   - Full test suite validation
   - Update documentation

3. **Follow-up**:
   - Add pipeline flow diagram to README
   - Create integration checklist for future features
   - Review all features for similar integration gaps

---

## Conclusion

The speakerless detection feature is **fully functional** but **not integrated** into the main pipeline. The fix is straightforward:

1. Add `has_speaker_labels()` check in `enhance_text()`
2. Route to `assign_speaker_labels()` when no speakers detected
3. Add end-to-end tests to prevent regression

**Estimated effort**: 2-4 hours  
**Risk level**: Low (well-tested feature, clear integration point)  
**Priority**: P0 (critical functionality missing)

Once integrated, the pipeline will correctly handle both:
- ✅ Transcripts with speaker labels (existing functionality)
- ✅ Transcripts without speaker labels (new functionality)
