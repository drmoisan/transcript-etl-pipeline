# Speaker Logic Enhancement - Agent Work Plan

## Document Metadata

- **Created**: 2025-12-02
- **Last Updated**: 2025-12-03
- **Status**: 🔴 NOT STARTED
- **Related Files**:
  - `src/transcript_etl_pipeline/transform/speakerless.py`
  - `src/transcript_etl_pipeline/transform/speaker_helpers.py`
  - `src/transcript_etl_pipeline/transform/identity_constraints.py`
  - `tests/integration/test_3speaker_spacex_discussion.py`
  - `docs/3speaker-spacex-test-analysis.md` (source analysis)
- **Validation Test**: `pytest tests/integration/test_3speaker_spacex_discussion.py -v`

---

## Status Summary (as of 2025-12-03)

### Current Implementation Status

✅ **Infrastructure Complete**:
- `detect_speaker_changes()` implemented with pronoun shift, question-answer, dialogue marker detection
- `assign_speaker_labels()` implemented with sentence-based segmentation
- `group_sentences_by_similarity()` implemented with feature-based clustering
- `detect_addresses_to_person()` implemented for vocative patterns
- Basic acknowledgment detection: "yes", "no", "yeah", "okay", "sure", "right", "absolutely"
- Identity constraint system operational

🔴 **Algorithmic Improvements Needed** (Per Analysis):
- Multi-sentence turn grouping: Algorithm produces 12 lines instead of 18 expected
- Rhetorical question handling: Not implemented
- Enhanced acknowledgments: Missing "exactly", "true", "fair", "definitely", etc.
- Topic continuation detection: Not implemented
- Vocabulary-based similarity: Not implemented

### Test Status

- **3-Speaker SpaceX Test**: ❌ XFAIL (expected failure)
- **Expected**: 18 speaker turns correctly assigned
- **Actual**: 12 output lines with 100% speaker mismatch rate
- **Root Cause**: Over-splitting within speaker turns + under-grouping of consecutive same-speaker sentences

---

## Objective

Improve the speakerless detection algorithm to correctly assign speaker labels in multi-speaker transcripts by addressing the logic weaknesses identified in the 3-speaker SpaceX test analysis.

### Current State

- **Test**: `test_3speaker_spacex_discussion.py` - XFAIL (expected failure)
- **Expected Lines**: 18 speaker turns
- **Actual Lines**: 12 speaker turns
- **Mismatch Rate**: 100%
- **Root Cause**: Algorithm over-splits and under-detects speaker changes

### Success Criteria

1. The 3-speaker SpaceX test passes (remove XFAIL marker)
2. At least 80% of speaker assignments are correct
3. Multi-sentence turns are properly grouped
4. Addressee detection prevents self-addressing violations
5. All existing 510 tests continue to pass
6. Code passes Black, Ruff, Pyright, and follows project policies

---

## Pre-Implementation Checklist

✅ Infrastructure review complete (2025-12-03):

- [x] Review `docs/code-change.instructions.md`
- [x] Review `docs/unit-test-policy.md`
- [x] Review `docs/developer-tooling.md`
- [x] Run `pytest --tb=short` to confirm current test state
  - Result: 617 passed, 1 xfailed (test_3speaker_spacex_discussion)
- [x] Run `black --check .` to confirm formatting
  - Result: All files properly formatted
- [x] Run `ruff check` to confirm linting
  - Result: All checks passed
- [x] Run `pyright` to confirm type checking
  - Result: 0 errors

**Ready for implementation**: All prerequisites met.

---

## Priority 1: Multi-Sentence Turn Grouping [0% Complete]

### Problem Statement

