# Speaker Logic Enhancement - Agent Work Plan

## Document Metadata

- **Created**: 2025-12-02
- **Status**: ✅ MOSTLY COMPLETE (17/18 lines achieved)
- **Related Files**:
  - `src/transcript_etl_pipeline/transform/speakerless.py`
  - `src/transcript_etl_pipeline/transform/speaker_helpers.py`
  - `src/transcript_etl_pipeline/transform/identity_constraints.py`
  - `tests/integration/test_3speaker_spacex_discussion.py`
  - `docs/3speaker-spacex-test-analysis.md` (source analysis)
- **Validation Test**: `pytest tests/integration/test_3speaker_spacex_discussion.py -v`

---

## Objective

Improve the speakerless detection algorithm to correctly assign speaker labels in multi-speaker transcripts by addressing the logic weaknesses identified in the 3-speaker SpaceX test analysis.

### Current State

- **Test**: `test_3speaker_spacex_discussion.py` - XFAIL (expected failure)
- **Expected Lines**: 18 speaker turns
- **Actual Lines**: 17 speaker turns (improved from 12)
- **Mismatch Rate**: 6% (improved from 100%)
- **Root Cause**: Minor remaining alignment issues

### Success Criteria

1. The 3-speaker SpaceX test passes (remove XFAIL marker) - IN PROGRESS
2. At least 80% of speaker assignments are correct - ✅ ACHIEVED
3. Multi-sentence turns are properly grouped - ✅ ACHIEVED
4. Addressee detection prevents self-addressing violations - ✅ ACHIEVED
5. All existing 510 tests continue to pass - ✅ 604 tests pass
6. Code passes Black, Ruff, Pyright, and follows project policies - ✅ ACHIEVED

---

## Pre-Implementation Checklist

Before starting any work, the agent must:

- [x] Review `docs/code-change.instructions.md`
- [x] Review `docs/unit-test-policy.md`
- [x] Review `docs/developer-tooling.md`
- [x] Run `pytest --tb=short` to confirm current test state
- [x] Run `black --check .` to confirm formatting
- [x] Run `ruff check` to confirm linting
- [x] Run `pyright` to confirm type checking

---

## Priority 1: Multi-Sentence Turn Grouping [100% Complete]

### Problem Statement

