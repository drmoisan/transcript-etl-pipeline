---
applyTo: "**"
---

# **copilot-instructions.md**

## **Purpose of This Document**

You (the agent) are responsible for autonomously developing the **entire transcript ETL pipeline** in this repository.

You must:

1. Follow the technical objectives precisely.
2. Follow the repo’s policy files (link only; do not restate).
3. Produce correct, maintainable, test-covered, tool-compliant code.
4. Implement CLI **and** thin UI functionality.
5. Produce DOCX, RTF, and Markdown outputs correctly formatted.

Your work should be structured, incremental, and fully validated through tests.

---

# **1. Policies — Always Follow These**

When implementing **any** code, tests, or tasks, you must adhere to these repo policies:

* **Coding Standards, Workflow, PR/commit procedures:**
  [code-change.instructions.md](../docs/code-change.instructions.md)

* **Developer Tooling: Poetry, Black, Ruff, Pyright, Pytest, pytest-cov, coverage, pre-commit, VSCode tasks, tools for EXE bundling:**
  [developer-tooling.md](../docs/developer-tooling.md)

* **Unit Test Policy (independence, determinism, clarity, AAA, etc.):**
  [unit-test-policy.md](../docs/unit-test-policy.md)

**Never restate these policies in your code. Follow them directly.**

---

# **2. High-Level Architecture**

Create a modular, testable architecture:

```
src/
  transcript_etl_pipeline/
    __init__.py
    cli.py
    ui.py
    config.py

    extract/
      __init__.py
      from_file.py
      from_clipboard.py

    transform/
      __init__.py
      normalize.py
      enhance.py
      paragraphs.py
      speakers.py

    document/
      __init__.py
      model.py          # Represents labels, paragraphs, metadata, etc.
      parser.py         # Parse enhanced text into Document model
      formatting_rules.py

    formatters/
      __init__.py
      docx_formatter.py
      rtf_formatter.py
      md_formatter.py

tests/
  ... (full coverage per policy)
```

---

# **3. Pipeline Requirements**

The pipeline has **three stages**: Extract → Transform → Load.
Implement each stage in its own subpackage.
Each stage must be independently unit-testable.
All I/O must be thin wrappers around pure functions.

---

# **4. Extract Stage (Clipboard & File)**

### **4.1 Requirements**

Implement extractors enabling two ingestion sources:

1. **Clipboard Input**

   * Use `tkinter` or a lightweight clipboard helper.
   * Must support Windows reliably.
   * Provide an abstraction layer for testability.
   * Use fallback logic if clipboard is empty.

2. **File Input**

   * Accept text files (.txt, .md) in UTF-8 or UTF-16 automatically detected.
   * Raise helpful error messages on unsupported types.

### **4.2 CLI**

Implement in `cli.py`:

```
--source clipboard | file
--file path-to-file    (required if --source=file)
```

### **4.3 Thin UI**

In `ui.py` (tkinter):

* If the user does not provide CLI flags:

  * Display a small dialog to select:

    * Source: Clipboard / File
    * If File -> File picker dialog
  * Cancel → graceful abort with popup message.

---

# **5. Transform Stage**

The transform stage consists of **Normalize** then **Enhance**.

## **5.1 Normalize Requirements**

Implement in `transform/normalize.py`.

### **Normalization Rules**

1. **Line endings**

   * Convert all line endings to **Windows CRLF** (`\r\n`).

2. **Whitespace cleanup**

   * Remove duplicate spaces.
   * Remove trailing spaces.
   * Collapse multiple blank lines → a single blank line.
   * Remove all-empty lines where they are structurally meaningless.

3. **Label normalization**

   * A “label” is any **1-word capitalized token ending with `:`**.

     * Examples: `John:`, `Manager:`, `Intro:`
   * A label must:

     1. Appear at the **beginning** of a line, and
     2. Be followed by exactly **one space**.
   * If a label appears mid-line:

     * Insert a CRLF before it.
     * Continue processing.

4. **Output**

   * Return a list of normalized text blocks or a structured internal representation (your choice), but it must be consumed by the *Enhance* stage.

---

## **5.2 Enhance Requirements**

### **5.2.0 Speakerless Detection (Entry Point)**

**Before** processing speakers, check if the transcript has speaker labels using `has_speaker_labels()`:

