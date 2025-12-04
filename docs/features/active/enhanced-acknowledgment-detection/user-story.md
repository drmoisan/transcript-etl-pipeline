# enhanced-acknowledgment-detection - User Story

- Issue: #18
- Owner: drmoisan
- Status: Draft
- Last Updated: 2025-12-04

## Story Statement
 
- As a user, I often transcribe adhoc conversations. Adhoc transcriptions lack proper speaker transitions or labels. I want to be able to supply raw text, detect the transitions, and apply a label. The feature should be able to detect common acknowledgments and exclamations to trigger transitions. It should also leverage light context awareness so fillers (e.g., “yeah I think…”) don’t cause false speaker changes.

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

## Personas & Scenarios

- **Persona: Meeting Transcriber (Professional Context)**
  - **Who they are**: A professional who regularly transcribes multi-person meetings, interviews, or podcast discussions from audio recordings or live notes
  - **What they care about**: Accurate speaker attribution and natural conversation flow in the final document; minimal manual editing required
  - **Their constraints**: Limited time to manually identify and fix speaker transitions; raw transcripts often lack clear speaker labels or have formatting inconsistencies
  - **Their goals**: Produce clean, well-formatted transcripts with correct speaker assignments quickly and reliably
  - **Their frustrations**: Current tools miss conversational cues like acknowledgments ("Exactly!", "Fair point"), causing speaker turns to be incorrectly grouped or split; must manually fix false transitions where fillers like "yeah I think..." incorrectly trigger speaker changes
  - **Their context**: Works with 3+ speaker conversations regularly; needs the tool to understand natural conversation patterns including acknowledgments and exclamations that signal turn-taking

- **Scenario: Transcribing a Three-Person Strategy Meeting**
  - **Who is acting?** Sarah, a project coordinator transcribing a strategy meeting between three team leaders
  - **What triggered the action?** Sarah received a raw transcript from the meeting recording service but it lacks speaker labels and proper turn segmentation
  - **What steps do they take?**
    1. Sarah pastes the raw transcript into the ETL pipeline tool
    2. She selects speakerless detection mode with 3 speakers
    3. The tool analyzes the text and detects speaker changes based on conversational patterns
    4. The tool identifies acknowledgments ("Exactly!", "Fair point", "True") as turn-taking signals
    5. The tool distinguishes between acknowledgments and fillers (doesn't split on "yeah I think that's right")
    6. Sarah reviews the output with properly labeled speaker turns
  - **What obstacles or decisions occur?** 
    - The conversation includes frequent acknowledgments and exclamations that weren't previously detected
    - Some acknowledgment words appear both as turn signals and as fillers within turns
    - The tool must decide whether "yeah" means speaker change or continuation based on context
  - **What outcome do they expect?** 
    - A formatted transcript with 18 properly identified speaker turns (not 12 over-split turns)
    - Acknowledgments like "Exactly" and "Fair" correctly trigger speaker transitions
    - Fillers like "Yeah I think..." stay within the same speaker's turn
    - Minimal manual editing required - speaker attributions are 80%+ accurate

## Acceptance Criteria

- [ ] New acknowledgment words recognized: "exactly", "true", "fair", "definitely", "certainly", "agreed", "correct", "indeed".
- [ ] Exclamation acknowledgments trigger speaker change when appropriate ("Ha!", "Wow!", "Nice!", "Cool!").
- [ ] Context-aware handling reduces false positives for fillers vs acknowledgments.
- [ ] No regressions in existing speakerless tests.
- [ ] 3-speaker SpaceX test improves turn grouping (line count and accuracy trend).

## Non-Goals

Call out what is explicitly excluded from this feature.
