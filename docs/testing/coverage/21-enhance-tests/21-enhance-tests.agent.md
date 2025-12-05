Agent A Objective: Characterize and raise coverage for `transform/enhance.py` (speakerless routing, identity constraints, normalization interactions) to a solid baseline.

## Policies: Always Follow These

CRITICAL: When implementing any code, tests, or tasks, you must adhere to these repo policies without exception. These are not guidelines-they are requirements.

Read each policy document thoroughly before starting work. Implement them exactly as written. Do not interpret, modify, or skip any requirements.

* Coding Standards, Workflow, PR/commit procedures:  
  [code-change.instructions.md](../../../code-change.instructions.md)
  
  This document defines the complete development workflow including:  
  - Pre-implementation requirements (clarify objectives, document plans)  
  - Python coding standards (formatting, linting, typing, testing)  
  - Design principles (simplicity, reusability, extensibility, separation of concerns)  
  - Post-implementation requirements (quality checks, documentation updates)

* Developer Tooling: Poetry, Black, Ruff, Pyright, Pytest, pytest-cov, coverage, pre-commit, VSCode tasks:  
  [developer-tooling.md](../../../developer-tooling.md)
  
  This document covers all tooling setup and usage.

* Unit Test Policy (independence, determinism, clarity, AAA, etc.):  
  [unit-test-policy.md](../../../unit-test-policy.md)
  
  This document defines mandatory testing standards. Every test must comply.

Do not guess. Do not omit steps. Do not introduce inconsistencies. Follow the policies exactly.

## Workplan
- Inspect current behavior of `transform/enhance.py`; note key branches (speakerless routing, identity constraints, normalization interplay).
- Add characterization tests to lock current outputs for representative inputs.
- Add focused unit tests for helpers/branches to drive coverage toward the target (≈70%+ on the module).
- Keep tests in `tests/transform/` (or appropriate area); no code in this folder.
- Run `poetry run pytest --cov=src/transcript_etl_pipeline --cov-report=term` (or the VS Code tasks) to confirm coverage lift.
- Document any surprising behaviors/edge cases here and in issue #21; link PR(s).

## Acceptance Criteria
- Failing-before/passing-after tests added for the targeted behaviors.
- Module coverage for `transform/enhance.py` reaches roughly 70% or higher (cite report).
- Tests follow unit-test policy (deterministic, clear assertions, AAA).
- Issue #21 updated with findings, links to tests/PR, and coverage evidence.

---

## Completed Work (December 2024)

### Coverage Summary

**`transform/enhance.py` Coverage: 100%** (13/13 statements)

```
Name                                               Stmts   Miss  Cover   Missing
--------------------------------------------------------------------------------
src/transcript_etl_pipeline/transform/enhance.py      13      0   100%
--------------------------------------------------------------------------------
TOTAL                                                 13      0   100%
```

### Tests Added

21 new characterization tests were added to `tests/transform/test_enhance.py`:

1. **Identity Constraints (4 tests)**:
   - `test_self_identification_with_two_speakers_uses_alternation` - Documents that 2-speaker mode uses alternating assignment without identity constraints
   - `test_addresses_other_constraint_with_three_speakers` - Verifies "Thanks [Name]" prevents speaker-name grouping conflicts
   - `test_multiple_self_identifications_needs_more_changes` - Documents that weak change signals result in grouped output
   - `test_self_identifications_with_strong_change_signals` - Shows that Q&A/greeting patterns produce distinct speakers

2. **Normalization Interactions (7 tests)**:
   - `test_unix_line_endings_handled` - Unix LF line endings processed correctly
   - `test_mixed_line_endings_handled` - Mixed CRLF/LF handled gracefully
   - `test_whitespace_only_text_handled` - Whitespace-only input doesn't crash
   - `test_single_line_no_labels` - Single line triggers speakerless detection
   - `test_trailing_whitespace_preserved` - Content preserved despite whitespace
   - `test_empty_lines_between_speakers` - Empty lines between speakers handled
   - `test_very_long_speakerless_text` - Longer dialogue processed correctly

3. **Edge Cases (10 tests)**:
   - `test_single_sentence_speakerless` - Single sentence gets Speaker A
   - `test_question_answer_pattern_speakerless` - Q&A produces 2 speakers
   - `test_pronoun_shift_detection` - I/you exchange affects assignment
   - `test_greeting_triggers_speaker_change` - "Hello" triggers change
   - `test_thank_you_pattern_speaker_change` - "Thank you" triggers change
   - `test_acknowledgment_triggers_speaker_change` - "Sure" triggers change
   - `test_num_speakers_one` - Monologue mode assigns all to Speaker A
   - `test_num_speakers_four` - 4-speaker mode works correctly
   - `test_labeled_with_speakerless_content` - Mixed labeled/unlabeled preserved
   - `test_metadata_then_speakerless_dialogue` - Metadata + speakerless handled

### Key Findings

1. **2-speaker vs 3+ speaker behavior differs significantly**:
   - 2-speaker mode uses simple alternating assignment (A→B→A→B) based on detected change points
   - Identity constraints (self-identification, addresses_other) only affect 3+ speaker mode
   - 3+ speaker mode uses similarity-based grouping with constraint enforcement

2. **Speaker change detection relies on heuristics**:
   - Pronoun shifts (I→you, you→I)
   - Question-answer patterns
   - Dialogue markers (greetings, acknowledgments, thanks)
   - Identity constraints prevent but don't force groupings

3. **Line ending handling is robust**:
   - The pipeline handles Unix, Windows, and mixed line endings
   - Content is preserved regardless of input format

### All Quality Checks Passed

- ✅ Black formatting
- ✅ Ruff linting
- ✅ Pyright type checking
- ✅ 404 transform tests passing
- ✅ CodeQL security analysis - no issues
