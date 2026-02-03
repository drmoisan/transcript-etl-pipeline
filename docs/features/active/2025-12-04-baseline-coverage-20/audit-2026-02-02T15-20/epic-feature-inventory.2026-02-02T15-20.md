# Epic Feature Inventory — 2025-12-04-baseline-coverage-20

Timestamp: 2026-02-02T15-20

## Inventory

| Feature folder | Issue # | Versions present | Current version | Current plan | Doc completeness (issue/spec/user-story/plan) | Acceptance criteria present? | Dependency declarations present? | Notes / risks / gaps |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `2025-12-04-enhance-tests-21` | 21 | None | Root | `plan.2026-02-02T11-49.md` | Yes / Yes / Yes / Yes | Yes (`issue.md`, `user-story.md`) | No explicit dependencies | Coverage target not met (enhance.py line-rate 0.4615). Plan auto-checked for test additions only. |
| `2025-12-04-speakerless-heuristics-22` | 22 | None | Root | `plan.2026-02-02T12-24.md` | Yes / Yes / Yes / Yes | Yes (`issue.md`, `user-story.md`) | No explicit dependencies | Coverage targets not met (speakerless 0.0625; speaker_helpers 0.07008). NLTK download risk in tests. |
| `2025-12-04-identity-normalize-23` | 23 | None | Root | `plan.2026-02-02T13-08.md` | Yes / Yes / Yes / Yes | Yes (`issue.md`, `user-story.md`) | No explicit dependencies | Coverage targets not met (identity_constraints 0.1852; normalize 0.1702). Plan auto-checked for identity-constraint tests only. |
| `2025-12-04-multi-speaker-fixtures-24` | 24 | None | Root | `plan.2026-02-02T13-09.md` | Yes / Yes / Yes / Yes | Yes (`issue.md`, `user-story.md`) | Soft dependency on #22 fixtures | Fixtures and regression tests exist; plan auto-checked for fixture/test creation. Issue/prompt updates pending. |
| `2025-12-04-e2e-speakerless-notes-25` | 25 | None | Root | `plan.2026-02-02T12-45.md` | Yes / Yes / Yes / Yes | Yes (`issue.md`, `user-story.md`) | Yes (fixtures from #24) | Integration tests exist, but use filesystem tmp_path; unit-test policy conflict. Plan tasks not aligned with implementation. |
| `2025-12-04-notes-regressions-26` | 26 | None | Root | `plan.2026-02-02T13-09.md` | Yes / Yes / Yes / Yes | Yes (`issue.md`, `user-story.md`) | No explicit dependencies | Regression criteria not evidenced; notes coverage low (0.141). |
| `2025-12-04-formatters-parser-27` | 27 | None | Root | `plan.2026-02-02T13-08.md` | Yes / Yes / Yes / Yes | Yes (`issue.md`, `user-story.md`) | No explicit dependencies | Tests exist but use temporary files; coverage targets not met (docx 0.2807, md 0.1136, rtf 0.1228, parser 0.07018). |
| `2025-12-04-ci-coverage-gate-28` | 28 | None | Root | `plan.2025-12-04T11-43.md` | Yes / Yes / Yes / Yes | Yes (`issue.md`, `user-story.md`) | Implicit dependency on baseline coverage stabilization | CI coverage gate implemented (ci.yml + pyproject). Plan auto-checked for config steps. Documentation criterion still pending. |

## Alignment check (per feature)

- **#21 Enhance tests**: MVP-aligned; coverage target unmet.
- **#22 Speakerless heuristics**: MVP-aligned; coverage target unmet and external download risk.
- **#23 Identity + normalize**: MVP-aligned; coverage target unmet.
- **#24 Multi-speaker fixtures**: Post-MVP regression enabler; core fixtures/tests exist.
- **#25 E2E speakerless + notes**: Post-MVP; tests exist but violate temp-file policy.
- **#26 Notes regressions**: Post-MVP; acceptance criteria not evidenced.
- **#27 Formatters + parser**: Post-MVP; tests exist but coverage targets unmet and temp-file policy conflict.
- **#28 CI coverage gate**: Post-MVP; CI gate implemented; documentation and sequencing still pending.

## Summary

- **Ready to execute**: #24 (fixtures/tests delivered), #28 (CI gate delivered) — pending documentation updates.
- **Needs delivery work**: #21, #22, #23, #26, #27 (coverage targets and acceptance criteria unmet).
- **Blocked**: #25 and #27 due to unit-test policy violations (filesystem/temp files).