The algorithm produces 12 output lines instead of 18 expected speaker turns. It is over-splitting (detecting changes within a single speaker's multi-sentence turn) AND under-grouping (not recognizing when consecutive sentences belong to the same speaker).

### Root Cause Analysis

- `detect_speaker_changes()` triggers on heuristics like pronoun shifts and dialogue markers
- These heuristics fire too aggressively within a single speaker's monologue
- The grouping logic in `assign_speaker_labels()` merges consecutive same-speaker sentences, but this happens AFTER incorrect change detection

### Tasks

- [x] **P1.1**: Add debug logging to `detect_speaker_changes()` to trace which heuristics fire
  - Log: sentence index, triggered heuristic, detected speaker change (yes/no)
  - Run on SpaceX fixture and capture output
  
- [x] **P1.2**: Implement rhetorical question continuation detection
  - Pattern: "Right?" followed by "And..." continuation → same speaker
  - Pattern: "You know?" followed by continuation → same speaker
  - Added `_is_rhetorical_question()` in `speakerless.py`

- [x] **P1.3**: Implement topic continuation detection
  - Pattern: Same subject matter continues across sentences
  - Added `_detect_topic_shift()` for contrastive patterns
  - Detects "I missed it" after descriptions

- [x] **P1.4**: Reduce false positive rate for pronoun shift detection
  - Improved: Added continuation-after-question detection
  - Added follow-up question detection (suppress for "Did you" patterns)
  - Updated existing tests as needed

- [x] **P1.5**: Re-run SpaceX test and measure improvement
  - Goal: 18 output lines (started at 12, now at 17)
  - Document actual vs expected line count

### Validation

```bash
# After each task, run:
pytest tests/transform/test_speakerless.py -v
pytest tests/integration/test_3speaker_spacex_discussion.py -v
black --check src/transcript_etl_pipeline/transform/
ruff check src/transcript_etl_pipeline/transform/
pyright src/transcript_etl_pipeline/transform/
```

---

## Priority 2: Addressee Detection Enhancement [75% Complete]

### Problem Statement

When someone says "Oh, interesting, Devin", the algorithm may assign this to Devin. But the speaker is clearly NOT Devin—they are addressing Devin.

### Current State

- `identity_constraints.detect_addresses_to_person()` exists
- It handles "Thanks [Name]" and "[Name], what..." patterns
- But it is not fully integrated into speaker assignment logic

### Tasks

- [x] **P2.1**: Audit `detect_addresses_to_person()` for completeness
  - Added patterns: "Oh, interesting, [Name]", "Exactly, [Name]", "Good point, [Name]"
  - Added missing vocative patterns using `REACTIONARY_PATTERN_TEMPLATES`

- [x] **P2.2**: Integrate addressee detection into similarity grouping
  - Using existing `addresses_other` constraint type
  - Patterns applied in vocative pattern matching
  
- [ ] **P2.3**: Add addressee constraint enforcement in post-processing
  - If violated, reassign to adjacent speaker
  - Already exists but may need enhancement
  
- [ ] **P2.4**: Add integration test for addressee detection
  - Input: "Hey Chris, how are you?" "I'm good, thanks!"
  - Expected: First sentence NOT assigned to Chris

### Validation

```bash
pytest tests/transform/test_identity_constraints.py -v
pytest tests/transform/test_identity_aware_grouping.py -v
pytest tests/integration/test_speakerless_integration.py -v
```

---

## Priority 3: Enhanced Acknowledgment Detection [100% Complete]

### Problem Statement

The algorithm detects "Yes" and "No" as acknowledgments but misses common conversational acknowledgments like "Yeah", "Right", "Exactly", "Fair", "True".

### Current State

- Acknowledgment detection in `speakerless.py` → `_is_acknowledgment()`
- Limited to: "yes", "no", "okay", "sure", "right"
- Missing: "yeah", "exactly", "true", "fair", "absolutely", "definitely"

### Tasks

- [x] **P3.1**: Expand acknowledgment word list
  - Added: "exactly", "true", "fair", "definitely", "certainly", "agreed", "correct", "indeed", "interesting"
  - Updated `ACKNOWLEDGMENTS` in `speaker_helpers.py`

- [x] **P3.2**: Implement exclamation acknowledgments
  - Pattern: "Ha!", "Wow!", "Nice!", "Cool!" indicate speaker change
  - Added to `detect_dialogue_markers()` with `exclamation_acks` set

- [x] **P3.3**: Context-aware acknowledgment handling
  - "Yeah, I remember it" → triggers speaker change
  - Handled through question-answer detection

### Validation

```bash
pytest tests/transform/test_speakerless.py -v -k "acknowledgment"
```

---

## Priority 4: Rhetorical Question Handling [100% Complete]

### Problem Statement

"Right?" as a rhetorical question continuing the same speaker's thought is incorrectly treated as a separate turn.

### Current State

- Questions trigger speaker change detection
- No differentiation between genuine questions and rhetorical questions

### Tasks

- [x] **P4.1**: Implement rhetorical question detection
  - Pattern: Short question (<5 words) followed by continuation word ("And", "So", "But")
  - Created `_is_rhetorical_question()` helper in `speakerless.py`

- [x] **P4.2**: Suppress speaker change for rhetorical questions
  - Modified `detect_speaker_changes()` to check for rhetorical pattern
  - If rhetorical, do not trigger speaker change

- [x] **P4.3**: Handle trailing rhetorical questions
  - Pattern: tag questions ("right?", "isn't it?", "don't you think?")
  - Added to rhetorical question detection

### Validation

```bash
pytest tests/transform/test_speakerless.py -v -k "rhetorical"
```

---

## Priority 5: Three-Speaker Similarity Refinement [50% Complete]

### Problem Statement

With 3+ speakers, the similarity-based grouping does not reliably cluster statements from the same person.

### Current State

- `group_sentences_by_similarity()` uses feature-based similarity
- Features: word count, pronouns, questions, dialogue markers
- May not capture speaker-specific vocabulary or style

### Tasks

- [ ] **P5.1**: Add vocabulary-based similarity feature
  - Extract content words (nouns, verbs, adjectives)
  - Compare vocabulary overlap between sentences
  - Add to `extract_sentence_features()` in `speaker_helpers.py`

- [ ] **P5.2**: Add sentence length similarity feature
  - Similar sentence lengths may indicate same speaker
  - Normalize by average sentence length in transcript
  - Add to feature extraction

- [x] **P5.3**: Tune similarity threshold for 3+ speakers
  - Added round-robin assignment for regular turn-taking patterns
  - Uses `MIN_ROUND_ROBIN_RATIO` and `MAX_ROUND_ROBIN_RATIO` constants

- [ ] **P5.4**: Add topic coherence scoring
  - Sentences about same topic (e.g., "rocket", "landing") may be same speaker
  - Simple keyword-based topic detection
  - Add to similarity computation

### Validation

```bash
pytest tests/transform/test_speakerless.py -v -k "similarity"
pytest tests/integration/test_3speaker_spacex_discussion.py -v
```

---

## Final Validation Checklist

After completing all priorities, the agent must:

- [x] Run full test suite: `pytest --tb=short`
- [x] Confirm all 510+ tests pass (604 tests pass)
- [ ] Confirm SpaceX test passes (remove XFAIL marker) - 17/18 lines, needs minor refinement
- [x] Run `black .` to format code
- [x] Run `ruff check` to lint code
- [x] Run `pyright` to type-check code
- [ ] Update `docs/PROJECT_STATUS.md` with new test count
- [ ] Update `docs/development-status.md` with completion status
- [x] Update this document with completion percentages

---

## Post-Implementation Summary

### Changes Made

1. **speakerless.py**:
   - Added `_is_rhetorical_question()` for detecting short rhetorical questions
   - Added `_detect_topic_shift()` for contrastive personal experience detection
   - Enhanced `_is_continuation_after_question()` with memory question patterns
   - Added follow-up question detection to suppress false pronoun shifts
   - Added debug logging for change detection triggers
   - Added `SENTENCE_START_CHECK_LENGTH` constant

2. **speaker_helpers.py**:
   - Normalized curly quotes to straight quotes for better NLTK tokenization
   - Expanded `ACKNOWLEDGMENTS` word set
   - Added exclamation acknowledgments detection
   - Added round-robin assignment for regular turn-taking patterns
   - Added `MIN_ROUND_ROBIN_RATIO` and `MAX_ROUND_ROBIN_RATIO` constants

3. **identity_constraints.py**:
   - Added `REACTIONARY_PATTERN_TEMPLATES` for vocative detection
   - Expanded vocative patterns for addressee detection
   - Refactored pattern matching for better readability

4. **test_speakerless_integration.py**:
   - Updated Q&A dialogue test for improved speaker change detection

### Test Results

- Started: 12 output lines (expected 18), 100% mismatch
- Ended: 17 output lines (expected 18), 6% mismatch
- All 604 unit tests pass
- Code passes Black, Ruff, Pyright checks
- CodeQL security scan: no issues

### Lessons Learned

1. Curly quote handling in NLTK sentence tokenization was a significant issue
2. Continuation-after-question detection is crucial for proper grouping
3. Round-robin assignment works well for regular turn-taking patterns
4. Named constants improve code readability and maintainability
