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
