---
applyTo: "**"
---

# **copilot-instructions.md**

## **Purpose of This Document**

This document contains instructions for **future enhancements** to the transcript ETL pipeline.

---

# **1. Policies — Always Follow These**

**CRITICAL**: When implementing **any** code, tests, or tasks, you **must** adhere to these repo policies **without exception**. These are not guidelines—they are requirements.

Read each policy document **thoroughly** before starting work. Implement them **exactly as written**. Do not interpret, modify, or skip any requirements.

* **Coding Standards, Workflow, PR/commit procedures:**
  [code-change.instructions.md](../docs/code-change.instructions.md)
  
  This document defines the complete development workflow including:
  - Pre-implementation requirements (clarify objectives, document plans)
  - Python coding standards (formatting, linting, typing, testing)
  - Design principles (simplicity, reusability, extensibility, separation of concerns)
  - Post-implementation requirements (quality checks, documentation updates)

* **Developer Tooling: Poetry, Black, Ruff, Pyright, Pytest, pytest-cov, coverage, pre-commit, VSCode tasks:**
  [developer-tooling.md](../docs/developer-tooling.md)
  
  This document covers all tooling setup and usage.

* **Unit Test Policy (independence, determinism, clarity, AAA, etc.):**
  [unit-test-policy.md](../docs/unit-test-policy.md)
  
  This document defines mandatory testing standards. Every test must comply.

**Do not guess. Do not omit steps. Do not introduce inconsistencies. Follow the policies exactly.**

---

# **2. Future Enhancement Work**

For detailed status on current development work, see:
- **Current Focus**: [`docs/features/backlog.md`](../docs/features/backlog.md) - Feature backlog and priorities
- **Optional Features**: [`docs/features/ideas/ideas.md`](../docs/features/ideas/ideas.md) - Deferred enhancements for future consideration
