# Remediation Plan — 2025-12-04-baseline-coverage-20

Timestamp: 2026-02-02T15-20

## Scope Lock

This plan is limited to the remediation inputs listed in `remediation-inputs.2026-02-02T15-20.md` (items 1–13). No additional scope is permitted.

## Scope Confirmation (In-Scope Items)

1. #21 Enhance tests coverage target not met (enhance.py ≥ 70%)
2. #22 Speakerless heuristics coverage targets not met (speakerless.py, speaker_helpers.py ≥ 70% + tag/rhetorical tests)
3. #23 Identity + normalize coverage targets not met (combined ≥ 75%)
4. #26 Notes regressions acceptance criteria not evidenced
5. #27 Formatters + parser coverage targets not met (≥ 70%, deterministic in-memory tests)
6. #25 E2E CLI tests violate unit-test policy (no temp files)
7. Test-policy violations (temp files + external downloads)
8. Plan checklists incomplete for #21–#28
9. MVP boundaries + metrics not explicit in initiative.md
10. Milestone status mismatch in initiative.md
11. Coverage gate sequencing criteria missing (orchestration.md + ci-coverage spec)
12. #24 fixture ownership & reuse governance missing in spec
13. #25 policy compliance decision missing in spec

## Baseline Evidence

(Record baseline toolchain output here in Phase 0.)

## Coverage Evidence

(Record per-module coverage evidence here in Phases 1–7.)

## QA Evidence

(Record doc checks, lint, link checks, and final toolchain output here in Phase 9.)

## Implementation Plan (Atomic Tasks)

### Phase 0 — Context & Inputs
- [ ] [P0-T1] Read `.github/copilot-instructions.md` to establish baseline agent rules.
  - Acceptance: The file exists and was reviewed; add a dated line to the “QA Evidence” section starting with `Policy Review: copilot-instructions`.
- [ ] [P0-T2] Read `.github/instructions/general-code-change.instructions.md` to confirm workflow requirements.
  - Acceptance: “QA Evidence” includes `Policy Review: general-code-change` with an ISO-8601 timestamp.
- [ ] [P0-T3] Read `.github/instructions/general-unit-test.instructions.md` to confirm unit-test rules.
  - Acceptance: “QA Evidence” includes `Policy Review: general-unit-test` with an ISO-8601 timestamp.
- [ ] [P0-T4] Read `.github/instructions/python-code-change.instructions.md` to confirm Python rules.
  - Acceptance: “QA Evidence” includes `Policy Review: python-code-change` with an ISO-8601 timestamp.
- [ ] [P0-T5] Read `.github/instructions/python-unit-test.instructions.md` to confirm Pytest rules.
  - Acceptance: “QA Evidence” includes `Policy Review: python-unit-test` with an ISO-8601 timestamp.
- [ ] [P0-T6] Review `remediation-inputs.2026-02-02T15-20.md`, `initiative.md`, and `orchestration.md`, then confirm scope by keeping the “Scope Confirmation” list aligned to items 1–13 only.
  - Acceptance: “Scope Confirmation (In-Scope Items)” lists exactly 13 items matching the remediation inputs.
- [ ] [P0-T7] Capture baseline formatting output with `poetry run black .` and paste output under “Baseline Evidence”.
  - Acceptance: “Baseline Evidence” contains a fenced block labeled `Black Baseline` with the exact command output.
- [ ] [P0-T8] Capture baseline lint output with `poetry run ruff check` and paste output under “Baseline Evidence”.
  - Acceptance: “Baseline Evidence” contains a fenced block labeled `Ruff Baseline` with the exact command output.
- [ ] [P0-T9] Capture baseline type-check output with `poetry run pyright` and paste output under “Baseline Evidence”.
  - Acceptance: “Baseline Evidence” contains a fenced block labeled `Pyright Baseline` with the exact command output.
- [ ] [P0-T10] Capture baseline test+coverage output with `poetry run pytest --cov=src/transcript_etl_pipeline --cov-report=term --cov-report=xml --cov-report=html` and paste output under “Baseline Evidence”.
  - Acceptance: “Baseline Evidence” contains a fenced block labeled `Pytest Baseline` with the exact command output.