```python
from transcript_etl_pipeline.transform.speakerless import (
    has_speaker_labels,
    assign_speaker_labels,
)

if not has_speaker_labels(normalized_text):
    # Apply speakerless detection - adds generic Speaker A, Speaker B, etc.
    text_with_speakers = assign_speaker_labels(normalized_text, num_speakers)
    speaker_map = {}  # No name resolution for generic speakers
else:
    # Proceed with speaker resolution for transcripts with labels
    text_with_speakers, speaker_map = resolve_speakers(normalized_text, ui_callback)
```

This ensures transcripts without explicit speaker labels are handled correctly by applying NLTK-based speakerless detection before speaker resolution.

**Parameters:**
- `num_speakers`: Optional parameter (default None = auto-detect 2-4 speakers)
- Can be specified via CLI: `--num-speakers 3`

### **5.2.1 Paragraph Detection**

Implement in `transform/paragraphs.py`.

Rules:

* Raw transcripts often have many lines without paragraph breaks.
* Use paragraph detection heuristics:

  * Sentence endings (`.`, `?`, `!`).
  * Major pause indicators (long lines followed by shorter lines).
  * Label boundaries.
  * Metadata termination (first label marks end of metadata block).
* As paragraphs are detected:

  * Insert a CRLF **after** each paragraph.
  * **Never** insert an extra CRLF at the very end of the document.

### **5.2.2 Speaker Handling**

Implement in `transform/speakers.py`.

Speaker label format:

```
Speaker A:
Speaker B:
Speaker C:
Speaker: B
Speaker: C
```

**Rules:**

1. If a line begins with a Speaker label, detect which person it represents.

2. **Determine who "Dan Moisan" is.**

   * If text contains “Dan” as part of a speaker label → **that is NOT me.**
   * Identify my real presence using context:

     * Look for lines that reference me in conversation:

       * “Dan, what do you think?”
       * “As Dan mentioned…”
     * Or by unique phrasing associated with my responses.
   * Once identified, replace that speaker label with:

     ```
     Dan Moisan:
     ```

3. **Other attendees**

   * Attempt auto-detection using:

     * Names found in the metadata.
     * Names referenced in dialogue.
     * Distinct linguistic patterns (optional but helpful).
   * If confidence is low:

     * Trigger UI dialog:

       * Show 2–3 sample utterances for “Speaker B”.
       * Let user map “Speaker B” → person name.
       * Allow Cancel, which yields:

         * Speaker B remains as given.

---

## **5.3 Formatting Rules**

Implement in:

* `document/model.py` (document structure)
* `document/formatting_rules.py` (spacing, fonts)

Formatting must be **identical across DOCX, RTF, and Markdown**, within each format’s natural limits.

### **Rules to Implement**

1. **Single spaced text (1.0 line spacing)**

   * Except where vertical spacing rules override.

2. **Font**

   * 10pt Calibri for main body and labels.
   * Labels are **bold**, followed by normal text.

3. **Metadata block**

   * Located at the top.
   * **Single spaced.**
   * Never treated as a paragraph.
   * Do not add before/after spacing.

4. **"Transcript:" label**

   * Add **12pt space above** it.

5. **Lines beginning with a name label**

   * Add **12pt space above**.

6. **All other paragraphs**

   * Add **6pt space above**.

7. **Paragraph wrapping**

   * If a paragraph spans multiple lines, wrap internally but maintain single spacing.

---

# **6. Load Stage (DOCX, RTF, MD)**

### **6.1 Output Format Selection**

Provide via CLI:

```
--format docx | rtf | md
```

Default = `docx`.

If not provided:

* Thin UI prompts user to pick one.

### **6.2 Document Naming**

Rules:

1. CLI flag:

   ```
   --output-name "custom_name"
   ```

2. If omitted:

   * UI dialog prompts for filename.
   * Cancel → graceful abort.

3. Default auto-generated name:

   ```
   YYYY MM dd <MeetingTitle>.docx|rtf|md
   ```

   Where `<MeetingTitle>` is inferred from:

   * Metadata fields, or
   * First clear topic heading, or
   * A fallback like “Transcript”.

### **6.3 Output Folder**

CLI:

```
--output-folder <path>
```

Rules:

* If invalid path → CLI fails with explanation.
* If not provided → UI folder picker dialog.
* Default = most recent folder used by the app (store in a simple config file under `~/.transcript_etl/last_output_folder.json`).

### **6.4 Formatters**

Implement:

* `formatters/docx_formatter.py` using `python-docx`
* `formatters/rtf_formatter.py` using string-based RTF
* `formatters/md_formatter.py` outputting plain Markdown

Each must:

* Apply all spacing rules.
* Apply proper font and bold styling.
* Respect paragraph model from `document/model.py`.

