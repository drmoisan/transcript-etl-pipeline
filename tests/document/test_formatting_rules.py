"""Tests for formatting rules."""

from transcript_etl_pipeline.document.formatting_rules import (
    BODY_FONT,
    LABEL_FONT,
    SPACING_RULES,
    FontStyle,
    SpacingRule,
    get_body_font,
    get_label_font,
    get_spacing_for_section,
)
from transcript_etl_pipeline.document.model import SectionType


class TestFontStyle:
    """Tests for FontStyle dataclass."""

    def test_font_style_defaults(self) -> None:
        """Test default font style values."""
        font = FontStyle()
        assert font.name == "Calibri"
        assert font.size_pt == 10.0
        assert font.bold is False

    def test_font_style_custom(self) -> None:
        """Test custom font style."""
        font = FontStyle(name="Arial", size_pt=12.0, bold=True)
        assert font.name == "Arial"
        assert font.size_pt == 12.0
        assert font.bold is True


class TestSpacingRule:
    """Tests for SpacingRule dataclass."""

    def test_spacing_rule_defaults(self) -> None:
        """Test default spacing rule values."""
        rule = SpacingRule()
        assert rule.before_pt == 0.0
        assert rule.after_pt == 0.0
        assert rule.line_spacing == 1.0

    def test_spacing_rule_custom(self) -> None:
        """Test custom spacing rule."""
        rule = SpacingRule(before_pt=12.0, after_pt=6.0, line_spacing=1.5)
        assert rule.before_pt == 12.0
        assert rule.after_pt == 6.0
        assert rule.line_spacing == 1.5


class TestFormattingConstants:
    """Tests for formatting constant definitions."""

    def test_label_font_is_bold(self) -> None:
        """Test that label font is bold Calibri 10pt."""
        assert LABEL_FONT.name == "Calibri"
        assert LABEL_FONT.size_pt == 10.0
        assert LABEL_FONT.bold is True

    def test_body_font_is_normal(self) -> None:
        """Test that body font is normal Calibri 10pt."""
        assert BODY_FONT.name == "Calibri"
        assert BODY_FONT.size_pt == 10.0
        assert BODY_FONT.bold is False

    def test_metadata_spacing_no_extra_space(self) -> None:
        """Test that metadata has no extra spacing."""
        rule = SPACING_RULES[SectionType.METADATA]
        assert rule.before_pt == 0.0
        assert rule.after_pt == 0.0
        assert rule.line_spacing == 1.0

    def test_transcript_label_spacing(self) -> None:
        """Test that Transcript: label has 12pt space above."""
        rule = SPACING_RULES[SectionType.TRANSCRIPT_LABEL]
        assert rule.before_pt == 12.0
        assert rule.after_pt == 0.0
        assert rule.line_spacing == 1.0

    def test_speaker_paragraph_spacing(self) -> None:
        """Test that speaker paragraphs have 12pt space above."""
        rule = SPACING_RULES[SectionType.SPEAKER_PARAGRAPH]
        assert rule.before_pt == 12.0
        assert rule.after_pt == 0.0
        assert rule.line_spacing == 1.0

    def test_regular_paragraph_spacing(self) -> None:
        """Test that regular paragraphs have 6pt space above."""
        rule = SPACING_RULES[SectionType.REGULAR_PARAGRAPH]
        assert rule.before_pt == 6.0
        assert rule.after_pt == 0.0
        assert rule.line_spacing == 1.0


class TestFormattingHelpers:
    """Tests for formatting helper functions."""

    def test_get_spacing_for_metadata(self) -> None:
        """Test getting spacing for metadata section."""
        rule = get_spacing_for_section(SectionType.METADATA)
        assert rule.before_pt == 0.0
        assert rule.line_spacing == 1.0

    def test_get_spacing_for_transcript_label(self) -> None:
        """Test getting spacing for transcript label."""
        rule = get_spacing_for_section(SectionType.TRANSCRIPT_LABEL)
        assert rule.before_pt == 12.0

    def test_get_spacing_for_speaker(self) -> None:
        """Test getting spacing for speaker paragraph."""
        rule = get_spacing_for_section(SectionType.SPEAKER_PARAGRAPH)
        assert rule.before_pt == 12.0

    def test_get_spacing_for_regular(self) -> None:
        """Test getting spacing for regular paragraph."""
        rule = get_spacing_for_section(SectionType.REGULAR_PARAGRAPH)
        assert rule.before_pt == 6.0

    def test_get_label_font(self) -> None:
        """Test getting label font."""
        font = get_label_font()
        assert font.bold is True
        assert font.size_pt == 10.0

    def test_get_body_font(self) -> None:
        """Test getting body font."""
        font = get_body_font()
        assert font.bold is False
        assert font.size_pt == 10.0