### Phase 1 — #21 Enhance Coverage (enhance.py)
- [ ] [P1-T1] Add a unit test in `tests/transform/test_enhance.py` for `enhance_text` when `has_speaker_labels` is `False`, stubbing `assign_speaker_labels` and `detect_paragraphs` to assert the speakerless branch returns the paragraph-detected output and an empty mapping.
  - Acceptance: `tests/transform/test_enhance.py` contains a test named `test_enhance_text_speakerless_branch_uses_assign_and_paragraphs` with assertions for output text and `{}` mapping.
- [ ] [P1-T2] Add a unit test in `tests/transform/test_enhance.py` for `enhance_text` when `has_speaker_labels` is `True`, stubbing `resolve_speakers` and `detect_paragraphs` to assert the labeled branch returns the resolved mapping and paragraph-detected output.
  - Acceptance: `tests/transform/test_enhance.py` contains a test named `test_enhance_text_labeled_branch_uses_resolve_and_paragraphs` with assertions for output text and mapping content.
- [ ] [P1-T3] Run `poetry run pytest tests/transform/test_enhance.py -k "speakerless_branch_uses_assign_and_paragraphs or labeled_branch_uses_resolve_and_paragraphs"`.
  - Acceptance: Command exits with code 0.
- [ ] [P1-T4] Run `poetry run pytest tests/transform/test_enhance.py --cov=src/transcript_etl_pipeline/transform/enhance.py --cov-report=term` and record results under “Coverage Evidence”.
  - Acceptance: Coverage output shows `enhance.py` coverage ≥ 70% and the output is recorded in “Coverage Evidence” as `Enhance Coverage`.
- [ ] [P1-T5] Update `2025-12-04-enhance-tests-21/plan.2026-02-02T11-49.md` to check off P4-T1 and P5-T1..P5-T4 with the recorded coverage evidence.
  - Acceptance: The plan file shows those tasks checked and references the recorded coverage snippet.
- [ ] [P1-T6] Update Issue #21 with the coverage snippet and the two new test names.
  - Acceptance: `gh issue view 21 --json body -q ".body"` output includes both test names and the coverage snippet.

### Phase 2 — #22 Speakerless Heuristics + NLTK Download Compliance
- [ ] [P2-T1] Add a unit test in `tests/transform/test_speakerless.py` for `detect_speaker_changes` using the tag question input `"We should proceed, right?\r\nYes, let's do it."` and assert that index `1` is included in `changes`.
  - Acceptance: `tests/transform/test_speakerless.py` contains `test_detect_speaker_changes_tag_question_includes_change` and the test asserts `1 in changes`.
- [ ] [P2-T2] Add a unit test in `tests/transform/test_speakerless.py` for `detect_speaker_changes` using continuation text `"I think we should proceed.\r\nYou know I agree."` and assert `changes == [0]`.
  - Acceptance: `tests/transform/test_speakerless.py` contains `test_detect_speaker_changes_continuation_no_shift` asserting `changes == [0]`.
- [ ] [P2-T3] Add a unit test in `tests/transform/test_speakerless.py` for `assign_speaker_labels` with `num_speakers=3` and input containing `"I'm Frank Oz. Thanks Frank."`, asserting the addressee line is not assigned to Frank’s speaker label.
  - Acceptance: `tests/transform/test_speakerless.py` contains `test_assign_speaker_labels_addressee_not_self` and asserts distinct speaker labels for the self-ID and addressee line.
- [ ] [P2-T4] Add a unit test in `tests/transform/test_speakerless.py` for `assign_speaker_labels` with a closing statement `"Great. Thank you both."` after self-identification, asserting the closing statement is assigned to the organizer’s speaker.
  - Acceptance: `tests/transform/test_speakerless.py` contains `test_assign_speaker_labels_closing_statement_to_organizer` with assertions on the organizer’s speaker label.
- [ ] [P2-T5] Add a unit test in `tests/transform/test_speaker_helpers.py` for `detect_dialogue_markers("Right?")` asserting `is_acknowledgment` is `True`.
  - Acceptance: `tests/transform/test_speaker_helpers.py` contains `test_detect_dialogue_markers_right_tag_question_acknowledgment` asserting `markers["is_acknowledgment"] is True`.
