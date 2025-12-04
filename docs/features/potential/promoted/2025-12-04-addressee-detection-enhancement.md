# addressee-detection-enhancement (Issue: #17)

- Date captured: 2025-12-04
- Author: Dan Moisan
- Status: Promoted -> docs/features/active/addressee-detection-enhancement/ (Issue #17)
- Issue: #17
- Issue URL: https://github.com/drmoisan/transcript-etl-pipeline/issues/17
- Last Updated: 2025-12-04

## Problem / Why

Addressee detection is incomplete: sentences like “Oh, interesting, Devin” or mid-sentence vocatives (“What do you think, Chris, about…”) can be assigned to the addressee, causing self-addressing violations. The constraint system needs broader patterns and enforcement across grouping/post-processing.

## Proposed Behavior

- Expand vocative patterns to catch mid-sentence and lead-in forms (“Oh, interesting, [Name]”, “Exactly, [Name]”, “Good point, [Name]”, “What do you think, [Name], about…”).
- Ensure constraints are used during grouping and post-processing so sentences that address [Name] are not assigned to [Name].
- Add an integration test to confirm addressee constraints in the speakerless pipeline.

## Acceptance Criteria (early draft)

- [ ] `detect_addresses_to_person()` recognizes the new patterns (including mid-sentence vocatives).
- [ ] Constraint enforcement prevents assigning an utterance to the person it addresses.
- [ ] Grouping/post-processing respects `addresses_other` constraints.
- [ ] Integration test: “Hey Chris, how are you?” is not assigned to Chris.
- [ ] No regression in existing speakerless tests.

## Constraints & Risks

- Must keep behavior lightweight and avoid regressions in 2-speaker cases.
- Distinguish addressee patterns from third-person mentions to avoid false positives.
- Logging/tests should validate without impacting runtime performance.

## Test Conditions to Consider

- [ ] Unit: new patterns in `identity_constraints.detect_addresses_to_person()`.
- [ ] Integration: speakerless pipeline test ensures addressed person is not assigned.
- [ ] Verification that constraints are consumed in `group_sentences_by_similarity()` and post-processing.

## Next Step

- [ ] Promote to GitHub issue (feature request template)
- [ ] Create `docs/features/active/addressee-detection-enhancement/` folder from the template
