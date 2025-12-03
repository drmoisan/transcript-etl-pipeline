"""Enhancement orchestration for transcript transformation.

This module coordinates the paragraph detection and speaker resolution steps.
"""

import logging

from transcript_etl_pipeline.transform.paragraphs import detect_paragraphs
from transcript_etl_pipeline.transform.speakerless import (
    assign_speaker_labels,
    has_speaker_labels,
)
from transcript_etl_pipeline.transform.speakers import SpeakerResolutionUI, resolve_speakers

logger = logging.getLogger(__name__)


def enhance_text(
    normalized_text: str,
    ui_callback: SpeakerResolutionUI | None = None,
    num_speakers: int | None = None,
) -> tuple[str, dict[str, str]]:
    """Enhance normalized transcript text.

    Applies paragraph detection and speaker resolution to create a well-formatted
    transcript with resolved speaker names.

    For transcripts without speaker labels, automatically applies speakerless
    detection to assign generic speaker labels (Speaker A, Speaker B, etc.)

    Args:
        normalized_text: Text that has been normalized (CRLF, whitespace, labels)
        ui_callback: Optional UI callback for resolving unknown speakers
        num_speakers: Optional number of speakers for speakerless detection.
                     If None, auto-detected (2-4 speakers). Only used when
                     transcript has no speaker labels.

    Returns:
        Tuple of (enhanced text with paragraphs and resolved speakers, speaker mapping)
    """
    # Step 0: Check if transcript has speaker labels
    if not has_speaker_labels(normalized_text):
        logger.info("No speaker labels detected, using speakerless detection")
        # Apply speakerless detection to add generic speaker labels
        text_with_speakers = assign_speaker_labels(normalized_text, num_speakers)
        speaker_map = {}  # No name resolution for generic speakers
    else:
        # Step 1: Resolve speakers (transcript already has labels)
        text_with_speakers, speaker_map = resolve_speakers(normalized_text, ui_callback)

    # Step 2: Detect and format paragraphs
    enhanced_text = detect_paragraphs(text_with_speakers)

    return enhanced_text, speaker_map
