Timestamp: 2026-02-07T23-45
Command: gh api "repos/drmoisan/transcript-etl-pipeline/branches/master/protection"
EXIT_CODE: 1

Output:
~~~
{
  "message": "Branch not protected",
  "documentation_url": "https://docs.github.com/rest/branches/branch-protection#
get-branch-protection",
  "status": "404"
}

gh: Branch not protected (HTTP 404)
~~~

---

Timestamp: 2026-02-07T23-55
Command: gh api "repos/drmoisan/transcript-etl-pipeline/rulesets/12566949"
EXIT_CODE: 0

Output:
~~~
{
  "id": 12566949,
  "name": "Master",
  "target": "branch",
  "source_type": "Repository",
  "source": "drmoisan/transcript-etl-pipeline",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "exclude": [],
      "include": [
        "refs/heads/master"
      ]
    }
  },
  "rules": [
    {
      "type": "deletion"
    },
    {
      "type": "non_fast_forward"
    },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": false,
        "required_reviewers": [],
        "require_code_owner_review": true,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false,
        "allowed_merge_methods": [
          "merge",
          "squash",
          "rebase"
        ]
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "do_not_enforce_on_create": false,
        "required_status_checks": [
          {
            "context": "quality-checks (3.10)",
            "integration_id": 15368
          },
          {
            "context": "quality-checks (3.11)",
            "integration_id": 15368
          },
          {
            "context": "quality-checks (3.12)",
            "integration_id": 15368
          },
          {
            "context": "quality-checks (3.13)",
            "integration_id": 15368
          },
          {
            "context": "Security Scanning",
            "integration_id": 15368
          },
          {
            "context": "Documentation Validation",
            "integration_id": 15368
          },
          {
            "context": "Build Package",
            "integration_id": 15368
          }
        ]
      }
    }
  ],
  "node_id": "RRS_lACqUmVwb3NpdG9yec5Bn5DtzgC_waU",
  "created_at": "2026-02-07T20:44:46.816-05:00",
  "updated_at": "2026-02-07T21:41:43.180-05:00",
  "bypass_actors": [],
  "current_user_can_bypass": "never",
  "_links": {
    "self": {
      "href": "https://api.github.com/repos/drmoisan/transcript-etl-pipeline/rul
esets/12566949"
    },
    "html": {
      "href": "https://github.com/drmoisan/transcript-etl-pipeline/rules/1256694
9"
    }
  }
}
~~~

---

Timestamp: 2026-02-08T00-03
Command: gh ruleset check --default
EXIT_CODE: 0

Output:
~~~
4 rules apply to branch master in repo drmoisan/transcript-etl-pipeline

- deletion
  (configured in ruleset 12566949 from repository drmoisan/transcript-etl-pipeline)
- non_fast_forward
  (configured in ruleset 12566949 from repository drmoisan/transcript-etl-pipeline)
- pull_request: [allowed_merge_methods: [merge squash rebase]] [dismiss_stale_reviews_on_push: false] [require_code_owner_review: true] [require_last_push_approval: false] [required_approving_review_count: 0] [required_review_thread_resolution: false] [required_reviewers: []]
  (configured in ruleset 12566949 from repository drmoisan/transcript-etl-pipeline)
- required_status_checks: [do_not_enforce_on_create: false] [required_status_checks: [map[context:quality-checks (3.10) integration_id:15368] map[context:quality-checks (3.11) integration_id:15368] map[context:quality-checks (3.12) integration_id:15368] map[context:quality-checks (3.13) integration_id:15368] map[context:Security Scanning integration_id:15368] map[context:Documentation Validation integration_id:15368] map[context:Build Package integration_id:15368]]] [strict_required_status_checks_policy: true]
  (configured in ruleset 12566949 from repository drmoisan/transcript-etl-pipeline)
~~~

---

Timestamp: 2026-02-07T23-59
Command: gh api "repos/drmoisan/transcript-etl-pipeline/rulesets/12566949/evaluations"
EXIT_CODE: 1

Output:
~~~
{
  "message": "Not Found",
  "documentation_url": "https://docs.github.com/rest",
  "status": "404"
}

gh: Not Found (HTTP 404)
~~~

---

Timestamp: 2026-02-07T23-59
Command: gh api "repos/drmoisan/transcript-etl-pipeline/rulesets/12566949"
EXIT_CODE: 0

Output:
~~~
{
  "id": 12566949,
  "name": "Master",
  "target": "branch",
  "source_type": "Repository",
  "source": "drmoisan/transcript-etl-pipeline",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "exclude": [],
      "include": [
        "refs/heads/master"
      ]
    }
  },
  "rules": [
    {
      "type": "deletion"
    },
    {
      "type": "non_fast_forward"
    },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": false,
        "required_reviewers": [],
        "require_code_owner_review": true,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false,
        "allowed_merge_methods": [
          "merge",
          "squash",
          "rebase"
        ]
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "do_not_enforce_on_create": false,
        "required_status_checks": [
          {
            "context": "quality-checks (3.10)",
            "integration_id": 15368
          },
          {
            "context": "quality-checks (3.11)",
            "integration_id": 15368
          },
          {
            "context": "quality-checks (3.12)",
            "integration_id": 15368
          },
          {
            "context": "quality-checks (3.13)",
            "integration_id": 15368
          },
          {
            "context": "Security Scanning",
            "integration_id": 15368
          },
          {
            "context": "Documentation Validation",
            "integration_id": 15368
          },
          {
            "context": "Build Package",
            "integration_id": 15368
          }
        ]
      }
    }
  ],
  "node_id": "RRS_lACqUmVwb3NpdG9yec5Bn5DtzgC_waU",
  "created_at": "2026-02-07T20:44:46.816-05:00",
  "updated_at": "2026-02-07T21:41:43.180-05:00",
  "bypass_actors": [],
  "current_user_can_bypass": "never",
  "_links": {
    "self": {
      "href": "https://api.github.com/repos/drmoisan/transcript-etl-pipeline/rul
esets/12566949"
    },
    "html": {
      "href": "https://github.com/drmoisan/transcript-etl-pipeline/rules/1256694
9"
    }
  }
}
~~~
