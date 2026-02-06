# CI Run Evidence (CI workflow)

## Summary
- **Workflow:** CI
- **Run ID:** 21735466091
- **Run URL:** https://github.com/drmoisan/transcript-etl-pipeline/actions/runs/21735466091
- **Branch:** baseline-coverage-#20
- **Commit:** 3f3c973aea9846afd711d5f234e1641c7243f8d2
- **Status:** completed
- **Conclusion:** success
- **Created:** 2026-02-06T01:39:11Z
- **Updated:** 2026-02-06T01:40:41Z

## Artifacts
- coverage-html-report-3.10 (276050 bytes)
  - https://api.github.com/repos/drmoisan/transcript-etl-pipeline/actions/artifacts/5399998631/zip
- coverage-xml-report-3.10 (7432 bytes)
  - https://api.github.com/repos/drmoisan/transcript-etl-pipeline/actions/artifacts/5399998775/zip
- coverage-html-report-3.11 (276050 bytes)
  - https://api.github.com/repos/drmoisan/transcript-etl-pipeline/actions/artifacts/5399998778/zip
- coverage-xml-report-3.11 (7432 bytes)
  - https://api.github.com/repos/drmoisan/transcript-etl-pipeline/actions/artifacts/5399998866/zip
- coverage-html-report-3.12 (276056 bytes)
  - https://api.github.com/repos/drmoisan/transcript-etl-pipeline/actions/artifacts/5399999118/zip
- coverage-xml-report-3.12 (7445 bytes)
  - https://api.github.com/repos/drmoisan/transcript-etl-pipeline/actions/artifacts/5399999265/zip
- coverage-html-report-3.13 (276056 bytes)
  - https://api.github.com/repos/drmoisan/transcript-etl-pipeline/actions/artifacts/5399998175/zip
- coverage-xml-report-3.13 (7446 bytes)
  - https://api.github.com/repos/drmoisan/transcript-etl-pipeline/actions/artifacts/5399998308/zip

## Commands

### Trigger workflow
- **Timestamp:** 2026-02-06T01:39:08Z
- **Command:** `gh workflow run ci.yml --ref baseline-coverage-#20`
- **Exit Code:** 0
- **Output:** `Created workflow_dispatch event for ci.yml at baseline-coverage-#20`

### Run metadata
- **Timestamp:** 2026-02-06T01:41:05Z
- **Command:** `gh api /repos/drmoisan/transcript-etl-pipeline/actions/runs/21735466091 --jq '{id: .id, run_number: .run_number, name: .name, head_branch: .head_branch, head_sha: .head_sha, status: .status, conclusion: .conclusion, url: .html_url, created_at: .created_at, updated_at: .updated_at}'`
- **Exit Code:** 0
- **Output:**
  ```json
  {
    "conclusion": "success",
    "created_at": "2026-02-06T01:39:11Z",
    "head_branch": "baseline-coverage-#20",
    "head_sha": "3f3c973aea9846afd711d5f234e1641c7243f8d2",
    "id": 21735466091,
    "name": "CI",
    "run_number": 4,
    "status": "completed",
    "updated_at": "2026-02-06T01:40:41Z",
    "url": "https://github.com/drmoisan/transcript-etl-pipeline/actions/runs/21735466091"
  }
  ```

### Artifact inventory
- **Timestamp:** 2026-02-06T01:40:55Z
- **Command:** `gh api /repos/drmoisan/transcript-etl-pipeline/actions/runs/21735466091/artifacts --jq '{total: .total_count, artifacts: [.artifacts[] | {name: .name, size_in_bytes: .size_in_bytes, expired: .expired, url: .archive_download_url}]}'`
- **Exit Code:** 0
- **Output:**
  ```json
  {
    "artifacts": [
      {
        "expired": false,
        "name": "coverage-html-report-3.13",
        "size_in_bytes": 276056,
        "url": "https://api.github.com/repos/drmoisan/transcript-etl-pipeline/actions/artifacts/5399998175/zip"
      },
      {
        "expired": false,
        "name": "coverage-xml-report-3.13",
        "size_in_bytes": 7446,
        "url": "https://api.github.com/repos/drmoisan/transcript-etl-pipeline/actions/artifacts/5399998308/zip"
      },
      {
        "expired": false,
        "name": "coverage-html-report-3.10",
        "size_in_bytes": 276050,
        "url": "https://api.github.com/repos/drmoisan/transcript-etl-pipeline/actions/artifacts/5399998631/zip"
      },
      {
        "expired": false,
        "name": "coverage-xml-report-3.10",
        "size_in_bytes": 7432,
        "url": "https://api.github.com/repos/drmoisan/transcript-etl-pipeline/actions/artifacts/5399998775/zip"
      },
      {
        "expired": false,
        "name": "coverage-html-report-3.11",
        "size_in_bytes": 276050,
        "url": "https://api.github.com/repos/drmoisan/transcript-etl-pipeline/actions/artifacts/5399998778/zip"
      },
      {
        "expired": false,
        "name": "coverage-xml-report-3.11",
        "size_in_bytes": 7432,
        "url": "https://api.github.com/repos/drmoisan/transcript-etl-pipeline/actions/artifacts/5399998866/zip"
      },
      {
        "expired": false,
        "name": "coverage-html-report-3.12",
        "size_in_bytes": 276056,
        "url": "https://api.github.com/repos/drmoisan/transcript-etl-pipeline/actions/artifacts/5399999118/zip"
      },
      {
        "expired": false,
        "name": "coverage-xml-report-3.12",
        "size_in_bytes": 7445,
        "url": "https://api.github.com/repos/drmoisan/transcript-etl-pipeline/actions/artifacts/5399999265/zip"
      }
    ],
    "total": 8
  }
  ```
