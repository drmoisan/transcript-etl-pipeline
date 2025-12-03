---
applyTo: "**"
---

# **copilot-instructions.md**

## **Purpose of This Document**

This document contains instructions for **future enhancements** to the transcript ETL pipeline.

**Note**: The core ETL pipeline (Phases 1-9 + Speakerless Detection) is **fully complete**.
For completed implementation details, see:
- **Completed Instructions**: [docs/archive/core_etl/core_etl_instructions.md](archive/core_etl/core_etl_instructions.md)
- **Completed Status**: [docs/archive/core_etl/core_etl_status.md](archive/core_etl/core_etl_status.md)

---

# **1. Policies — Always Follow These**

**CRITICAL**: When implementing **any** code, tests, or tasks, you **must** adhere to these repo policies **without exception**. These are not guidelines—they are requirements.

Read each policy document **thoroughly** before starting work. Implement them **exactly as written**. Do not interpret, modify, or skip any requirements.

* **Coding Standards, Workflow, PR/commit procedures:**
  [code-change.instructions.md](code-change.instructions.md)
  
  This document defines the complete development workflow including:
  - Pre-implementation requirements (clarify objectives, document plans)
  - Python coding standards (formatting, linting, typing, testing)
  - Design principles (simplicity, reusability, extensibility, separation of concerns)
  - Post-implementation requirements (quality checks, documentation updates)

* **Developer Tooling: Poetry, Black, Ruff, Pyright, Pytest, pytest-cov, coverage, pre-commit, VSCode tasks:**
  [developer-tooling.md](developer-tooling.md)
  
  This document covers all tooling setup and usage.

* **Unit Test Policy (independence, determinism, clarity, AAA, etc.):**
  [unit-test-policy.md](unit-test-policy.md)
  
  This document defines mandatory testing standards. Every test must comply.

**Do not guess. Do not omit steps. Do not introduce inconsistencies. Follow the policies exactly.**

---

# **2. Future Enhancement Work**

For detailed status on current development work, see:
- **Current Focus**: [docs/features/feature_status.md](features/feature_status.md) - Notes enhancement and Speaker Logic improvement
- **Optional Features**: [docs/ideas/potential_features.md](ideas/potential_features.md) - Deferred enhancements for future consideration