- [ ] [P2-T6] Add a unit test in `tests/transform/test_speaker_helpers.py` for `resolve_addresses_other_violations` with sentences `"I'm Frank.", "Thanks Frank.", "Fred?"` to verify the addressee line and follow-through line are reassigned away from Frank.
  - Acceptance: `tests/transform/test_speaker_helpers.py` contains `test_resolve_addresses_other_follow_through_reassigns` with assertions that both indices are not assigned to Frank’s speaker.
- [ ] [P2-T7] Add a unit test in `tests/transform/test_speaker_helpers.py` for `group_sentences_by_similarity` using two sentences, `change_points = [0, 1]`, `num_speakers = 3`, and assert assignments match the round-robin branch result `[0, 1]`.
  - Acceptance: `tests/transform/test_speaker_helpers.py` contains `test_group_sentences_round_robin_two_segments` asserting assignments equal `[0, 1]`.
- [ ] [P2-T8] Add a unit test in `tests/transform/test_speaker_helpers.py` for `group_sentences_by_similarity` with three self-identified speakers and assert the three indices map to three distinct speaker IDs.
  - Acceptance: `tests/transform/test_speaker_helpers.py` contains `test_group_sentences_distinct_self_identifications` asserting `len(set(...)) == 3` for the self-ID indices.
- [ ] [P2-T9] Add a pytest fixture in `tests/transform/test_speaker_helpers.py` that monkeypatches `nltk.download` to raise if called and `nltk.data.find` to return success, and apply it to tests that call `ensure_nltk_data`.
  - Acceptance: The file contains a fixture named `no_nltk_downloads` and tests referencing it no longer call `nltk.download`.
- [ ] [P2-T10] Add a pytest fixture in `tests/transform/test_speaker_helpers.py` that monkeypatches `nltk.word_tokenize` and `nltk.pos_tag` with deterministic stubs, and update at least one pronoun-pattern test to use this fixture.
  - Acceptance: The file contains a fixture named `stub_nltk_tagging` and `test_first_person_detection` uses it without network access.
- [ ] [P2-T11] Run `poetry run coverage report --include=src/transcript_etl_pipeline/transform/speakerless.py,src/transcript_etl_pipeline/transform/speaker_helpers.py --fail-under=70` and record output under “Coverage Evidence”.
  - Acceptance: The command exits with code 0 and “Coverage Evidence” includes a `Speakerless Coverage` block.
- [ ] [P2-T12] Update Issue #22 with coverage evidence and the added test names.
  - Acceptance: `gh issue view 22 --json body -q ".body"` output includes the coverage evidence and test names.
- [ ] [P2-T13] Update `2025-12-04-speakerless-heuristics-22/22-speakerless-heuristics.md` with any new edge-case notes from the added tests.
  - Acceptance: The document contains a new “Edge cases” or “Surprises” note referencing tag/rhetorical questions.

### Phase 3 — #23 Normalize Test Scenarios (normalize.py)
- [ ] [P3-T1] Add test `test_normalize_line_endings_mixed_inputs` in `tests/transform/test_normalize.py` covering `_normalize_line_endings("a\r\nb\nc\rd") == "a\r\nb\r\nc\r\nd"`.
  - Acceptance: Running `poetry run pytest tests/transform/test_normalize.py -k test_normalize_line_endings_mixed_inputs` exits with code 0.
- [ ] [P3-T2] Add test `test_clean_whitespace_collapses_duplicate_spaces` covering `_clean_whitespace("A  B\r\nC   D") == "A B\r\nC D"`.
  - Acceptance: Running `poetry run pytest tests/transform/test_normalize.py -k test_clean_whitespace_collapses_duplicate_spaces` exits with code 0.
- [ ] [P3-T3] Add test `test_clean_whitespace_collapses_blank_lines_and_trailing` covering `_clean_whitespace("A\r\n\r\n\r\nB\r\n\r\n") == "A\r\n\r\nB"`.
  - Acceptance: Running `poetry run pytest tests/transform/test_normalize.py -k test_clean_whitespace_collapses_blank_lines_and_trailing` exits with code 0.
