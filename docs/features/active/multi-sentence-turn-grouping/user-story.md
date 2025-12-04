# multi-sentence-turn-grouping - User Story

- Issue: #16
- Owner: drmoisan
- Status: Draft
- Last Updated: 2025-12-04

## Story Statement

- As a user transcribing technical discussions or debates, I want multi-sentence explanations and arguments to stay together under one speaker, so that complex thoughts aren't artificially fragmented across multiple speaker labels.
- As a user, I want rhetorical questions and topic continuations to be recognized as part of the same speaker's turn, so that natural speech patterns don't trigger incorrect speaker changes.

## Problem / Why

Speakerless detection over-splits and under-groups multi-sentence turns. The algorithm outputs 12 lines instead of the expected 18 turns because change heuristics (pronoun shifts, dialogue markers) fire incorrectly inside a single speaker's continuous thought. There is no rhetorical question or topic continuation handling, causing logical multi-sentence explanations to be broken apart.

**Current State**:
- Algorithm detects speaker changes too aggressively within monologues
- Rhetorical questions ("Right? And so...") trigger false speaker changes
- Topic continuations with same subject matter split incorrectly
- No debug visibility into which heuristics are firing
- 3-speaker SpaceX test produces 12 lines instead of 18 expected turns

## Personas & Scenarios

- **Persona: Conference Call Transcriber (Business Context)**
  - **Who they are**: A project manager who transcribes strategy meetings and technical discussions where participants explain complex ideas at length
  - **What they care about**: Preserving complete thoughts and arguments; having multi-sentence explanations stay under one speaker so the logical flow is maintained
  - **Their constraints**: Deals with 3-4 speaker calls where people give detailed explanations with rhetorical questions and topic shifts; limited time to manually fix fragmented turns
  - **Their goals**: Produce transcripts where each speaker's complete thought is captured as a single turn; avoid artificial mid-thought speaker changes that confuse readers
  - **Their frustrations**: Current tools split sentences like "The launch was successful. Right? And the landing was perfect too." into multiple speakers, breaking the natural flow; rhetorical questions cause false speaker changes
  - **Their context**: Transcribes weekly technical strategy calls where engineers and product managers explain detailed plans that span multiple sentences

- **Scenario: Transcribing a Technical Strategy Discussion**
  - **Who is acting?** Amanda, a project manager transcribing a 3-person strategy meeting about a product launch
  - **What triggered the action?** Amanda received a transcript where one person's 4-sentence explanation was split across 3 different speaker labels, making it unreadable
  - **What steps do they take?**
    1. Amanda pastes the raw transcript into the ETL pipeline with speakerless detection
    2. The tool analyzes the conversation and detects where speaker changes actually occur
    3. The tool recognizes rhetorical questions ("Right?") followed by continuations ("And then...") as same-speaker turns
    4. The tool detects topic continuation when keyword overlap shows the same subject is being discussed
    5. The tool groups consecutive sentences from the same speaker into single turns
    6. Amanda receives a transcript with 18 logical speaker turns instead of 12 fragmented ones
  - **What obstacles or decisions occur?**
    - The conversation has genuine questions (speaker change) vs rhetorical questions (same speaker)
    - Pronoun shifts ("I think" → "you might") occur within one person's explanation
    - Some dialogue markers ("Well..." "So...") start new thoughts by the same speaker, not new speakers
    - The tool must balance avoiding over-splitting with still detecting real speaker changes
  - **What outcome do they expect?**
    - Each speaker's multi-sentence explanations stay grouped as single turns
    - Rhetorical continuations ("Right? And..." "You know? So...") don't trigger false speaker changes
    - Topic continuations (same keywords, same subject) remain under one speaker
    - 18 properly grouped speaker turns with at least 80% correct speaker assignments
    - Natural speech patterns preserved without artificial fragmentation

## Acceptance Criteria

- [ ] Debug logging in `detect_speaker_changes()` shows heuristic triggers (sentence index + trigger).
- [ ] Rhetorical question continuations do not trigger speaker changes.
- [ ] Topic continuation heuristic suppresses changes when keyword overlap is high (>40%).
- [ ] Pronoun shift change detection is gated (boundary + dialogue marker) to reduce false positives.
- [ ] 3-speaker SpaceX test outputs 18 lines (currently 12) and can be un-XFAILed.
- [ ] No regression to 2-speaker accuracy or existing tests.

## Non-Goals

- Broader speaker logic refinements (acknowledgments, addressee patterns, similarity features) are tracked separately.
