"""Speaker detection for transcripts without explicit speaker labels.

This module provides tools to detect distinct speakers from contextual clues
when no explicit speaker labels (e.g., "Speaker A:", "Speaker B:") are present.

NLTK tools used for speaker detection:
- Sentence tokenization (sent_tokenize) to split continuous text into sentences
- Part-of-speech (POS) tagging to identify pronoun patterns
- Word tokenization for detailed analysis

Detection heuristics (applied at sentence level, not line level):
1. Pronoun shift patterns (I/you exchanges indicate speaker changes)
2. Question-answer patterns (questions often followed by responses from different speaker)
3. Dialogue markers (acknowledgments, greetings, turn-taking cues)
4. Semantic cues (thank you, response patterns)

Speaker assignment modes:
- num_speakers=2: Simple alternating assignment (A→B→A→B...)
- num_speakers≥3: Similarity-based grouping to cluster similar-sounding sentences

The detection works on both:
- Multi-line text (traditional line-by-line)
- Continuous text blocks (sentence-based detection)
"""

import logging
import re

from transcript_etl_pipeline.transform.speaker_helpers import (
    analyze_pronoun_patterns,
    detect_dialogue_markers,
    group_sentences_by_similarity,
    tokenize_into_sentences,
)

logger = logging.getLogger(__name__)

__all__ = [
    "has_speaker_labels",
    "detect_speaker_changes",
    "assign_speaker_labels",
]


def has_speaker_labels(text: str) -> bool:
    """Check if a transcript has explicit speaker labels.

    Detects common speaker label patterns:
    - "Speaker A:", "Speaker B:", etc.
    - "Name:" at the start of lines
    - Numbered speakers like "1:", "2:", etc.

    Args:
        text: The transcript text to analyze

    Returns:
        True if speaker labels are detected, False otherwise
    """
    if not text or not text.strip():
        return False

    lines = text.split("\n")

    # Pattern to match speaker labels at the start of lines
    # Matches: "Speaker A:", "John:", "Speaker 1:", etc.
    speaker_pattern = r"^([A-Z][A-Za-z0-9\s]*?):\s"

    label_count = 0
    for line in lines:
        line = line.strip()
        if re.match(speaker_pattern, line):
            label_count += 1

    # If we find at least 2 speaker labels, consider it labeled
    # Also check if labels make up a reasonable portion of non-empty lines
    non_empty_lines = sum(1 for line in lines if line.strip())
    if non_empty_lines == 0:
        return False

    # At least 2 labels and at least 10% of lines have labels
    return label_count >= 2 and label_count / non_empty_lines >= 0.1


def detect_speaker_changes(text: str) -> list[int]:
    """Detect potential speaker change points in unlabeled text.

    Uses sentence-based analysis to identify where speaker changes likely occur.
    This works on both multi-line text AND continuous text blocks without newlines.

    Heuristics applied at sentence level:
    1. Pronoun shift patterns (I/you exchanges)
    2. Question-answer sequences
    3. Dialogue markers (greetings, acknowledgments)
    4. Thank you / appreciation patterns (often signal speaker change)

    Args:
        text: The transcript text without speaker labels

    Returns:
        List of sentence indices where speaker changes are detected (0-indexed)
    """
    if not text or not text.strip():
        return []

    # Use sentence tokenization to handle continuous text blocks
    sentences = tokenize_into_sentences(text)

    if len(sentences) < 2:
        return [0] if sentences else []

    # First sentence is always a speaker change (speaker 0 starts)
    change_points = [0]

    # Analyze pronoun patterns for all sentences
    pronoun_patterns = analyze_pronoun_patterns(sentences)

    # Track previous sentence characteristics
    prev_is_question = False

    for i in range(1, len(sentences)):
        is_speaker_change = False

        sentence = sentences[i]
        curr_patterns = pronoun_patterns[i] if i < len(pronoun_patterns) else {}
        prev_patterns = pronoun_patterns[i - 1] if i - 1 < len(pronoun_patterns) else {}

        # Heuristic 1: Pronoun shift
        # If previous sentence had "I" and current has "you" or vice versa
        curr_first = curr_patterns.get("first_person", 0)
        curr_second = curr_patterns.get("second_person", 0)
        prev_first = prev_patterns.get("first_person", 0)
        prev_second = prev_patterns.get("second_person", 0)

        if (prev_first > 0 and curr_second > 0) or (prev_second > 0 and curr_first > 0):
            is_speaker_change = True

        # Heuristic 2: Question-answer pattern
        # If previous sentence was a question and current is not
        curr_is_question = curr_patterns.get("is_question", 0) > 0
        if prev_is_question and not curr_is_question:
            is_speaker_change = True

        # Heuristic 3: Dialogue markers
        markers = detect_dialogue_markers(sentence)
        if markers["is_greeting"]:
            is_speaker_change = True
        if markers["is_acknowledgment"]:
            is_speaker_change = True
        if markers["is_response"] and prev_is_question:
            is_speaker_change = True

        # Heuristic 4: Thank you patterns often indicate speaker change
        sentence_lower = sentence.lower().strip()
        if sentence_lower.startswith("thank you") or sentence_lower.startswith("thanks"):
            is_speaker_change = True

        # Heuristic 5: "That's" patterns often respond to previous speaker
        if sentence_lower.startswith("that's "):
            is_speaker_change = True

        # Record change point if detected
        if is_speaker_change:
            change_points.append(i)

        # Update for next iteration
        prev_is_question = curr_is_question

    return change_points


