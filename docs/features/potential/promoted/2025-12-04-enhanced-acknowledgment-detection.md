# enhanced-acknowledgment-detection (Issue: #18)

- Date captured: 2025-12-04
- Author: Dan Moisan
- Status: Promoted -> docs/features/active/enhanced-acknowledgment-detection/ (Issue #18)
- Priority: 3 (from Speaker Logic Enhancement work plan)
- Completion: 20%
- Issue: #18
- Issue URL: https://github.com/drmoisan/transcript-etl-pipeline/issues/18
- Last Updated: 2025-12-04

## Problem / Why

The speakerless detection algorithm detects basic acknowledgments like "Yes" and "No" but misses common conversational acknowledgments like "Yeah", "Right", "Exactly", "Fair", "True". This causes:

- Mis-grouped speaker turns in multi-speaker transcripts
- Poor speaker change detection at acknowledgment boundaries
- False positives where filler words trigger unwanted speaker changes
- Missed exclamation acknowledgments ("Ha!", "Wow!") that signal turn-taking

**Current State**:

- Acknowledgment detection exists in `speaker_helpers.py` → `detect_dialogue_markers()`
- Current list: "yes", "no", "yeah", "yep", "nope", "okay", "ok", "sure", "right", "absolutely", "great", "perfect", "excellent"
- ✅ Includes: "yeah", "right", "absolutely"
- ❌ Missing: "exactly", "true", "fair", "definitely", "certainly", "agreed", "correct", "indeed"
- ❌ No exclamation acknowledgments
- ❌ No context-aware handling to distinguish fillers from acknowledgments

## Proposed Behavior

1. **Expand acknowledgment lexicon** in `ACKNOWLEDGMENTS` frozenset (`speaker_helpers.py` line 40):

   - Add: "exactly", "true", "fair", "definitely", "certainly", "agreed", "correct", "indeed"
2. **Implement exclamation acknowledgments**:

   - Pattern: "Ha!", "Wow!", "Nice!", "Cool!" indicate speaker change
   - Add to `detect_dialogue_markers()` or create new helper function
   - Should trigger speaker change when appropriate
3. **Add context-aware acknowledgment handling**:

   - "Yeah, I remember it" → "Yeah" is acknowledgment, triggers speaker change
   - "Yeah I think so" → "Yeah" is filler, may NOT trigger change
   - Distinguish based on comma presence and following content
   - Prevents over-triggering on every filler utterance

## Acceptance Criteria (early draft)

- [ ] New acknowledgment words recognized: "exactly", "true", "fair", "definitely", "certainly", "agreed", "correct", "indeed".
- [ ] Exclamation acknowledgments trigger speaker change when appropriate ("Ha!", "Wow!", "Nice!", "Cool!").
- [ ] Context-aware handling reduces false positives for fillers vs acknowledgments.
- [ ] No regressions in existing speakerless tests.
- [ ] 3-speaker SpaceX test improves turn grouping (line count and accuracy trend).

## Constraints & Risks

- **Lightweight heuristics**: Keep detection simple and performant
- **No overfitting**: Avoid optimizing only for SpaceX fixture
- **Backward compatibility**: Must not regress 2-speaker accuracy
- **False positive management**: Exclamation detection should not trigger on non-acknowledgment exclamations when possible
- **Performance**: Context-aware logic must not significantly slow processing

## Test Conditions to Consider

### Unit Tests

- [ ] Each new acknowledgment word properly detected
- [ ] Exclamation acknowledgments ("Ha!", "Wow!", "Nice!", "Cool!") trigger speaker change
- [ ] Context-aware logic: comma presence affects acknowledgment vs filler classification
- [ ] Edge cases: acknowledgments at sentence boundaries, multiple acknowledgments in sequence

### Integration Tests

- [ ] Speakerless pipeline correctly groups turns with new acknowledgments
- [ ] No regression on existing 2-speaker fixtures
- [ ] Test fixture: `pytest tests/transform/test_speakerless.py -v -k "acknowledgment"`

### Target Fixture

- [ ] 3-speaker SpaceX test (`test_3speaker_spacex_discussion.py`)
- [ ] Goal: Move line count from 12 toward 18
- [ ] Goal: Improve speaker assignment accuracy

## Next Step

- [ ] Promote to GitHub issue (feature request template)
- [ ] Create `docs/features/active/enhanced-acknowledgment-detection/` folder from the template
