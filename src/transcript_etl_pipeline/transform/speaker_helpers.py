"""Shared helper functions for speaker detection and analysis.

This module provides common utilities used by both:
- speakerless.py: For detecting speaker changes in unlabeled transcripts
- speakers.py: For resolving speaker labels to actual names

NLTK tools used:
- POS tagging for pronoun analysis
- Word tokenization for lexical analysis
- Frequency distributions for style comparison
"""

import logging
import re
from typing import Any, cast

logger = logging.getLogger(__name__)

__all__ = [
    "ensure_nltk_data",
    "ensure_sentence_tokenizer",
    "tokenize_into_sentences",
    "analyze_pronoun_patterns",
    "detect_dialogue_markers",
    "extract_sentence_features",
    "compute_sentence_similarity",
    "GREETINGS",
    "ACKNOWLEDGMENTS",
    "TURN_TAKING_CUES",
]

# Common dialogue marker sets - shared between speakerless and speakers modules
GREETINGS = frozenset({"hello", "hi", "hey", "good morning", "good afternoon", "good evening"})
ACKNOWLEDGMENTS = frozenset(
    {"yes", "no", "yeah", "yep", "nope", "okay", "ok", "sure", "right", "absolutely"}
)
TURN_TAKING_CUES = frozenset({"well", "so", "but", "actually", "anyway", "however"})

# Pronoun sets for analysis
FIRST_PERSON_PRONOUNS = frozenset(
    {"i", "me", "my", "mine", "myself", "we", "us", "our", "ours", "ourselves"}
)
SECOND_PERSON_PRONOUNS = frozenset({"you", "your", "yours", "yourself", "yourselves"})

# Response patterns that indicate a reply to previous speaker
RESPONSE_PATTERNS = [
    r"^i think\b",
    r"^i believe\b",
    r"^i agree\b",
    r"^i disagree\b",
    r"^i would\b",
    r"^i don't\b",
    r"^that's\b",
    r"^it's\b",
]

# Flag to track if sentence tokenizer is ready
_sent_tokenizer_ready = False


def ensure_nltk_data() -> bool:
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


def ensure_sentence_tokenizer() -> None:
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


def tokenize_into_sentences(text: str) -> list[str]:
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
        return _fallback_sentence_split(text)

    ensure_sentence_tokenizer()

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
    pattern = r"(?<=[.!?])\s+(?=[A-Z])"
    sentences = re.split(pattern, normalized)
    return [s.strip() for s in sentences if s.strip()]


def analyze_pronoun_patterns(sentences: list[str]) -> list[dict[str, int]]:
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
    if not ensure_nltk_data():
        return [{} for _ in sentences]

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
                if token_str in FIRST_PERSON_PRONOUNS:
                    counts["first_person"] += 1
                elif token_str in SECOND_PERSON_PRONOUNS:
                    counts["second_person"] += 1

            # Check if sentence ends with question mark
            if sentence.strip().endswith("?"):
                counts["is_question"] = 1

            results.append(counts)
        except Exception as e:
            logger.debug(f"Error analyzing sentence: {e}")
            results.append({})

    return results


def detect_dialogue_markers(sentence: str) -> dict[str, bool]:
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

    markers = {
        "is_greeting": False,
        "is_acknowledgment": False,
        "is_turn_taking": False,
        "is_response": False,
    }

    # Check for greetings
    for greeting in GREETINGS:
        if sentence_lower.startswith(greeting):
            markers["is_greeting"] = True
            break

    # Check for acknowledgments at start
    first_word = sentence_lower.split()[0] if sentence_lower.split() else ""
    first_word = first_word.rstrip(".,!?")
    if first_word in ACKNOWLEDGMENTS:
        markers["is_acknowledgment"] = True

    # Check for turn-taking cues at start
    if first_word in TURN_TAKING_CUES:
        markers["is_turn_taking"] = True

    # Check for response patterns
    for pattern in RESPONSE_PATTERNS:
        if re.match(pattern, sentence_lower):
            markers["is_response"] = True
            break

    return markers


def extract_sentence_features(sentence: str) -> dict[str, Any]:
    """Extract linguistic features from a sentence for speaker similarity analysis.

    Features extracted:
    - Word count
    - Character count
    - First-person pronoun count
    - Second-person pronoun count
    - Is question
    - Is exclamation
    - Has greeting
    - Has acknowledgment
    - Average word length

    Args:
        sentence: The sentence to analyze

    Returns:
        Dictionary of extracted features
    """
    sentence_lower = sentence.lower().strip()
    words = sentence_lower.split()

    features: dict[str, Any] = {
        "word_count": len(words),
        "char_count": len(sentence),
        "first_person_count": 0,
        "second_person_count": 0,
        "is_question": sentence.endswith("?"),
        "is_exclamation": sentence.endswith("!"),
        "has_greeting": False,
        "has_acknowledgment": False,
        "avg_word_length": 0.0,
    }

    # Count pronouns
    for word in words:
        word_clean = word.rstrip(".,!?")
        if word_clean in FIRST_PERSON_PRONOUNS:
            features["first_person_count"] += 1
        elif word_clean in SECOND_PERSON_PRONOUNS:
            features["second_person_count"] += 1

    # Check for dialogue markers
    markers = detect_dialogue_markers(sentence)
    features["has_greeting"] = markers["is_greeting"]
    features["has_acknowledgment"] = markers["is_acknowledgment"]

    # Average word length
    if words:
        total_word_length = sum(len(w) for w in words)
        features["avg_word_length"] = total_word_length / len(words)

    return features


