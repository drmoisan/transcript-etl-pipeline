---
applyTo: "**"
---

# **copilot-instructions.md**

## **Purpose of This Document**

This document contains instructions for **future enhancements** to the transcript ETL pipeline.

---

## 1. Policies - Always Follow These

**CRITICAL**: When implementing **any** code, tests, or tasks, you **must** strictly adhere to these policies **without exception**. These are not guidelines—they are requirements.

Read each policy document **thoroughly** before starting work. Implement them **exactly as written**. Do not interpret, modify, or skip any requirements.

- **Reading order / authority:** General instructions first, then language-specific instructions, then unit-test addenda. developer-tooling.md and CI docs are operational guidance layered underneath.
- **Coding standards & workflow:** [general-code-change.instructions.md](./instructions/general-code-change.instructions.md)
- **Language-specific coding:** [python-code-change.instructions.md](./instructions/python-code-change.instructions.md)
- **Unit test policy (general):** [general-unit-test.instructions.md](./instructions/general-unit-test.instructions.md)
- **Unit test policy (Python):** [python-unit-test.instructions.md](./instructions/python-unit-test.instructions.md)

* **Developer Tooling: Poetry, Black, Ruff, Pyright, Pytest, pytest-cov, coverage, pre-commit, VSCode tasks:**
  [developer-tooling.md](../docs/developer-tooling.md)
  
  This document covers all tooling setup and usage.

**Do not guess. Do not omit steps. Do not introduce inconsistencies. Follow the policies exactly.**

---

## 2. Future Enhancement Work

- Current backlog and priorities: [/docs/features/backlog.md](../docs/features/backlog.md)
- Active initiatives: [/docs/features/active/](../docs/features/active/) 
- Idea parking lot: [/docs/features/ideas/ideas.md](../docs/features/ideas/ideas.md)

Use these sources to align scope, status, and acceptance criteria before starting changes.

## 3. Operational Reminders

- Architecture/behavior reference: see [README.md](../README.md).
- Secrets: never commit keys