- [ ] [P3-T4] Add test `test_is_label_accepts_capitalized_token` covering `_is_label("Speaker:") is True`.
  - Acceptance: Running `poetry run pytest tests/transform/test_normalize.py -k test_is_label_accepts_capitalized_token` exits with code 0.
- [ ] [P3-T5] Add test `test_is_label_rejects_lowercase_token` covering `_is_label("speaker:") is False`.
  - Acceptance: Running `poetry run pytest tests/transform/test_normalize.py -k test_is_label_rejects_lowercase_token` exits with code 0.
- [ ] [P3-T6] Add test `test_is_label_rejects_token_with_spaces` covering `_is_label("Speaker Name:") is False`.
  - Acceptance: Running `poetry run pytest tests/transform/test_normalize.py -k test_is_label_rejects_token_with_spaces` exits with code 0.
- [ ] [P3-T7] Add test `test_normalize_labels_inserts_space_after_label` covering `_normalize_labels("Bob:Hello") == "Bob: Hello"`.
  - Acceptance: Running `poetry run pytest tests/transform/test_normalize.py -k test_normalize_labels_inserts_space_after_label` exits with code 0.
- [ ] [P3-T8] Add test `test_normalize_labels_splits_mid_line_label` covering `_normalize_labels("Hi. Bob: Hello") == "Hi.\r\nBob: Hello"`.
  - Acceptance: Running `poetry run pytest tests/transform/test_normalize.py -k test_normalize_labels_splits_mid_line_label` exits with code 0.
- [ ] [P3-T9] Add test `test_normalize_text_applies_all_steps` covering `normalize_text("Bob:Hello\n\nA  B") == "Bob: Hello\r\n\r\nA B"`.
  - Acceptance: Running `poetry run pytest tests/transform/test_normalize.py -k test_normalize_text_applies_all_steps` exits with code 0.

### Phase 4 — #23 Coverage Evidence (identity_constraints.py + normalize.py)
- [ ] [P4-T1] Run `poetry run pytest --cov=src/transcript_etl_pipeline --cov-report=term-missing` and record module coverage for `identity_constraints.py` and `normalize.py` in `2025-12-04-identity-normalize-23/coverage-results.md`.
  - Acceptance: `coverage-results.md` exists with a table listing both modules and coverage values ≥ 75% combined.
- [ ] [P4-T2] Update Issue #23 with the coverage table and command used.
  - Acceptance: `gh issue view 23 --json body -q ".body"` output includes the coverage table and command.
- [ ] [P4-T3] Update `2025-12-04-identity-normalize-23/plan.2026-02-02T13-08.md` to check off P3-T1..P3-T9 and P4-T1..P4-T3.
  - Acceptance: The plan file shows those tasks checked.

### Phase 5 — #26 Notes Regressions
- [ ] [P5-T1] Add a “Regression Cases” section to `2025-12-04-notes-regressions-26/spec.md` listing five cases with explicit input and expected output snippets.
  - Acceptance: The spec contains a “Regression Cases” section with five numbered cases and explicit input/output blocks.
- [ ] [P5-T2] Add test `test_regression_clean_markdown_text_escapes` in `tests/transform/test_notes.py` covering `_clean_markdown_text("\\$100 **bold** __strong__") == "$100 bold strong"`.
  - Acceptance: Running `poetry run pytest tests/transform/test_notes.py -k test_regression_clean_markdown_text_escapes` exits with code 0.
- [ ] [P5-T3] Add test `test_regression_parse_bullet_line_indentation_levels` covering `_parse_bullet_line("- Item")` and `_parse_bullet_line("  - Nested")` returning `(1, "Item")` and `(2, "Nested")`.
  - Acceptance: Running `poetry run pytest tests/transform/test_notes.py -k test_regression_parse_bullet_line_indentation_levels` exits with code 0.
- [ ] [P5-T4] Add test `test_regression_get_heading_level_leading_whitespace` covering `_get_heading_level("  ## Heading") == 2`.
  - Acceptance: Running `poetry run pytest tests/transform/test_notes.py -k test_regression_get_heading_level_leading_whitespace` exits with code 0.