The algorithm produces 12 output lines instead of 18 expected speaker turns. It is over-splitting (detecting changes within a single speaker's multi-sentence turn) AND under-grouping (not recognizing when consecutive sentences belong to the same speaker).

### Root Cause Analysis

- `detect_speaker_changes()` triggers on heuristics like pronoun shifts and dialogue markers
- These heuristics fire too aggressively within a single speaker's monologue
- The grouping logic in `assign_speaker_labels()` merges consecutive same-speaker sentences, but this happens AFTER incorrect change detection

### Tasks

- [ ] **P1.1**: Add debug logging to `detect_speaker_changes()` to trace which heuristics fire
  - Log: sentence index, triggered heuristic, detected speaker change (yes/no)
  - Run on SpaceX fixture and capture output
  
- [ ] **P1.2**: Implement rhetorical question continuation detection
  - Pattern: "Right?" followed by "And..." continuation → same speaker
  - Pattern: "You know?" followed by continuation → same speaker
  - Add to `detect_speaker_changes()` in `speakerless.py`
  - Add 3+ unit tests for rhetorical continuations

- [ ] **P1.3**: Implement topic continuation detection
  - Pattern: Same subject matter continues across sentences
  - Use simple keyword overlap heuristic
  - If >40% keyword overlap with previous sentence, suppress speaker change
  - Add to `speaker_helpers.py`
  - Add 3+ unit tests

- [ ] **P1.4**: Reduce false positive rate for pronoun shift detection
  - Current: Any I→you or you→I shift triggers change
  - Improved: Require shift at sentence boundary AND dialogue marker
  - Update `_detect_pronoun_shift()` in `speakerless.py`
  - Update existing tests as needed

- [ ] **P1.5**: Re-run SpaceX test and measure improvement
  - Goal: 18 output lines (currently 12)
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

## Priority 2: Addressee Detection Enhancement [80% Complete]

### Problem Statement

When someone says "Oh, interesting, Devin", the algorithm may assign this to Devin. But the speaker is clearly NOT Devin—they are addressing Devin.

### Current State

✅ **Mostly Implemented**:
- `identity_constraints.detect_addresses_to_person()` exists and is operational (line 89)
- Handles "Thanks [Name]" and "[Name], what..." patterns
- Integrated into identity constraint system
- ✅ Self-identification filtering prevents "I'm [Name]" from being treated as addressee
- ✅ Constraints enforce speaker ≠ addressed person

❌ **Missing Patterns**:
- "Oh, interesting, [Name]"
- "Exactly, [Name]"
- "Good point, [Name]"
- Mid-sentence vocatives: "What do you think, [Name], about..."

### Tasks

- [ ] **P2.1**: Audit `detect_addresses_to_person()` for completeness
  - ✅ Current patterns working: "[Name], what...", "Thanks [Name]", vocatives with commas
  - ❌ Missing patterns: "Oh, interesting, [Name]", "Exactly, [Name]", "Good point, [Name]"
  - ❌ Missing: Mid-sentence vocatives "What do you think, [Name], about..."
  - Location: `identity_constraints.py` line 89
  - Add 3+ unit tests for new patterns

- [ ] **P2.2**: Integrate addressee detection into similarity grouping
  - ✅ Already integrated: `detect_addresses_to_person()` called in constraint system
  - ✅ Constraint type `addresses_other` exists
  - ⚠️ Verify: Check if `group_sentences_by_similarity()` uses these constraints
  - Review: `speaker_helpers.py` line 470
  
- [ ] **P2.3**: Add addressee constraint enforcement in post-processing
  - ✅ `resolve_addresses_other_violations()` exists in `speaker_helpers.py`
  - ⚠️ Verify: Confirm it's called in speaker assignment pipeline
  - If violated, reassign to adjacent speaker
  
- [ ] **P2.4**: Add integration test for addressee detection
  - Input: "Hey Chris, how are you?" "I'm good, thanks!"
  - Expected: First sentence NOT assigned to Chris
  - Location: `tests/integration/test_speakerless_integration.py`

### Validation

```bash
pytest tests/transform/test_identity_constraints.py -v
pytest tests/transform/test_identity_aware_grouping.py -v
pytest tests/integration/test_speakerless_integration.py -v
```

---

## Priority 3: Enhanced Acknowledgment Detection [20% Complete]

### Problem Statement

The algorithm detects "Yes" and "No" as acknowledgments but misses common conversational acknowledgments like "Yeah", "Right", "Exactly", "Fair", "True".

### Current State

✅ **Partially Implemented**:
- Acknowledgment detection in `speaker_helpers.py` → `detect_dialogue_markers()`
- Current list: "yes", "no", "yeah", "yep", "nope", "okay", "ok", "sure", "right", "absolutely", "great", "perfect", "excellent"
- ✅ Includes: "yeah", "right", "absolutely" (from Priority list)
- ❌ Missing: "exactly", "true", "fair", "definitely", "certainly", "agreed", "correct", "indeed"

### Tasks

- [ ] **P3.1**: Expand acknowledgment word list
  - ✅ Already have: "yeah", "right", "absolutely"
  - ❌ Add: "exactly", "true", "fair", "definitely", "certainly", "agreed", "correct", "indeed"
  - Location: `ACKNOWLEDGMENTS` frozenset in `speaker_helpers.py` (line 40)
  - Add unit tests for each new acknowledgment

- [ ] **P3.2**: Implement exclamation acknowledgments
  - Pattern: "Ha!", "Wow!", "Nice!", "Cool!" indicate speaker change
  - Add to `detect_dialogue_markers()` or create new helper
  - Add 3+ unit tests

- [ ] **P3.3**: Context-aware acknowledgment handling
  - "Yeah, I remember it" → "Yeah" is acknowledgment, triggers speaker change
  - "Yeah I think so" → "Yeah" is filler, may NOT trigger change
  - Distinguish based on comma presence and following content
  - Add 3+ unit tests

### Validation

```bash
pytest tests/transform/test_speakerless.py -v -k "acknowledgment"
```

---

## Priority 4: Rhetorical Question Handling [0% Complete]

### Problem Statement

"Right?" as a rhetorical question continuing the same speaker's thought is incorrectly treated as a separate turn.

### Current State

- Questions trigger speaker change detection
- No differentiation between genuine questions and rhetorical questions

### Tasks

- [ ] **P4.1**: Implement rhetorical question detection
  - Pattern: Short question (<5 words) followed by continuation word ("And", "So", "But")
  - Pattern: Question at end of paragraph/turn continuing prior content
  - Create `_is_rhetorical_question()` helper in `speakerless.py`
  - Add 5+ unit tests

- [ ] **P4.2**: Suppress speaker change for rhetorical questions
  - Modify `detect_speaker_changes()` to check for rhetorical pattern
  - If rhetorical, do not trigger speaker change
  - Add integration tests

- [ ] **P4.3**: Handle trailing rhetorical questions
  - "The rocket landed perfectly, didn't it?" → no speaker change
  - Pattern: tag questions ("right?", "isn't it?", "don't you think?")
  - Add to rhetorical question detection

### Validation

```bash
pytest tests/transform/test_speakerless.py -v -k "rhetorical"
```

---

## Priority 5: Three-Speaker Similarity Refinement [40% Complete]

### Problem Statement

With 3+ speakers, the similarity-based grouping does not reliably cluster statements from the same person.

### Current State

✅ **Basic Implementation Complete**:
- `group_sentences_by_similarity()` implemented in `speaker_helpers.py` (line 470)
- `extract_sentence_features()` implemented (line 312)
- Current features:
  - ✅ Word count
  - ✅ Character count  
  - ✅ First-person pronoun count
  - ✅ Second-person pronoun count
  - ✅ Is question
  - ✅ Is exclamation
  - ✅ Has greeting
  - ✅ Has acknowledgment
  - ✅ Average word length

❌ **Missing Features**:
- Vocabulary-based similarity (content word overlap)
- Sentence length similarity scoring
- Topic coherence scoring (keyword clustering)
- Tuned threshold for 3+ speakers

### Tasks

- [ ] **P5.1**: Add vocabulary-based similarity feature
  - Extract content words (nouns, verbs, adjectives) using NLTK POS tagging
  - Compare vocabulary overlap between sentences
  - Add to `extract_sentence_features()` in `speaker_helpers.py` (line 312)
  - Requires: NLTK POS tagger (already available in codebase)

- [ ] **P5.2**: Add sentence length similarity feature
  - Similar sentence lengths may indicate same speaker
  - Normalize by average sentence length in transcript
  - Add to feature extraction
  - Weight this feature appropriately in similarity computation

- [ ] **P5.3**: Tune similarity threshold for 3+ speakers
  - Current threshold may be too high/low for 3-speaker scenarios
  - Test with SpaceX fixture
  - Document optimal threshold value
  - Consider dynamic threshold based on num_speakers parameter

- [ ] **P5.4**: Add topic coherence scoring
  - Sentences about same topic (e.g., "rocket", "landing") may be same speaker
  - Simple keyword-based topic detection
  - Add to similarity computation
  - Weight topic coherence in final similarity score

### Validation

```bash
pytest tests/transform/test_speakerless.py -v -k "similarity"
pytest tests/integration/test_3speaker_spacex_discussion.py -v
```

---

## Final Validation Checklist

After completing all priorities, the agent must:

- [ ] Run full test suite: `pytest --tb=short`
- [ ] Confirm all 510+ tests pass
- [ ] Confirm SpaceX test passes (remove XFAIL marker)
- [ ] Run `black .` to format code
- [ ] Run `ruff check` to lint code
- [ ] Run `pyright` to type-check code
- [ ] Update `docs/PROJECT_STATUS.md` with new test count
- [ ] Update `docs/development-status.md` with completion status
- [ ] Update this document with completion percentages

---

## Implementation Priority Summary (2025-12-03)

Based on review of current codebase and test analysis:

### Recommended Implementation Order

1. **Priority 1 (Multi-Sentence Turn Grouping)** - 0% Complete
   - **Impact**: HIGH - Directly addresses 12 vs 18 line mismatch
   - **Effort**: MEDIUM - Requires careful heuristic tuning
   - **Status**: Not started - No debug logging, no rhetorical/topic detection

2. **Priority 4 (Rhetorical Question Handling)** - 0% Complete  
   - **Impact**: HIGH - Will reduce false speaker changes
   - **Effort**: LOW - New helper function + integration
   - **Status**: Not started - No rhetorical question detection exists

3. **Priority 3 (Enhanced Acknowledgment Detection)** - 20% Complete
   - **Impact**: MEDIUM - Improves turn-taking detection
   - **Effort**: LOW - Just adding words to existing list
   - **Status**: Partially complete - Missing "exactly", "true", "fair", etc.

4. **Priority 5 (Three-Speaker Similarity Refinement)** - 40% Complete
   - **Impact**: HIGH - Critical for 3+ speaker scenarios
   - **Effort**: HIGH - Feature engineering + threshold tuning
   - **Status**: Basic features done, advanced features missing

5. **Priority 2 (Addressee Detection Enhancement)** - 80% Complete
   - **Impact**: MEDIUM - Handles edge cases
   - **Effort**: LOW - Add missing patterns to existing function
   - **Status**: Infrastructure complete, needs pattern expansion

### Quick Win Tasks (Start Here)

These can be completed quickly and will provide immediate test improvements:

1. **P3.1**: Add missing acknowledgments ("exactly", "true", "fair") - 15 min
2. **P2.1**: Add missing addressee patterns - 30 min  
3. **P1.1**: Add debug logging to trace heuristics - 30 min
4. **P4.1**: Implement rhetorical question detection - 1 hour

### Critical Path to Pass SpaceX Test

To achieve 18 output lines and >80% accuracy:

1. Implement P1.2 (rhetorical continuations) + P1.3 (topic continuations)
2. Implement P4.1 (rhetorical question detection)
3. Implement P5.1 (vocabulary similarity) + P5.3 (threshold tuning)
4. Re-test and iterate on P1.4 (reduce pronoun shift false positives)

---

## Post-Implementation Summary

### Changes Made

(To be filled by agent after implementation)

### Test Results

(To be filled by agent after implementation)

### Lessons Learned

(To be filled by agent after implementation)

---

## Loading Prompt for Next Agent

```
You are continuing work on the transcript-etl-pipeline repository.

**Current Branch**: copilot/add-speaker-detection-tool

**Task**: Implement speaker logic enhancements as documented in docs/speaker_logic_enhancement.agent.md

**Context**:
- The speakerless speaker detection algorithm has logic weaknesses identified in a 3-speaker stress test
- The test (test_3speaker_spacex_discussion.py) is currently marked XFAIL and produces 12 lines instead of 18
- Root causes: over-aggressive change detection, missing acknowledgments, no rhetorical question handling

**Your Objectives**:
1. Review docs/speaker_logic_enhancement.agent.md for the full work plan
2. Review docs/code-change.instructions.md for coding standards
3. Implement priorities in order (P1 → P2 → P3 → P4 → P5)
4. Update checkboxes in the work plan as you complete each task
5. Run validation commands after each task
6. Remove XFAIL from the SpaceX test once it passes

**Key Files**:
- src/transcript_etl_pipeline/transform/speakerless.py
- src/transcript_etl_pipeline/transform/speaker_helpers.py
- tests/integration/test_3speaker_spacex_discussion.py

**Start by**:
1. Running `pytest --tb=short` to confirm current test state
2. Reviewing Priority 1 tasks in the work plan
3. Implementing P1.1 (add debug logging) first

Good luck!
```
