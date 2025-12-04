# enhanced-acknowledgment-detection - Spec

- Issue: #18
- Owner: drmoisan
- Last Updated: 2025-12-04

## Overview

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

## Behavior

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

## Inputs / Outputs

- Inputs: existing speakerless pipeline (no new flags); sentences analyzed for dialogue markers/acknowledgments.
- Outputs: unchanged API; improved grouping/speaker changes driven by expanded acknowledgment handling; optional debug logs if enabled.

## API / CLI Surface

- Internal changes only; tests under `tests/transform` and `tests/integration` (acknowledgment-focused cases).

## Data & State

- Uses existing dialogue marker detection; no persistent state changes.

## Constraints & Risks

- **Lightweight heuristics**: Keep detection simple and performant
- **No overfitting**: Avoid optimizing only for SpaceX fixture
- **Backward compatibility**: Must not regress 2-speaker accuracy
- **False positive management**: Exclamation detection should not trigger on non-acknowledgment exclamations when possible
- **Performance**: Context-aware logic must not significantly slow processing

## Definition of Done

- [ ] Behavior matches acceptance criteria (see user story)
- [ ] Tests updated/added
- [ ] Docs updated (README, docs/features/active/... links)
- [ ] Telemetry/logging (if applicable)

## Seeded Test Conditions (from potential)

- [ ] Unit: new acknowledgment words detected; exclamation acknowledgments trigger change; context-aware handling (commas/short utterances vs fillers); boundary cases.
- [ ] Integration: speakerless pipeline groups correctly with new acknowledgments; no regression on existing 2-speaker fixtures; `pytest tests/transform/test_speakerless.py -v -k "acknowledgment"`.
- [ ] Target fixture: 3-speaker SpaceX test (`test_3speaker_spacex_discussion.py`) moves line count toward 18 and improves assignments.