- [ ] [P5-T5] Add test `test_regression_transform_notes_label_after_h1_with_label` covering `transform_notes("# Title\n\n- Bullet", label="Meeting Notes")` and asserting the H2 header uses the provided label.
  - Acceptance: Running `poetry run pytest tests/transform/test_notes.py -k test_regression_transform_notes_label_after_h1_with_label` exits with code 0.
- [ ] [P5-T6] Add test `test_regression_parse_markdown_mixed_order` covering `_parse_markdown("# Title\n- One\n## Section\n- Two")` and asserting heading/bullet ordering.
  - Acceptance: Running `poetry run pytest tests/transform/test_notes.py -k test_regression_parse_markdown_mixed_order` exits with code 0.
- [ ] [P5-T7] Run `poetry run pytest tests/transform/test_notes.py` and record output in “Coverage Evidence” as `Notes Regression Tests`.
  - Acceptance: “Coverage Evidence” includes the command output and the command exits with code 0.
- [ ] [P5-T8] Run `poetry run coverage report --include=src/transcript_etl_pipeline/transform/notes.py --fail-under=70` and record output.
  - Acceptance: The command exits with code 0 and “Coverage Evidence” includes a `Notes Coverage` block.
- [ ] [P5-T9] Update Issue #26 with the five regression cases and coverage evidence.
  - Acceptance: `gh issue view 26 --json body -q ".body"` output includes the five case titles and coverage snippet.
- [ ] [P5-T10] Update `2025-12-04-notes-regressions-26/plan.2026-02-02T13-09.md` to check off P1-T1..P1-T5 and P2-T1..P2-T3.
  - Acceptance: The plan file shows those tasks checked.

### Phase 6 — #27 Formatters + Parser (No Temp Files)
- [ ] [P6-T1] Add fake DOCX classes (`FakeDocxDocument`, `FakeDocxParagraph`, `FakeDocxRun`, `FakeParagraphFormat`) in `tests/formatters/test_docx_formatter.py` to avoid filesystem writes.
  - Acceptance: The file contains class definitions for all four fakes.
- [ ] [P6-T2] Replace file-based DOCX tests with in-memory tests that call `_format_paragraph`, `_apply_spacing`, and `_apply_font`, removing `tmp_path` and `DocxDocument` usage.
  - Acceptance: `tests/formatters/test_docx_formatter.py` contains no `tmp_path` or `DocxDocument(` references.
- [ ] [P6-T3] Add test `test_format_paragraph_notes_header_heading_level` asserting heading style mapping for `heading_level=3`.
  - Acceptance: Running `poetry run pytest tests/formatters/test_docx_formatter.py -k test_format_paragraph_notes_header_heading_level` exits with code 0.
- [ ] [P6-T4] Add test `test_format_paragraph_notes_body_bullet_level_two` asserting `List Bullet 2` is used for `bullet_level=2`.
  - Acceptance: Running `poetry run pytest tests/formatters/test_docx_formatter.py -k test_format_paragraph_notes_body_bullet_level_two` exits with code 0.
- [ ] [P6-T5] Add test `test_apply_spacing_sets_before_after_and_single_spacing` asserting `space_before`, `space_after`, and `line_spacing_rule` are set.
  - Acceptance: Running `poetry run pytest tests/formatters/test_docx_formatter.py -k test_apply_spacing_sets_before_after_and_single_spacing` exits with code 0.
- [ ] [P6-T6] Replace file-based RTF tests with in-memory tests for `_generate_rtf`, `_format_paragraph`, and `_escape_rtf`, removing `tempfile` usage.
  - Acceptance: `tests/formatters/test_rtf_formatter.py` contains no `tempfile`, `NamedTemporaryFile`, or `unlink` references.
- [ ] [P6-T7] Add test `test_format_paragraph_speaker_label_bold_and_body_text` asserting bold label wrapper and escaped body text in `_format_paragraph`.
  - Acceptance: Running `poetry run pytest tests/formatters/test_rtf_formatter.py -k test_format_paragraph_speaker_label_bold_and_body_text` exits with code 0.
- [ ] [P6-T8] Add test `test_escape_rtf_converts_newlines_to_par` asserting `_escape_rtf("Line1\nLine2") == "Line1\\par Line2"`.
  - Acceptance: Running `poetry run pytest tests/formatters/test_rtf_formatter.py -k test_escape_rtf_converts_newlines_to_par` exits with code 0.
