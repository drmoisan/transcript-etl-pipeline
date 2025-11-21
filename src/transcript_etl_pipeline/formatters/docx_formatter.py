"""DOCX formatter for transcript documents.

This module generates Microsoft Word (.docx) files with proper formatting
according to the transcript formatting rules.
"""

from docx import Document as DocxDocument  # type: ignore[import-untyped]
from docx.enum.text import WD_LINE_SPACING  # type: ignore[import-untyped]
from docx.shared import Pt  # type: ignore[import-untyped]

from transcript_etl_pipeline.document.formatting_rules import (
    BODY_FONT,
    LABEL_FONT,
    SPACING_RULES,
)
from transcript_etl_pipeline.document.model import Document, DocumentSection, SectionType


def format_to_docx(doc: Document, output_path: str) -> None:
    """Format transcript document to DOCX file.

    Applies all formatting rules:
    - 10pt Calibri font
    - Bold labels, normal body text
    - Single line spacing (1.0)
    - No extra spacing for metadata
    - 12pt spacing above Transcript: label and speaker paragraphs
    - 6pt spacing above regular paragraphs

    Args:
        doc: The transcript document to format
        output_path: Path where the DOCX file should be saved
    """
    docx_doc = DocxDocument()

    # Process all sections
    for section in doc.sections:
        _format_section(docx_doc, section)

    # Save the document
    docx_doc.save(output_path)


def _format_section(docx_doc: DocxDocument, section: DocumentSection) -> None:
    """Format a document section.

    Args:
        docx_doc: The python-docx Document object
        section: The transcript section to format
    """
    for paragraph in section.paragraphs:
        _format_paragraph(docx_doc, paragraph, section.section_type)


def _format_paragraph(docx_doc: DocxDocument, paragraph, section_type: SectionType) -> None:
    """Format a single paragraph.

    Args:
        docx_doc: The python-docx Document object
        paragraph: The paragraph to format
        section_type: The type of section this paragraph belongs to
    """
    # Create a new paragraph in the document
    docx_paragraph = docx_doc.add_paragraph()

    # Get spacing based on section type
    spacing = SPACING_RULES[section_type]
    _apply_spacing(docx_paragraph, spacing)

    # Add label if present (bold)
    if paragraph.label:
        run = docx_paragraph.add_run(f"{paragraph.label.text} ")
        _apply_font(run, LABEL_FONT)

    # Add body text (normal)
    if paragraph.text:
        run = docx_paragraph.add_run(paragraph.text)
        _apply_font(run, BODY_FONT)


def _apply_spacing(
    docx_paragraph: DocxDocument.Paragraph,  # type: ignore[name-defined]
    spacing,
) -> None:
    """Apply spacing rules to a paragraph.

    Args:
        docx_paragraph: The python-docx Paragraph object
        spacing: The spacing rule to apply
    """
    # Set line spacing to 1.0 (single spacing)
    docx_paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE

    # Set before spacing
    if spacing.before_pt > 0:
        docx_paragraph.paragraph_format.space_before = Pt(spacing.before_pt)
    else:
        docx_paragraph.paragraph_format.space_before = Pt(0)

    # Set after spacing
    if spacing.after_pt > 0:
        docx_paragraph.paragraph_format.space_after = Pt(spacing.after_pt)
    else:
        docx_paragraph.paragraph_format.space_after = Pt(0)


def _apply_font(run: DocxDocument.Run, font_style) -> None:  # type: ignore[name-defined]
    """Apply font styling to a text run.

    Args:
        run: The python-docx Run object
        font_style: The font style to apply
    """
    run.font.name = font_style.name
    run.font.size = Pt(font_style.size_pt)
    run.font.bold = font_style.bold
