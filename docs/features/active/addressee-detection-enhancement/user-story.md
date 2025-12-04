# addressee-detection-enhancement - User Story

- Issue: #17
- Owner: drmoisan
- Status: Draft
- Last Updated: 2025-12-04

## Story Statement

- As a user transcribing multi-person conversations, I want the tool to correctly identify when someone is addressing another person by name, so that utterances are never incorrectly assigned to the person being addressed.
- As a user, I want mid-sentence vocatives ("What do you think, Chris, about...") and lead-in patterns ("Oh, interesting, Devin") to be recognized as addressing someone, so that speaker assignments remain logically consistent.

## Problem / Why

Addressee detection is incomplete: sentences like "Oh, interesting, Devin" or mid-sentence vocatives ("What do you think, Chris, about...") can be assigned to the addressee, causing self-addressing violations. Constraints need broader patterns and enforcement in grouping/post-processing.

**Current State**:
- Basic vocative patterns work: "[Name], what...", "Thanks [Name]"
- Missing patterns cause self-addressing errors where the tool assigns "Hey Chris, how are you?" to Chris
- Mid-sentence vocatives are not detected, leading to logical inconsistencies

## Personas & Scenarios

- **Persona: Podcast Transcriber**
  - **Who they are**: A content creator who transcribes multi-guest podcast episodes for show notes and blog posts
  - **What they care about**: Natural conversation flow with correct speaker attribution; transcripts that make logical sense when read
  - **Their constraints**: Works with 3+ speaker conversations where guests frequently address each other by name; limited budget for manual editing time
  - **Their goals**: Produce accurate transcripts where it's always clear who said what; avoid confusing attributions that readers would immediately spot as errors
  - **Their frustrations**: Current tools assign phrases like "That's a great point, Maria" to Maria herself, creating obvious logical errors; mid-conversation vocatives ("What do you think, Alex, about this topic?") break speaker detection
  - **Their context**: Transcribes weekly episodes with rotating guests; needs reliable automation since manual checking of every name mention is too time-consuming

- **Scenario: Transcribing a Panel Discussion**
  - **Who is acting?** James, a podcast producer transcribing a three-person panel discussion
  - **What triggered the action?** James received a raw transcript that incorrectly assigned several utterances to the people being addressed rather than the speakers
  - **What steps do they take?**
    1. James pastes the raw transcript into the ETL pipeline with speakerless detection
    2. The tool analyzes the conversation and detects vocative patterns (names being used to address someone)
    3. The tool identifies lead-in addressees: "Oh, interesting, Sarah" is spoken TO Sarah, not BY Sarah
    4. The tool detects mid-sentence vocatives: "What do you think, Michael, about renewable energy?" is not Michael speaking
    5. The constraint system prevents assigning these utterances to the addressed person
    6. James receives a transcript where no one is shown addressing themselves
  - **What obstacles or decisions occur?** 
    - The conversation has frequent cross-talk where panelists address each other by name
    - Some names appear both as addressees and as speakers in adjacent turns
    - The tool must distinguish between "Thanks, Maria" (addressing Maria) and "Maria mentioned earlier..." (third-person reference)
    - Mid-sentence vocatives require careful pattern matching to avoid false positives
  - **What outcome do they expect?** 
    - A logically consistent transcript where "Hey Chris, how are you?" is never assigned to Chris
    - All vocative patterns (beginning, middle, end) correctly identified
    - No self-addressing violations in the final output
    - 100% accuracy on addressee constraint enforcement (no speaker addresses themselves)

## Acceptance Criteria

- [ ] `detect_addresses_to_person()` recognizes the new patterns (including mid-sentence vocatives).
- [ ] Constraint enforcement prevents assigning an utterance to the person it addresses.
- [ ] Grouping/post-processing respects `addresses_other` constraints.
- [ ] Integration test: "Hey Chris, how are you?" is not assigned to Chris.
- [ ] No regression in existing speakerless tests.

## Non-Goals

- Broader speaker logic enhancements (acknowledgments, similarity refinements) are out of scope for this subfeature.