- [ ] [P6-T9] Replace file-based Markdown tests with in-memory tests for `_generate_markdown` and `_format_paragraph`, removing `tempfile` usage.
  - Acceptance: `tests/formatters/test_md_formatter.py` contains no `tempfile`, `NamedTemporaryFile`, or `unlink` references.
- [ ] [P6-T10] Add test `test_notes_header_inserts_blank_line_and_heading_prefix` asserting notes header spacing and `#` prefix.
  - Acceptance: Running `poetry run pytest tests/formatters/test_md_formatter.py -k test_notes_header_inserts_blank_line_and_heading_prefix` exits with code 0.
- [ ] [P6-T11] Add test `test_transcript_label_gets_blank_line_before_when_not_first` asserting blank-line rule for transcript labels.
  - Acceptance: Running `poetry run pytest tests/formatters/test_md_formatter.py -k test_transcript_label_gets_blank_line_before_when_not_first` exits with code 0.
- [ ] [P6-T12] Add parser test `test_transcript_label_inline_text_is_preserved` in `tests/document/test_parser_unit.py`.
  - Acceptance: Running `poetry run pytest tests/document/test_parser_unit.py -k test_transcript_label_inline_text_is_preserved` exits with code 0.
- [ ] [P6-T13] Add parser test `test_unlabeled_transcript_lines_create_regular_paragraphs` in `tests/document/test_parser_unit.py`.
  - Acceptance: Running `poetry run pytest tests/document/test_parser_unit.py -k test_unlabeled_transcript_lines_create_regular_paragraphs` exits with code 0.
- [ ] [P6-T14] Add parser test `test_is_metadata_label_accepts_meeting_title_variants` in `tests/document/test_parser_unit.py`.
  - Acceptance: Running `poetry run pytest tests/document/test_parser_unit.py -k test_is_metadata_label_accepts_meeting_title_variants` exits with code 0.
- [ ] [P6-T15] Run `poetry run coverage report --include=src/transcript_etl_pipeline/formatters/docx_formatter.py,src/transcript_etl_pipeline/formatters/rtf_formatter.py,src/transcript_etl_pipeline/formatters/md_formatter.py,src/transcript_etl_pipeline/document/parser.py --fail-under=70` and record output.
  - Acceptance: Command exits with code 0 and “Coverage Evidence” includes `Formatters+Parser Coverage`.
- [ ] [P6-T16] Update Issue #27 with coverage evidence and scenario list.
  - Acceptance: `gh issue view 27 --json body -q ".body"` output includes the coverage snippet and the scenario list.
- [ ] [P6-T17] Update `2025-12-04-formatters-parser-27/plan.2026-02-02T13-08.md` to check off P1-T1..P5-T3.
  - Acceptance: The plan file shows those tasks checked.

### Phase 7 — #25 CLI E2E Tests (No Temp Files)
- [ ] [P7-T1] Add a `run_cli` helper and shared monkeypatch fixture in `tests/integration/test_cli_e2e_speakerless.py` to stub `setup_logging`, `config.save_last_output_folder`, `_save_document`, `_extract_text`, and `Path.exists` checks, removing all `tmp_path` usage.
  - Acceptance: `tests/integration/test_cli_e2e_speakerless.py` contains `def run_cli(` and no `tmp_path` references.
- [ ] [P7-T2] Refactor `TestCLISpeakerless3SpeakersDOCX` tests to use the helper and in-memory fixtures, asserting `_save_document` captures speaker labels.
  - Acceptance: Each test in the class calls `run_cli` and asserts captured document content includes `Speaker`.
- [ ] [P7-T3] Refactor `TestCLISpeakerlessMarkdown` tests to use the helper and in-memory fixtures, asserting `_save_document` is called with `output_format == "md"`.
  - Acceptance: The class uses `run_cli` and asserts the captured format for each test.
- [ ] [P7-T4] Refactor `TestCLISpeakerlessRTF` tests to use the helper and in-memory fixtures, asserting `_save_document` is called with `output_format == "rtf"`.
  - Acceptance: The class uses `run_cli` and asserts the captured format for each test.
