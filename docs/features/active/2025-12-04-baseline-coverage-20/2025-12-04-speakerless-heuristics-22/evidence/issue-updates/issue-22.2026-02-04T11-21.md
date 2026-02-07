# Issue Update Mirror

Timestamp: 2026-02-04T11-21
IssueNumber: 22
IssueURL: https://github.com/drmoisan/transcript-etl-pipeline/issues/22
FeatureFolder: docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-speakerless-heuristics-22/

This file is the **local mirror** for GitHub Issue #22 updates, required even when GitHub access is available.

CapturedVia:
- `gh issue view 22 -R drmoisan/transcript-etl-pipeline --json url,title,updatedAt,body`
- `gh api repos/drmoisan/transcript-etl-pipeline/issues/22/comments`

RemoteVerification:
- GitHub CLI/auth available: Yes
- Comments found: 0

## Exact posted text (machine-preserved)

### Issue JSON (authoritative)

~~~json
{"body":"Scope:\n- Modules: transform/speakerless.py and transform/speaker_helpers.py.\n- Heuristics: rhetorical/tag questions, addressee detection, continuation, clustering helpers.\n\nGoals:\n- Unit tests for core heuristics and helper functions.\n- Target: >=70% coverage on both modules.\n\nAcceptance:\n- Tests cover positive/negative cases for each heuristic.\n- Coverage report shows target met for both modules.\n## Coverage Evidence (Automated)\n\nTests added:\n- `test_detect_speaker_changes_tag_question_includes_change`\n- `test_detect_speaker_changes_continuation_no_shift`\n- `test_assign_speaker_labels_addressee_not_self`\n- `test_assign_speaker_labels_closing_statement_to_organizer`\n- `test_detect_dialogue_markers_right_tag_question_acknowledgment`\n- `test_resolve_addresses_other_follow_through_reassigns`\n- `test_group_sentences_round_robin_two_segments`\n- `test_group_sentences_distinct_self_identifications`\n- `test_first_person_detection`\n\n```Speakerless Coverage\nThe currently activated Python version 3.10.19 is not supported by the project (^3.12).\nTrying to find and use a compatible version. \nUsing python3.14 (3.14.0)\nSkipping virtualenv creation, as specified in config file.\nName                                                       Stmts   Miss  Cover\n------------------------------------------------------------------------------\nsrc/transcript_etl_pipeline/transform/speaker_helpers.py     371     30    92%\nsrc/transcript_etl_pipeline/transform/speakerless.py         144      7    95%\n------------------------------------------------------------------------------\nTOTAL                                                        515     37    93%\n```\n","title":"Add unit tests for speakerless heuristics and helpers","updatedAt":"2026-02-03T13:45:39Z","url":"https://github.com/drmoisan/transcript-etl-pipeline/issues/22"}
~~~

### Comments JSON

~~~json
[]
~~~
