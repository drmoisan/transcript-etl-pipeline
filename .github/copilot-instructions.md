---
applyTo: "**"
---

# **copilot-instructions.md**

## **Purpose of This Document**

This document contains instructions for **future enhancements** to the transcript ETL pipeline.

**Note**: The core ETL pipeline (Phases 1-9 + Speakerless Detection) is **fully complete**.
For completed implementation details, see:
- **Completed Instructions**: [`docs/archive/core_etl/core_etl_instructions.md`](../docs/archive/core_etl/core_etl_instructions.md)
- **Completed Status**: [`docs/archive/core_etl/core_etl_status.md`](../docs/archive/core_etl/core_etl_status.md)

---

# **1. Policies — Always Follow These**

When implementing **any** code, tests, or tasks, you must adhere to these repo policies:

* **Coding Standards, Workflow, PR/commit procedures:**
  [code-change.instructions.md](../docs/code-change.instructions.md)

* **Developer Tooling: Poetry, Black, Ruff, Pyright, Pytest, pytest-cov, coverage, pre-commit, VSCode tasks:**
  [developer-tooling.md](../docs/developer-tooling.md)

* **Unit Test Policy (independence, determinism, clarity, AAA, etc.):**
  [unit-test-policy.md](../docs/unit-test-policy.md)

**Never restate these policies in your code. Follow them directly.**

---

# **2. Future Enhancement Work**

## **2.1 Notes Conversion Features** 🟢 PARTIALLY COMPLETE

**Status**: Basic infrastructure implemented, enhancement features remain

**Completed**:
- ✅ `transform/notes.py` - Basic note conversion
- ✅ Notes CLI integration (`--notes-source`, `--notes-file`)
- ✅ Notes update mode (`--mode update`, `--update-action`)

**Remaining Work**:
- [ ] Advanced note formatting features
- [ ] Note categorization and organization
- [ ] Smart note merging algorithms
- [ ] Note conflict resolution
- [ ] Enhanced metadata extraction from notes

**Reference**: See user stories in [`docs/features/notes_feature/notes-feature-user-story.md`](../docs/features/notes_feature/notes-feature-user-story.md)

---

## **2.2 Speaker Logic Enhancement** 🔴 NOT STARTED

**Status**: Infrastructure complete, algorithmic improvements needed

**Work Plan**: [`docs/features/speaker_logic_enhancement/speaker_logic_enhancement.agent.md`](../docs/features/speaker_logic_enhancement/speaker_logic_enhancement.agent.md)

**Goal**: Improve 3+ speaker detection accuracy from current baseline

**Current State**:
- ✅ Basic speakerless detection working (2-speaker scenarios)
- ❌ 3-speaker SpaceX test failing (XFAIL marker)
- ❌ Multi-sentence turn grouping needs improvement
- ❌ Rhetorical question handling not implemented
- ❌ Enhanced acknowledgment patterns missing

**Priorities** (documented in work plan):
1. Multi-sentence turn grouping (0% complete)
2. Addressee detection enhancement (80% complete)
3. Enhanced acknowledgment detection (20% complete)
4. Rhetorical question handling (0% complete)
5. Three-speaker similarity refinement (40% complete)

**Test Target**: Pass `test_3speaker_spacex_discussion.py` (currently XFAIL)

---

## **2.3 Optional Enhancements** 🔵 DEFERRED

These are nice-to-have features for future consideration:

### **2.3.1 Additional Output Formats**
- [ ] PDF generation (via reportlab or similar)
- [ ] HTML output with styling
- [ ] Plain text with formatting markers
- [ ] JSON structured output

### **2.3.2 Advanced Formatting Options**
- [ ] Custom font selection
- [ ] Custom spacing rules
- [ ] Theme/template support
- [ ] Header/footer customization

### **2.3.3 Distribution**
- [ ] EXE bundling for Windows (PyInstaller)
- [ ] macOS app bundle
- [ ] Linux package (DEB/RPM)
- [ ] Standalone binary distribution

### **2.3.4 Performance Optimization**
- [ ] Parallel processing for large transcripts
- [ ] Caching for repeated operations
- [ ] Memory optimization for huge files
- [ ] Streaming processing mode

### **2.3.5 Advanced Features**
- [ ] Multi-language support
- [ ] Audio timestamp integration
- [ ] Sentiment analysis integration
- [ ] Topic extraction and summarization
- [ ] Export to presentation formats (PPTX)

---

# **3. Development Guidelines**

## **3.1 Before Starting Any New Work**

1. Review the relevant work plan document
2. Check [`docs/features/feature_status.md`](../docs/features/feature_status.md) for current priorities
3. Run full test suite to ensure baseline: `pytest --tb=short`
4. Verify quality checks pass:
   - `black --check .`
   - `ruff check`
   - `pyright`

## **3.2 During Development**

1. Follow incremental development approach
2. Write tests alongside code (test-first when possible)
3. Run quality checks frequently
4. Update relevant work plan documents with progress
5. Commit small, logical changes with clear messages

## **3.3 After Completing Work**

1. Run full test suite: `pytest`
2. Run all quality checks: `.\scripts\fix-all.ps1`
3. Update work plan documents with completion status
4. Update [`docs/features/feature_status.md`](../docs/features/feature_status.md)
5. Generate commit context: `.\scripts\collect-commit-context.ps1`

---

# **4. Agent Contract**

As an agent working on this codebase:

* **Do not guess.** Follow these instructions exactly.
* **Do not restate the project policies.** Link to them.
* **Do not omit tests.**
* **Do not introduce inconsistent architecture.**
* **Maintain the high quality bar** established by the core ETL pipeline.
* **Update tracking documents** as you complete work.
* **Preserve type safety** (Pyright strict mode, 0 errors).
* **Maintain test coverage** (core modules >95%).
