# Issue Update Mirror

Timestamp: 2026-02-04T11-21
IssueNumber: 25
IssueURL: https://github.com/drmoisan/transcript-etl-pipeline/issues/25
FeatureFolder: docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-e2e-speakerless-notes-25/

This file is the **local mirror** for GitHub Issue #25 updates, required even when GitHub access is available.

CapturedVia:
- `gh issue view 25 -R drmoisan/transcript-etl-pipeline --json url,title,updatedAt,body`
- `gh api repos/drmoisan/transcript-etl-pipeline/issues/25/comments`

RemoteVerification:
- GitHub CLI/auth available: Yes
- Comments found: 0

## Exact posted text (machine-preserved)

### Issue JSON (authoritative)

~~~json
{"body":"Scope:\n- CLI-driven runs for speakerless + notes workflows producing DOCX/MD.\n\nGoals:\n- End-to-end tests that assert on outputs and key text markers.\n- Cover at least one speakerless transcript and one notes pipeline case.\n\nAcceptance:\n- Tests run via pytest integration suite and pass reliably.\n- Outputs validated for expected structure/content (no golden DOCX required if impractical; can assert text markers).\n## Scenario Summary (Automated)\n\nSpeakerless CLI coverage:\n- **TestCLISpeakerless3SpeakersDOCX**: 3 tests for 3-speaker scenarios (SpaceX, Meeting, Standup).\n- **TestCLISpeakerless4SpeakersDOCX**: 1 test for a 4-speaker panel discussion.\n- **TestCLISpeakerlessMarkdown**: 2 tests for Markdown output.\n- **TestCLISpeakerlessRTF**: 2 tests for RTF output.\n- **TestCLISpeakerlessAutoDetect**: 1 test for auto-detection without `--num-speakers`.\n- **TestCLIErrorHandling**: 2 tests for missing files and invalid arguments.\n\nNotes CLI coverage:\n- **TestCLINotesOnly**: 3 tests for notes-only documents (DOCX/MD/RTF).\n- **TestCLINotesAndTranscript**: 2 tests for combined notes + transcript workflows.\n- **TestCLIUpdateModeNotes**: 2 tests for adding/replacing notes via `--mode update`.\n- **TestCLIUpdateModeTranscript**: 2 tests for adding/replacing transcript via `--mode update`.\n- **TestCLIUpdateModeDOCX**: 1 test for DOCX document reading/updating.\n- **TestCLINotesErrorHandling**: 2 tests for missing files.\n\n## Coverage Evidence (Automated)\n\n```CLI Coverage\nName                                               Stmts   Miss  Cover\n----------------------------------------------------------------------\nsrc/transcript_etl_pipeline/cli.py                   274     82    70%\nsrc/transcript_etl_pipeline/document/reader.py       206     17    92%\nsrc/transcript_etl_pipeline/extract/from_file.py      28      0   100%\nsrc/transcript_etl_pipeline/transform/notes.py        78      1    99%\n----------------------------------------------------------------------\nTOTAL                                                586    100    83%\n```\n\n**Detailed coverage report**: [remediation-baseline/coverage.2026-02-03T18-30.txt](https://github.com/davidtyrpak/transcript-etl-pipeline/blob/main/docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-e2e-speakerless-notes-25/remediation-baseline/coverage.2026-02-03T18-30.txt)\n\n## Scenario status\n\n✅ **COMPLETE** — All 23 E2E tests implemented and passing. Coverage improvements achieved:\n- cli.py: 11% → 70% (+59pp)\n- document/reader.py: 8% → 92% (+84pp)\n- extract/from_file.py: 14% → 100% (+86pp)\n- transform/notes.py: 14% → 99% (+85pp)\n\nTests cover speakerless transcription (3/4 speakers, auto-detect), notes workflows (notes-only, combined, update-mode), and all three output formats (DOCX/MD/RTF).\n","title":"Add end-to-end tests for speakerless + notes CLI flows","updatedAt":"2026-02-04T12:11:31Z","url":"https://github.com/drmoisan/transcript-etl-pipeline/issues/25"}
~~~

### Comments JSON

~~~json
[]
~~~