- [ ] [P7-T5] Refactor `TestCLISpeakerlessAutoDetect` to use the helper and in-memory fixtures, asserting speaker labels exist.
  - Acceptance: The test uses `run_cli` and asserts speaker labels in captured text.
- [ ] [P7-T6] Refactor `TestCLIErrorHandling` to avoid filesystem by mocking `Path.exists` and asserting non-zero exit codes.
  - Acceptance: The tests use monkeypatched `Path.exists` and assert `exit_code != 0`.
- [ ] [P7-T7] Add a `run_cli` helper and shared monkeypatch fixture in `tests/integration/test_cli_e2e_notes.py` to stub `setup_logging`, `config.save_last_output_folder`, `_save_document`, `_extract_text`, and `read_document`, removing all `tmp_path` usage.
  - Acceptance: `tests/integration/test_cli_e2e_notes.py` contains `def run_cli(` and no `tmp_path` references.
- [ ] [P7-T8] Refactor `TestCLINotesOnly` to use the helper and in-memory fixtures, asserting `_save_document` is called with the expected format per test.
  - Acceptance: The class uses `run_cli` and asserts the captured format for each test.
- [ ] [P7-T9] Refactor `TestCLINotesAndTranscript` to use the helper and in-memory fixtures, asserting both notes and transcript sections exist.
  - Acceptance: The class uses `run_cli` and asserts notes and transcript sections are present.
- [ ] [P7-T10] Refactor `TestCLIUpdateModeNotes` to use the helper and mocked `read_document`, asserting note sections are added/replaced.
  - Acceptance: The class uses `run_cli` and asserts the notes section count changes as expected.
- [ ] [P7-T11] Refactor `TestCLIUpdateModeTranscript` to use the helper and mocked `read_document`, asserting transcript sections are added/replaced.
  - Acceptance: The class uses `run_cli` and asserts transcript section counts match the action.
- [ ] [P7-T12] Refactor `TestCLIUpdateModeDOCX` to avoid filesystem by mocking `read_document` and `Path.exists`, asserting `_save_document` is called.
  - Acceptance: The test uses monkeypatching and asserts `_save_document` invocation.
- [ ] [P7-T13] Refactor `TestCLINotesErrorHandling` to avoid filesystem by mocking `Path.exists` and asserting non-zero exit codes.
  - Acceptance: The tests use monkeypatched `Path.exists` and assert `exit_code != 0`.
- [ ] [P7-T14] Run `poetry run coverage report --include=src/transcript_etl_pipeline/cli.py,src/transcript_etl_pipeline/document/reader.py,src/transcript_etl_pipeline/extract/from_file.py,src/transcript_etl_pipeline/transform/notes.py --fail-under=70` and record output.
  - Acceptance: Command exits with code 0 and “Coverage Evidence” includes `CLI Coverage`.
- [ ] [P7-T15] Update Issue #25 with coverage evidence and the test scenario summary.
  - Acceptance: `gh issue view 25 --json body -q ".body"` output includes the coverage snippet and scenario summary.

### Phase 8 — Documentation Gaps + Plan Checklist Reconciliation
- [ ] [P8-T1] Add an “MVP Scope & Metrics” section to `initiative.md` listing the MVP module set and measurable criteria.
  - Acceptance: `initiative.md` contains the section with module list and a coverage target table.
- [ ] [P8-T2] Align “Milestones & Status” in `initiative.md` with actual plan statuses from #21–#27 plan files.
  - Acceptance: Milestone statuses match the `Status` fields in the corresponding plan files.
- [ ] [P8-T3] Add a “Coverage Gate Sequencing Criteria” section to `orchestration.md` describing ratchet prerequisites tied to milestone completion and coverage targets.
  - Acceptance: `orchestration.md` contains the section with explicit prerequisites and thresholds.
- [ ] [P8-T4] Add a matching “Coverage Gate Sequencing Criteria” section to `2025-12-04-ci-coverage-gate-28/spec.md` referencing the same thresholds and milestone gates.
  - Acceptance: The spec contains the section and mirrors the criteria from `orchestration.md`.
