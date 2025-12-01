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

The detection works on both:
- Multi-line text (traditional line-by-line)
- Continuous text blocks (sentence-based detection)
"""

import logging
import re
from typing import Any, cast

logger = logging.getLogger(__name__)

__all__ = [
    "has_speaker_labels",
    "detect_speaker_changes",
    "assign_speaker_labels",
]

# Flag to track if sentence tokenizer is ready
_sent_tokenizer_ready = False


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


def _ensure_nltk_data() -> bool:
    """Ensure required NLTK data packages are available.

    Downloads the following if not already present:
    - punkt or punkt_tab: Sentence tokenization
    - averaged_perceptron_tagger_eng: Part-of-speech tagging

    Returns:
        True if NLTK data is available, False if download failed
    """
    try:
        import nltk  # type: ignore[import-untyped]
    except ImportError:
        logger.warning("NLTK library not available")
        return False

    def resource_available(resource_path: str) -> bool:
        try:
            nltk.data.find(resource_path)  # type: ignore[attr-defined]
            return True
        except LookupError:
            return False

    # Check and download punkt tokenizer
    if not resource_available("tokenizers/punkt_tab") and not resource_available(
        "tokenizers/punkt"
    ):
        try:
            nltk.download("punkt_tab", quiet=True)  # type: ignore[attr-defined]
        except Exception:
            try:
                nltk.download("punkt", quiet=True)  # type: ignore[attr-defined]
            except Exception:
                logger.warning("Could not download punkt tokenizer")
                return False

    # Check and download POS tagger
    if not resource_available("taggers/averaged_perceptron_tagger_eng") and not resource_available(
        "taggers/averaged_perceptron_tagger"
    ):
        try:
            nltk.download("averaged_perceptron_tagger_eng", quiet=True)  # type: ignore[attr-defined]
        except Exception:
            try:
                nltk.download("averaged_perceptron_tagger", quiet=True)  # type: ignore[attr-defined]
            except Exception:
                logger.warning("Could not download POS tagger")
                return False

    return True


def _ensure_sentence_tokenizer() -> None:
    """Ensure the sentence tokenizer is ready for use."""
    global _sent_tokenizer_ready
    if _sent_tokenizer_ready:
        return
    import nltk  # type: ignore[import-untyped]

    nltk_module = cast(Any, nltk)

    try:
        nltk_module.data.find("tokenizers/punkt_tab")
    except LookupError:
        try:
            nltk_module.data.find("tokenizers/punkt")
        except LookupError:
            nltk_module.download("punkt_tab", quiet=True)
    _sent_tokenizer_ready = True


def _tokenize_into_sentences(text: str) -> list[str]:
    """Split text into sentences using NLTK sentence tokenizer.

    This handles both multi-line text and continuous text blocks.

    Args:
        text: The text to tokenize

    Returns:
        List of sentences
    """
    if not text or not text.strip():
        return []

    try:
        from nltk.tokenize import sent_tokenize  # type: ignore[import-untyped]
    except ImportError:
        logger.warning("NLTK not available for sentence tokenization")
        # Fallback: split on common sentence terminators
        return _fallback_sentence_split(text)

    _ensure_sentence_tokenizer()

    # Normalize the text - replace line breaks with spaces
    normalized = text.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
    # Collapse multiple spaces
    normalized = re.sub(r"\s+", " ", normalized).strip()

    try:
        sentences = sent_tokenize(normalized)
        return [s.strip() for s in sentences if s.strip()]
    except Exception as e:
        logger.warning(f"Sentence tokenization failed: {e}")
        return _fallback_sentence_split(text)


def _fallback_sentence_split(text: str) -> list[str]:
    """Fallback sentence splitting when NLTK is not available.

    Uses regex to split on common sentence terminators.

    Args:
        text: The text to split

    Returns:
        List of sentences
    """
    # Normalize line endings
    normalized = text.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
    normalized = re.sub(r"\s+", " ", normalized).strip()

    # Split on sentence terminators followed by space and capital letter
    # This is a simple heuristic that works for most cases
    pattern = r"(?<=[.!?])\s+(?=[A-Z])"
    sentences = re.split(pattern, normalized)
    return [s.strip() for s in sentences if s.strip()]


def _analyze_pronoun_patterns(sentences: list[str]) -> list[dict[str, int]]:
    """Analyze pronoun usage patterns in sentences using NLTK POS tagging.

    Tracks:
    - First-person pronouns (I, me, my, we, us, our)
    - Second-person pronouns (you, your)
    - Question indicators

    Args:
        sentences: List of sentences to analyze

    Returns:
        List of dictionaries with pronoun counts per sentence
    """
    try:
        from nltk import pos_tag, word_tokenize  # type: ignore[import-untyped]
    except ImportError:
        logger.warning("NLTK not available for pronoun analysis")
        return [{} for _ in sentences]

    # Ensure NLTK data is available
    if not _ensure_nltk_data():
        return [{} for _ in sentences]

    first_person = {"i", "me", "my", "mine", "myself", "we", "us", "our", "ours", "ourselves"}
    second_person = {"you", "your", "yours", "yourself", "yourselves"}

    results: list[dict[str, int]] = []
    for sentence in sentences:
        try:
            tokens = word_tokenize(sentence.lower())
            tagged: list[tuple[str, str]] = pos_tag(tokens)  # type: ignore[assignment]

            counts = {
                "first_person": 0,
                "second_person": 0,
                "is_question": 0,
            }

            for token, _tag in tagged:
                token_str: str = str(token)
                if token_str in first_person:
                    counts["first_person"] += 1
                elif token_str in second_person:
                    counts["second_person"] += 1

            # Check if sentence ends with question mark
            if sentence.strip().endswith("?"):
                counts["is_question"] = 1

            results.append(counts)
        except Exception as e:
            logger.debug(f"Error analyzing sentence: {e}")
            results.append({})

    return results


def _detect_dialogue_markers(sentence: str) -> dict[str, bool]:
    """Detect dialogue markers that may indicate speaker changes.

    Markers include:
    - Greetings (hello, hi, hey)
    - Acknowledgments (yes, no, yeah, okay, sure, right)
    - Turn-taking cues (well, so, but, actually)
    - Response patterns (I think, I believe, I agree)

    Args:
        sentence: The sentence to analyze

    Returns:
        Dictionary of detected markers
    """
    sentence_lower = sentence.lower().strip()

    greetings = {"hello", "hi", "hey", "good morning", "good afternoon", "good evening"}
    acknowledgments = {"yes", "no", "yeah", "yep", "nope", "okay", "ok", "sure", "right"}
    turn_taking = {"well", "so", "but", "actually", "anyway", "however"}
    response_patterns = [
        r"^i think\b",
        r"^i believe\b",
        r"^i agree\b",
        r"^i disagree\b",
        r"^i would\b",
        r"^i don't\b",
        r"^that's\b",
        r"^it's\b",
    ]

    markers = {
        "is_greeting": False,
        "is_acknowledgment": False,
        "is_turn_taking": False,
        "is_response": False,
    }

    # Check for greetings
    for greeting in greetings:
        if sentence_lower.startswith(greeting):
            markers["is_greeting"] = True
            break

    # Check for acknowledgments at start
    first_word = sentence_lower.split()[0] if sentence_lower.split() else ""
    first_word = first_word.rstrip(".,!?")
    if first_word in acknowledgments:
        markers["is_acknowledgment"] = True

    # Check for turn-taking cues at start
    if first_word in turn_taking:
        markers["is_turn_taking"] = True

    # Check for response patterns
    for pattern in response_patterns:
        if re.match(pattern, sentence_lower):
            markers["is_response"] = True
            break

    return markers


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
    sentences = _tokenize_into_sentences(text)

    if len(sentences) < 2:
        return [0] if sentences else []

    # First sentence is always a speaker change (speaker 0 starts)
    change_points = [0]

    # Analyze pronoun patterns for all sentences
    pronoun_patterns = _analyze_pronoun_patterns(sentences)

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
        markers = _detect_dialogue_markers(sentence)
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

    Works on both multi-line text and continuous text blocks.

    Args:
        text: The transcript text without speaker labels
        num_speakers: Optional hint for the number of distinct speakers.
                     If None, automatically detected from change patterns.

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
    sentences = _tokenize_into_sentences(text)

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

    # Generate speaker labels
    speaker_labels = [chr(ord("A") + i) for i in range(num_speakers)]

    # Build result with speaker labels
    result_lines: list[str] = []
    current_speaker_idx = 0
    change_set = set(change_points)

    for i, sentence in enumerate(sentences):
        if i in change_set and i > 0:
            # Speaker change detected
            current_speaker_idx = (current_speaker_idx + 1) % num_speakers

        # Add speaker label to the sentence
        speaker_label = f"Speaker {speaker_labels[current_speaker_idx]}"
        result_lines.append(f"{speaker_label}: {sentence.strip()}")

    # Convert to CRLF for consistency with rest of pipeline
    return "\r\n".join(result_lines)
