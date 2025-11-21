"""Enhancement orchestration for transcript transformation.

This module coordinates the paragraph detection and speaker resolution steps.
"""

from transcript_etl_pipeline.transform.paragraphs import detect_paragraphs
from transcript_etl_pipeline.transform.speakers import SpeakerResolutionUI, resolve_speakers


def enhance_text(
    normalized_text: str, ui_callback: SpeakerResolutionUI | None = None
) -> tuple[str, dict[str, str]]:
    """Enhance normalized transcript text.

    Applies paragraph detection and speaker resolution to create a well-formatted
    transcript with resolved speaker names.

    Args:
        normalized_text: Text that has been normalized (CRLF, whitespace, labels)
        ui_callback: Optional UI callback for resolving unknown speakers

    Returns:
        Tuple of (enhanced text with paragraphs and resolved speakers, speaker mapping)
    """
    # Step 1: Resolve speakers first (before paragraph detection might modify structure)
    text_with_speakers, speaker_map = resolve_speakers(normalized_text, ui_callback)

    # Step 2: Detect and format paragraphs
    enhanced_text = detect_paragraphs(text_with_speakers)

    return enhanced_text, speaker_map
