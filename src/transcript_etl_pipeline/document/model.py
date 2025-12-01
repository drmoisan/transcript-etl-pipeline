"""Document model for transcript structure.

This module defines the core data structures for representing a formatted transcript
document, including metadata, labels, paragraphs, and their organization.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SectionType(Enum):
    """Type of document section for applying formatting rules."""

    METADATA = "metadata"  # Top section with meeting info
    NOTES_HEADER = "notes_header"  # Notes section header (e.g., "# Notes – 2025-01-01")
    NOTES_BODY = "notes_body"  # Notes content (may contain bullets)
    TRANSCRIPT_LABEL = "transcript_label"  # The "Transcript:" label
    SPEAKER_PARAGRAPH = "speaker_paragraph"  # Paragraph starting with speaker label
    REGULAR_PARAGRAPH = "regular_paragraph"  # Other paragraphs


@dataclass(frozen=True)
class Label:
    """A label is a single-word capitalized token ending with colon.

    Examples: "John:", "Manager:", "Transcript:"
    """

    text: str  # The label text including the colon
    is_speaker: bool = False  # True if this is a speaker label

    def __post_init__(self) -> None:
        """Validate label format."""
        if not self.text.endswith(":"):
            raise ValueError(f"Label must end with colon: {self.text}")
        if not self.text[:-1].strip():
            raise ValueError("Label cannot be empty before colon")


@dataclass
class Paragraph:
    """Represents a single paragraph in the document.

    A paragraph may start with a label followed by text, or just contain text.
    """

    label: Label | None = None
    text: str = ""
    section_type: SectionType = SectionType.REGULAR_PARAGRAPH
    is_bullet: bool = False  # True if this paragraph is a bullet point (for notes)

    def full_text(self) -> str:
        """Return the complete paragraph text including label if present."""
        if self.label:
            return f"{self.label.text} {self.text}".strip()
        return self.text.strip()

    def has_speaker_label(self) -> bool:
        """Check if this paragraph begins with a speaker label."""
        return self.label is not None and self.label.is_speaker


@dataclass
class DocumentSection:
    """A logical section of the document containing multiple paragraphs."""

    section_type: SectionType
    paragraphs: list[Paragraph] = field(default_factory=lambda: [])

    def add_paragraph(self, paragraph: Paragraph) -> None:
        """Add a paragraph to this section."""
        self.paragraphs.append(paragraph)


@dataclass
class Document:
    """Complete document representation with metadata and content sections.

    The document is organized into sections:
    - Metadata section (single-spaced, no extra spacing)
    - Notes sections (header + body, appear after metadata, before transcript)
    - Transcript section with labeled paragraphs
    """

    sections: list[DocumentSection] = field(default_factory=lambda: [])
    title: str = ""
    date: str = ""

    def add_section(self, section: DocumentSection) -> None:
        """Add a section to the document."""
        self.sections.append(section)

    def get_metadata_section(self) -> DocumentSection | None:
        """Get the metadata section if it exists."""
        for section in self.sections:
            if section.section_type == SectionType.METADATA:
                return section
        return None

    def all_paragraphs(self) -> list[Paragraph]:
        """Return all paragraphs from all sections in order."""
        result: list[Paragraph] = []
        for section in self.sections:
            result.extend(section.paragraphs)
        return result

    def _is_notes_section(self, section: DocumentSection) -> bool:
        """Check if a section is a notes section (header or body)."""
        return section.section_type in (SectionType.NOTES_HEADER, SectionType.NOTES_BODY)

    def _is_transcript_section(self, section: DocumentSection) -> bool:
        """Check if a section is a transcript section."""
        return section.section_type in (
            SectionType.TRANSCRIPT_LABEL,
            SectionType.SPEAKER_PARAGRAPH,
            SectionType.REGULAR_PARAGRAPH,
        )

    def _get_first_notes_index(self) -> int | None:
        """Get the index of the first notes section, if any."""
        for i, section in enumerate(self.sections):
            if self._is_notes_section(section):
                return i
        return None

    def _get_first_transcript_index(self) -> int | None:
        """Get the index of the first transcript section, if any."""
        for i, section in enumerate(self.sections):
            if self._is_transcript_section(section):
                return i
        return None

    def _get_notes_insert_index(self) -> int:
        """Get the index where new notes should be inserted.

        Notes are inserted after metadata (if present) but before existing notes.
        """
        # Find where metadata ends
        metadata_end = 0
        for i, section in enumerate(self.sections):
            if section.section_type == SectionType.METADATA:
                metadata_end = i + 1
                break

        return metadata_end

    def _get_transcript_insert_index(self) -> int:
        """Get the index where new transcript sections should be inserted.

        Transcript is appended at the end.
        """
        return len(self.sections)

    def _remove_notes_sections(self) -> None:
        """Remove all notes sections from the document."""
        self.sections = [s for s in self.sections if not self._is_notes_section(s)]

    def _remove_transcript_sections(self) -> None:
        """Remove all transcript sections from the document."""
        self.sections = [s for s in self.sections if not self._is_transcript_section(s)]

    def has_notes(self) -> bool:
        """Check if the document has any notes sections."""
        return any(self._is_notes_section(s) for s in self.sections)

    def has_transcript(self) -> bool:
        """Check if the document has any transcript sections."""
        return any(self._is_transcript_section(s) for s in self.sections)

    def merge_notes(self, new_sections: list[DocumentSection], mode: str) -> None:
        """Merge new notes sections into the document.

        Args:
            new_sections: List of notes sections to add (NOTES_HEADER, NOTES_BODY)
            mode: Either "add" or "replace"
                - "add": Insert new notes at the top, above existing notes
                - "replace": Remove all existing notes, then insert new ones

        Raises:
            ValueError: If mode is not "add" or "replace"
        """
        if mode not in ("add", "replace"):
            raise ValueError(f"Invalid mode: {mode}. Must be 'add' or 'replace'.")

        if mode == "replace":
            self._remove_notes_sections()

        # Insert new notes at the correct position (after metadata, before other notes)
        insert_index = self._get_notes_insert_index()
        for i, section in enumerate(new_sections):
            self.sections.insert(insert_index + i, section)

    def merge_transcript(self, new_sections: list[DocumentSection], mode: str) -> None:
        """Merge new transcript sections into the document.

        Args:
            new_sections: List of transcript sections to add
            mode: Either "add" or "replace"
                - "add": Append new transcript at the end
                - "replace": Remove all existing transcript, then append

        Raises:
            ValueError: If mode is not "add" or "replace"
        """
        if mode not in ("add", "replace"):
            raise ValueError(f"Invalid mode: {mode}. Must be 'add' or 'replace'.")

        if mode == "replace":
            self._remove_transcript_sections()

        # Append new transcript sections at the end
        for section in new_sections:
            self.sections.append(section)
