"""Formatting rules for document output.

This module defines the precise spacing, font, and styling rules that must be
applied consistently across DOCX, RTF, and Markdown outputs.
"""

from dataclasses import dataclass

from transcript_etl_pipeline.document.model import SectionType


@dataclass(frozen=True)
class FontStyle:
    """Font styling specification."""

    name: str = "Calibri"
    size_pt: float = 10.0
    bold: bool = False


@dataclass(frozen=True)
class SpacingRule:
    """Vertical spacing rules in points."""

    before_pt: float = 0.0
    after_pt: float = 0.0
    line_spacing: float = 1.0  # 1.0 = single spacing


# Font definitions
LABEL_FONT = FontStyle(name="Calibri", size_pt=10.0, bold=True)
BODY_FONT = FontStyle(name="Calibri", size_pt=10.0, bold=False)
NOTES_HEADER_FONT = FontStyle(name="Calibri", size_pt=14.0, bold=True)

# Spacing rules by section type
SPACING_RULES = {
    SectionType.METADATA: SpacingRule(before_pt=0.0, after_pt=0.0, line_spacing=1.0),
    SectionType.NOTES_HEADER: SpacingRule(before_pt=12.0, after_pt=0.0, line_spacing=1.0),
    SectionType.NOTES_BODY: SpacingRule(before_pt=6.0, after_pt=0.0, line_spacing=1.0),
    SectionType.TRANSCRIPT_LABEL: SpacingRule(before_pt=12.0, after_pt=0.0, line_spacing=1.0),
    SectionType.SPEAKER_PARAGRAPH: SpacingRule(before_pt=12.0, after_pt=0.0, line_spacing=1.0),
    SectionType.REGULAR_PARAGRAPH: SpacingRule(before_pt=6.0, after_pt=0.0, line_spacing=1.0),
}


def get_spacing_for_section(section_type: SectionType) -> SpacingRule:
    """Get the appropriate spacing rule for a section type."""
    return SPACING_RULES[section_type]


def get_label_font() -> FontStyle:
    """Get the font style for labels (bold)."""
    return LABEL_FONT


def get_body_font() -> FontStyle:
    """Get the font style for body text (normal)."""
    return BODY_FONT
