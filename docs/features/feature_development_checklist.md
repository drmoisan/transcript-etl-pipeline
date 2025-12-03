# Feature Development Checklist

Use this checklist for every new feature. It mirrors the workflow documented in the process note.

## Pre-work

- [ ] Capture the idea in `docs/features/backlog.md` or `docs/features/potential/` (use `template.md`).
- [ ] Open a GitHub issue with the feature request template (`GitHub: New Feature Issue` VS Code task uses it).
- [ ] Create a feature branch named `feature/<area>-#<issue>`.

## Planning

- [ ] Copy `docs/features/templates/feature/` to `docs/features/active/<feature-name>/`.
- [ ] Fill out `user-story.md`, `spec.md`, and `plan.md` (include the issue number).
- [ ] Define acceptance criteria and test conditions before coding.
- [ ] Decide on any feature flags or rollout guards.

## Implementation

- [ ] Write/update tests first (unit, integration, CLI examples).
- [ ] Update docs and examples that surface the new behavior.
- [ ] Implement code in small commits that keep tests and linters green.

## Validation

- [ ] `poetry run black --check .`
- [ ] `poetry run ruff check`
- [ ] `poetry run pyright`
- [ ] `poetry run pytest`
- [ ] Run smoke/manual checks if the feature affects UX/output.

## Pull Request and Archive

- [ ] PR title includes the issue number and references the feature folder.
- [ ] PR body summarizes changes, tests run, and breaking changes (if any).
- [ ] After merge, move the feature folder to `docs/features/archive/YYYY-MM-DD-<feature-name>/`.
