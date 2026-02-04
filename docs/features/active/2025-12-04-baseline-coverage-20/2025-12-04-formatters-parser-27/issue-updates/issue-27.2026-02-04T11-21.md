# Issue Update Mirror

Timestamp: 2026-02-04T11-21
IssueNumber: 27
IssueURL: https://github.com/drmoisan/transcript-etl-pipeline/issues/27
FeatureFolder: docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-formatters-parser-27/

This file is the **local mirror** for GitHub Issue #27 updates, required even when GitHub access is available.

CapturedVia:
- `gh issue view 27 -R drmoisan/transcript-etl-pipeline --json url,title,updatedAt,body`
- `gh api repos/drmoisan/transcript-etl-pipeline/issues/27/comments`

RemoteVerification:
- GitHub CLI/auth available: Yes
- Comments found: 0

## Exact posted text (machine-preserved)

### Issue JSON (authoritative)

~~~json
{"body":"Scope:\n- Modules: formatters (docx_formatter.py, rtf_formatter.py, md_formatter.py) and document/parser.py.\n- Focus on spacing/label rules and round-trip parsing where feasible.\n\nGoals:\n- Unit tests that validate formatting rules and parser behavior on representative samples.\n- Target: >=70% coverage on these modules.\n\nAcceptance:\n- Tests assert on key formatting/spacing rules and parsed structures.\n- Coverage report shows target met for formatters and parser modules.\n\n## Scenario List (Automated)\n\n- DOCX spacing rules set single line spacing with expected before/after points; heading level 3 maps to `Heading 3`.\n- Notes bullets at level 2 map to `List Bullet 2` in DOCX formatting.\n- RTF paragraph rendering wraps speaker labels in bold and escapes body text; newlines are converted to `\\par`.\n- Markdown notes headers insert a blank line and `#` prefix when not first; transcript labels insert a blank line before `**Transcript:**`.\n- Parser preserves inline text after `Transcript:` and treats unlabeled transcript lines as regular paragraphs.\n\n## Coverage Evidence (Automated)\n\nFull coverage report: https://github.com/carpenike/transcript-etl-pipeline/blob/main/docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-formatters-parser-27/remediation-baseline/coverage.2026-02-03T18-30.txt\n\n```Formatters+Parser Coverage\nThe currently activated Python version 3.10.19 is not supported by the project (^3.12).\nTrying to find and use a compatible version. \nUsing python3.14 (3.14.0)\nSkipping virtualenv creation, as specified in config file.\nName                                                       Stmts   Miss  Cover\n------------------------------------------------------------------------------\nsrc/transcript_etl_pipeline/document/parser.py                61      0   100%\nsrc/transcript_etl_pipeline/formatters/docx_formatter.py      57     13    77%\nsrc/transcript_etl_pipeline/formatters/md_formatter.py        44     13    70%\nsrc/transcript_etl_pipeline/formatters/rtf_formatter.py       57     12    79%\n------------------------------------------------------------------------------\nTOTAL                                                        219     38    83%\n```\n\n## QA evidence\n\nAll Python toolchain steps passed:\n- Black: https://github.com/carpenike/transcript-etl-pipeline/blob/main/docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-formatters-parser-27/remediation-baseline/qa-black.2026-02-03T18-30.txt\n- Ruff: https://github.com/carpenike/transcript-etl-pipeline/blob/main/docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-formatters-parser-27/remediation-baseline/qa-ruff.2026-02-03T18-30.txt\n- Pyright: https://github.com/carpenike/transcript-etl-pipeline/blob/main/docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-formatters-parser-27/remediation-baseline/qa-pyright.2026-02-03T18-30.txt\n- Pytest: https://github.com/carpenike/transcript-etl-pipeline/blob/main/docs/features/active/2025-12-04-baseline-coverage-20/2025-12-04-formatters-parser-27/remediation-baseline/qa-pytest.2026-02-03T18-30.txt","title":"Add tests for formatters and document parser","updatedAt":"2026-02-04T12:31:04Z","url":"https://github.com/drmoisan/transcript-etl-pipeline/issues/27"}
~~~

### Comments JSON

~~~json
[]
~~~