---

# **6.5 Document Parser**

Implement in `document/parser.py`:

* **Purpose**: Parse enhanced text (post-transform) into the structured `Document` model for formatting
* **Features**:
  * Smart metadata detection (lines before first label)
  * Automatic section type inference
  * Label extraction and paragraph building
  * Line continuation handling (multi-line paragraphs)
* **Benefits**: Bridges transform output to formatter input cleanly

# **6.6 Type Safety Requirements**

* **Pyright strict mode compliance**: All code passes strict type checking
* **Protocol-based design**: Use `Protocol` for extensible interfaces (e.g., `SpeakerResolutionUI`)
* **TYPE_CHECKING patterns**: Handle untyped third-party libraries gracefully
* **Benefits**: Catch errors at development time, improve IDE support, enable refactoring confidence

# **6.7 Error Handling Requirements**

* **Graceful degradation**: Handle tkinter unavailability with clear error messages
* **Encoding detection**: Automatic UTF-8/UTF-16 detection for file input
* **User-facing messages**: All errors provide actionable guidance
* **Benefits**: Smooth user experience across different environments

---

# **7. CLI Specification**

Build a complete CLI in `cli.py`.

Commands:

```
transcript-etl extract [--source clipboard|file] [--file path]
transcript-etl transform [--input path] [--output path]
transcript-etl run [--source ...] [--format ...] [--output-name ...] [--output-folder ...]
```

Or, simpler:

```
transcript-etl run [flags]
```

### **Behavior**

* If `--source`, `--format`, or `--output-name` are missing → launch the thin UI.
* CLI errors must be explicit and actionable.

---

# **8. Tests — Mandatory**

All code must be tested according to:
➜ [`docs/unit-test-policy.md`](docs/unit-test-policy.md)

You must create tests for:

### **Extract**

* Clipboard fallback logic (mocked).
* File encoding detection.
* Error handling.

### **Normalize**

* Line endings.
* Whitespace removal.
* Label normalization logic.
* Mid-line label CRLF insertion.

### **Enhance**

* Paragraph detection heuristics.
* Speaker identification logic.
* Dan Moisan identity logic.
* Auto-detection of attendees.
* UI fallback for unresolved speakers (mock UI).

### **Formatters**

* DOCX paragraph spacing.
* RTF structure correctness.
* Markdown formatting consistency.

### **End-to-end tests**

* An input transcript string → a full DOCX/RTF/MD file matching rules.

---

# **9. Development Expectations**

### **Coding Style**

* Follow repo coding standards:
  [`docs/code-change.instructions.md`](docs/code-change.instructions.md)

### **Tooling**

* Poetry environment must remain clean.
* All output must pass:

  * Black
  * Ruff
  * Pyright
  * Pytest
  * pytest-cov (minimum standard set by policies)

As defined in:
[`docs/developer-tooling.md`](docs/developer-tooling.md)

### **Autonomous Workflows**

You may:

* Create new modules.
* Refactor code.
* Update configuration files.
* Add VSCode tasks if needed.
* Add pre-commit hooks.
* Add missing dependencies to `pyproject.toml`.

But you must comply with policy instructions at all times.

---

# **10. Implementation Strategy For the Agent**

When prompted or operating autonomously:

### **Step 1 — Create data models**

* Build a document model.
* Create simple abstractions first.

### **Step 2 — Implement normalize stage**

* Convert raw text → normalized blocks.
* Add tests immediately.

### **Step 3 — Implement enhance stage**

* Speaker resolver.
* Paragraph detector.
* Name remapping.

### **Step 4 — Implement formatting model**

* Document section classes.
* Spacing rules.

### **Step 5 — Implement formatters**

* DOCX first (primary output).
* Then RTF.
* Then Markdown.

### **Step 6 — Build the CLI**

* Wire extract → transform → load.

### **Step 7 — Add Thin UI**

* Dialogs for:

  * Source selection.
  * Speaker resolution.
  * Output naming.
  * Output folder selection.

### **Step 8 — Ensure full test coverage**

* Write unit tests for each module.
* Write end-to-end tests.

### **Step 9 — Validate against policies**

* Run linting and type checks.
* Run full pytest with coverage.

---

# **The Agent’s Contract**

As the agent:

* **Do not guess.** Follow these instructions exactly.
* **Do not restate the project policies.** Link to them.
* **Do not omit tests.**
* **Do not introduce inconsistent architecture.**
* **Implement the complete ETL pipeline end-to-end.**
* **Maintain a high level of internal documentation and type hints.**