def compute_sentence_similarity(features1: dict[str, Any], features2: dict[str, Any]) -> float:
    """Compute similarity score between two sentences based on their features.

    This is a simple similarity metric that compares:
    - Word count similarity
    - Pronoun usage similarity
    - Question/statement similarity

    Args:
        features1: Features of first sentence
        features2: Features of second sentence

    Returns:
        Similarity score between 0.0 (different) and 1.0 (identical)
    """
    score = 0.0
    max_score = 0.0

    # Word count similarity (max 2 points)
    max_score += 2.0
    word_diff = abs(features1.get("word_count", 0) - features2.get("word_count", 0))
    if word_diff == 0:
        score += 2.0
    elif word_diff <= 3:
        score += 1.5
    elif word_diff <= 6:
        score += 1.0
    elif word_diff <= 10:
        score += 0.5

    # Pronoun usage similarity (max 2 points)
    max_score += 2.0
    # Similar first-person usage
    fp1 = features1.get("first_person_count", 0) > 0
    fp2 = features2.get("first_person_count", 0) > 0
    if fp1 == fp2:
        score += 1.0

    # Similar second-person usage
    sp1 = features1.get("second_person_count", 0) > 0
    sp2 = features2.get("second_person_count", 0) > 0
    if sp1 == sp2:
        score += 1.0

    # Question/statement similarity (max 1 point)
    max_score += 1.0
    if features1.get("is_question") == features2.get("is_question"):
        score += 1.0

    # Dialogue marker similarity (max 1 point)
    max_score += 1.0
    if features1.get("has_acknowledgment") == features2.get("has_acknowledgment"):
        score += 0.5
    if features1.get("has_greeting") == features2.get("has_greeting"):
        score += 0.5

    # Normalize to 0-1 range
    return score / max_score if max_score > 0 else 0.0


def group_sentences_by_similarity(
    sentences: list[str],
    change_points: list[int],
    num_speakers: int,
) -> list[int]:
    """Group sentences into speaker clusters based on similarity.

    Uses a hybrid approach:
    1. Each change point starts a potential new speaker segment
    2. For 3+ speakers with few change points, cycle through speakers
    3. Otherwise, use similarity matching to cluster sentences

    Args:
        sentences: List of sentences in the transcript
        change_points: Indices where speaker changes were detected
        num_speakers: Number of distinct speakers to assign

    Returns:
        List of speaker indices (0 to num_speakers-1) for each sentence
    """
    if not sentences:
        return []

    if num_speakers < 2:
        return [0] * len(sentences)

    # Extract features for all sentences
    all_features = [extract_sentence_features(s) for s in sentences]

    # Initialize speaker assignments (-1 = unassigned)
    assignments: list[int] = [-1] * len(sentences)

    # Track sentences assigned to each speaker cluster
    speaker_clusters: list[list[int]] = [[] for _ in range(num_speakers)]

    # Create segments from change points
    segments: list[tuple[int, int]] = []
    for i, start in enumerate(change_points):
        end = change_points[i + 1] if i + 1 < len(change_points) else len(sentences)
        segments.append((start, end))

    # If we have fewer segments than speakers, or very few change points,
    # use round-robin assignment at change points to ensure multiple speakers
    if len(segments) <= num_speakers or len(change_points) <= num_speakers:
        # Simple round-robin: each segment gets a different speaker
        for seg_idx, (start, end) in enumerate(segments):
            speaker_idx = seg_idx % num_speakers
            for idx in range(start, end):
                assignments[idx] = speaker_idx
                speaker_clusters[speaker_idx].append(idx)
        return assignments

    # Assign first segment to speaker 0
    if segments:
        start, end = segments[0]
        for idx in range(start, end):
            assignments[idx] = 0
            speaker_clusters[0].append(idx)

    # Assign remaining segments using similarity matching
    for seg_idx in range(1, len(segments)):
        start, end = segments[seg_idx]

        # Compute average similarity to each existing speaker cluster
        best_speaker = -1
        best_score = -1.0

        for speaker_idx in range(num_speakers):
            if not speaker_clusters[speaker_idx]:
                continue

            # Compute average similarity to this speaker's sentences
            total_sim = 0.0
            count = 0
            for sent_idx in speaker_clusters[speaker_idx]:
                for idx in range(start, end):
                    sim = compute_sentence_similarity(all_features[sent_idx], all_features[idx])
                    total_sim += sim
                    count += 1

            if count > 0:
                avg_sim = total_sim / count
                if avg_sim > best_score:
                    best_score = avg_sim
                    best_speaker = speaker_idx

        # If no good match found or score too high (all similar),
        # use round-robin to ensure speaker variety
        if best_speaker < 0 or best_score > 0.8:
            # Find first empty cluster
            for speaker_idx in range(num_speakers):
                if not speaker_clusters[speaker_idx]:
                    best_speaker = speaker_idx
                    break
            else:
                # All clusters have sentences - cycle to next speaker
                prev_speaker = assignments[start - 1] if start > 0 else 0
                best_speaker = (prev_speaker + 1) % num_speakers

        # Assign this segment to the best speaker
        for idx in range(start, end):
            assignments[idx] = best_speaker
            speaker_clusters[best_speaker].append(idx)

    # Ensure no unassigned sentences remain
    for i, assignment in enumerate(assignments):
        if assignment < 0:
            assignments[i] = 0

    return assignments