- [ ] [P8-T5] Add a “Fixture Ownership & Reuse Governance” section to `2025-12-04-multi-speaker-fixtures-24/spec.md` detailing ownership, update process, and reuse rules.
  - Acceptance: The spec contains the section with owner, review, and reuse guidance.
- [ ] [P8-T6] Add a “Policy Compliance Decision” section to `2025-12-04-e2e-speakerless-notes-25/spec.md` stating that tests are redesigned to avoid temp files (no exceptions).
  - Acceptance: The spec contains the section with a clear decision statement.
- [ ] [P8-T7] Reconcile checklist status in `2025-12-04-enhance-tests-21/plan.2026-02-02T11-49.md` and update `Last Updated`.
  - Acceptance: The plan file shows updated checkboxes and a refreshed `Last Updated` timestamp.
- [ ] [P8-T8] Reconcile checklist status in `2025-12-04-speakerless-heuristics-22/plan.2026-02-02T12-24.md` and update `Last Updated`.
  - Acceptance: The plan file shows updated checkboxes and a refreshed `Last Updated` timestamp.
- [ ] [P8-T9] Reconcile checklist status in `2025-12-04-identity-normalize-23/plan.2026-02-02T13-08.md` and update `Last Updated`.
  - Acceptance: The plan file shows updated checkboxes and a refreshed `Last Updated` timestamp.
- [ ] [P8-T10] Reconcile checklist status in `2025-12-04-multi-speaker-fixtures-24/plan.2026-02-02T13-09.md` and update `Last Updated`.
  - Acceptance: The plan file shows updated checkboxes and a refreshed `Last Updated` timestamp.
- [ ] [P8-T11] Reconcile checklist status in `2025-12-04-e2e-speakerless-notes-25/plan.2026-02-02T12-45.md` and update `Last Updated`.
  - Acceptance: The plan file shows updated checkboxes and a refreshed `Last Updated` timestamp.
- [ ] [P8-T12] Reconcile checklist status in `2025-12-04-notes-regressions-26/plan.2026-02-02T13-09.md` and update `Last Updated`.
  - Acceptance: The plan file shows updated checkboxes and a refreshed `Last Updated` timestamp.
- [ ] [P8-T13] Reconcile checklist status in `2025-12-04-formatters-parser-27/plan.2026-02-02T13-08.md` and update `Last Updated`.
  - Acceptance: The plan file shows updated checkboxes and a refreshed `Last Updated` timestamp.
- [ ] [P8-T14] Reconcile checklist status in `2025-12-04-ci-coverage-gate-28/plan.2025-12-04T11-43.md` and update `Last Updated`.
  - Acceptance: The plan file shows updated checkboxes and a refreshed `Last Updated` timestamp.

### Phase 9 — Final QA (Docs + Toolchain)
- [ ] [P9-T1] Verify updated docs contain required headings using a heading check (e.g., `Select-String` for each new section) and record results in “QA Evidence”.
  - Acceptance: “QA Evidence” lists each required heading and confirms presence.
- [ ] [P9-T2] Check for an available Markdown lint tool (e.g., `.markdownlint.*`, `markdownlint` scripts) and run it if present; if not present, record “Markdown lint not available” in “QA Evidence”.
  - Acceptance: “QA Evidence” contains either the lint command output or the “Markdown lint not available” note.
- [ ] [P9-T3] Check for an available link-check tool (repo script or config) and run it if present; if not present, record “Link check not available” in “QA Evidence”.
  - Acceptance: “QA Evidence” contains either the link-check output or the “Link check not available” note.
- [ ] [P9-T4] Run `poetry run black .` and restart the loop from [P9-T4] if files change or the command fails.
  - Acceptance: Command exits with code 0 on a pass where no files are modified.
- [ ] [P9-T5] Run `poetry run ruff check` and restart the loop from [P9-T4] if the command fails.
  - Acceptance: Command exits with code 0.
- [ ] [P9-T6] Run `poetry run pyright` and restart the loop from [P9-T4] if the command fails.
  - Acceptance: Command exits with code 0.
- [ ] [P9-T7] Run `poetry run pytest --cov=src/transcript_etl_pipeline --cov-report=term --cov-report=xml --cov-report=html` and restart the loop from [P9-T4] if the command fails.
  - Acceptance: Command exits with code 0.