def assign_speaker_labels(text: str, num_speakers: int | None = None) -> str:
    """Assign speaker labels to unlabeled transcript text.

    Uses sentence-based speaker change detection to segment text and assign
    generic speaker labels (Speaker A, Speaker B, etc.).

    Speaker assignment modes:
    - num_speakers=2: Simple alternating assignment (A→B→A→B...)
    - num_speakers≥3: Similarity-based grouping to cluster similar sentences

    Works on both multi-line text and continuous text blocks.

    Args:
        text: The transcript text without speaker labels
        num_speakers: Number of distinct speakers in the transcript.
                     If None, automatically detected from change patterns (default 2-4).
                     Set explicitly when you know the speaker count.

    Returns:
        Text with speaker labels added at detected speaker changes.
        Returns original text if speaker labels already exist.
    """
    if not text or not text.strip():
        return text

    # Check if text already has speaker labels
    if has_speaker_labels(text):
        logger.info("Text already has speaker labels, returning unchanged")
        return text

    # Use sentence tokenization to handle continuous text blocks
    sentences = tokenize_into_sentences(text)

    if not sentences:
        return f"Speaker A: {text.strip()}"

    # Detect speaker changes
    change_points = detect_speaker_changes(text)

    if not change_points:
        # No changes detected, return with single speaker label
        return f"Speaker A: {text.strip()}"

    # Determine number of speakers if not provided
    if num_speakers is None:
        # Use the number of change points as an indicator, capped at 4 speakers
        # Each change point represents a potential speaker switch
        # For simple dialogues, assume 2 speakers; for more complex ones, use detected count
        num_speakers = min(len(change_points), 4)
        if num_speakers < 2:
            num_speakers = 2  # At least 2 speakers for a dialogue

    # Ensure num_speakers is at least 1
    num_speakers = max(1, num_speakers)

    # Generate speaker labels
    speaker_labels = [chr(ord("A") + i) for i in range(num_speakers)]

    # Build result with speaker labels
    result_lines: list[str] = []

    if num_speakers == 2:
        # For 2 speakers, use simple alternating assignment
        current_speaker_idx = 0
        change_set = set(change_points)

        for i, sentence in enumerate(sentences):
            if i in change_set and i > 0:
                # Speaker change detected - switch to other speaker
                current_speaker_idx = (current_speaker_idx + 1) % 2

            # Add speaker label to the sentence
            speaker_label = f"Speaker {speaker_labels[current_speaker_idx]}"
            result_lines.append(f"{speaker_label}: {sentence.strip()}")
    else:
        # For 3+ speakers, use similarity-based grouping
        # This helps cluster similar-sounding sentences to the same speaker
        assignments = group_sentences_by_similarity(sentences, change_points, num_speakers)

        for i, sentence in enumerate(sentences):
            speaker_idx = assignments[i] if i < len(assignments) else 0
            speaker_label = f"Speaker {speaker_labels[speaker_idx]}"
            result_lines.append(f"{speaker_label}: {sentence.strip()}")

    # Convert to CRLF for consistency with rest of pipeline
    return "\r\n".join(result_lines)
