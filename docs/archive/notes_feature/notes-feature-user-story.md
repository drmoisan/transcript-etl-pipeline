Here is a clean, developer-ready **user story** (with acceptance criteria) that fully captures the workflow you described. It avoids ambiguity, defines system behaviors, and frames concrete requirements for engineering.

---

# **User Story — Unified Transcript + Notes Processing in Transcript ETL Pipeline**

## **Summary**

As a user who regularly extracts call artifacts from Granola.ai,
I want the ETL pipeline to accept and convert **both transcripts and markdown notes**, either individually or together,
so that I can generate a single consolidated, consistently-formatted document even when these artifacts are available at different times.

---

## **Problem Context**

Today the pipeline focuses exclusively on transcript ingestion and formatting.
However, Granola.ai provides **two separate artifacts** after a meeting:

1. A raw **transcript**
2. A set of **markdown-formatted notes**

These arrive via clipboard copy most of the time, but I may also save them to files and lightly edit them before running the pipeline.

The existing tool cannot process the notes or merge them into an ongoing document.

---

# **User Story**

## **Primary User Goal**

**I want to create or update a consolidated meeting document that contains formatted notes at the top and formatted transcript at the bottom, even if the notes and transcript become available at different times.**

---

# **Detailed Requirements**

## **1. Start-of-Operation State**

When I launch the ETL pipeline, the system must ask:

* **Do you want to:**

  * **Create a new consolidated document**, or
  * **Add to an existing document?**

---

## **2. Creating a New Document**

### **2.1 User chooses “Create New Document”**

The system asks:

**“What content should I include?”**

* **Notes only**
* **Transcript only**
* **Both Notes and Transcript**

### **2.2 Notes**

If the user chooses *Notes*:

* System accepts:

  * Clipboard text **or**
  * User-selected markdown file
* Notes are normalized and converted into the ETL’s standardized notes section.
* Notes always appear **at the top** of the new document.
* If multiple notes sources are imported sequentially:

  * The system must differentiate them using:

    * An explicit user-provided label **OR**
    * A generated label based on conversion timestamp.

### **2.3 Transcript**

If the user chooses *Transcript*:

* System accepts:

  * Clipboard text **or**
  * User-selected transcript file
* Transcript is normalized and appended **at the bottom** of the new document.

### **2.4 Combining Both**

If the user chooses *Both*:

* Notes appear at the top.
* Transcript appears at the bottom.
* They form a single output document in the project's standard output format (likely markdown or docx).

---

## **3. Adding to an Existing Document**

### **3.1 User chooses “Add to Existing Document”**

The system:

1. Prompts for an existing output document.
2. Automatically detects the sections already present:

   * Notes section(s)
   * Transcript section(s)

### **3.2 System asks user how to proceed**

**“Do you want to:**

* **Add notes**
* **Replace notes**
* **Add transcript**
* **Replace transcript”**

(Options disabled automatically if irrelevant — e.g., “Replace transcript” if none exists.)

### **3.3 Adding Notes**

* New notes are added **at the top**, above all previous notes.
* Each block must have a differentiator:

  * A user-provided title (preferred)
  * Or an auto-generated timestamp label

### **3.4 Replacing Notes**

* All previous notes blocks are removed.
* Newly imported notes become the only notes block.

### **3.5 Adding Transcript**

* New transcript is appended to the **bottom** of the document.

### **3.6 Replacing Transcript**

* Existing transcript block(s) are removed.
* Newly imported transcript becomes the only transcript block.

---

# **Functional Requirements (Acceptance Criteria)**

## **AC1 — Ingest Multiple Input Types**

* System can ingest from clipboard or file for both notes and transcript.

## **AC2 — New vs Existing Document Mode**

* User is always asked whether they are creating a new consolidated document or updating an existing one.

## **AC3 — Automatic Content Detection**

* When loading an existing document, the system reliably identifies notes sections and transcript sections.

## **AC4 — Notes Always at Top**

* Whenever notes are added, they appear above any previous notes.

## **AC5 — Transcript Always at Bottom**

* Whenever a transcript is added, it appears below any previous transcript.

## **AC6 — Notes Differentiation**

* If multiple notes blocks exist, the system tags each block using:

  * User-provided label, or
  * Auto-generated timestamp label

## **AC7 — Replace vs Add Behavior**

* “Add” preserves existing content.
* “Replace” removes the relevant section before inserting the new content.

## **AC8 — Idempotent Output Format**

* Output must follow the standard ETL formatting conventions already used in the pipeline.

## **AC9 — Error Handling**

* System produces human-readable errors when:

  * A file is not markdown/transcript text
  * Clipboard is empty
  * The existing document cannot be parsed

---

# **Developer Notes (Engineering Clarifications)**

* Sections should be structured with **well-defined headers**, e.g.:

  * `# Notes – 2025-01-19 14:05`
  * `# Transcript – Part 1`
* The parser must treat these headers as anchors for detection and replacement.
* The merge logic must be deterministic and predictable.
* The implementation should reuse existing normalization logic where possible.
