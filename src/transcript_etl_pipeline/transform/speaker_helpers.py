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
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from transcript_etl_pipeline.transform.identity_constraints import IdentityConstraint

logger = logging.getLogger(__name__)

# Round-robin assignment thresholds for multi-speaker detection
# When segments/num_speakers falls between these ratios, use round-robin assignment
MIN_ROUND_ROBIN_RATIO = 4
MAX_ROUND_ROBIN_RATIO = 8

__all__ = [
    "ensure_nltk_data",
    "ensure_sentence_tokenizer",
    "tokenize_into_sentences",
    "analyze_pronoun_patterns",
    "detect_dialogue_markers",
    "extract_sentence_features",
    "compute_sentence_similarity",
    "extract_speaker_identities",
    "resolve_speaker_assignments_by_identity",
    "resolve_addresses_other_violations",
    "GREETINGS",
    "ACKNOWLEDGMENTS",
    "TURN_TAKING_CUES",
]

# Common dialogue marker sets - shared between speakerless and speakers modules
GREETINGS = frozenset({"hello", "hi", "hey", "good morning", "good afternoon", "good evening"})
ACKNOWLEDGMENTS = frozenset(
    {
        "yes",
        "no",
        "yeah",
        "yep",
        "nope",
        "okay",
        "ok",
        "sure",
        "right",
        "absolutely",
        "great",
        "perfect",
        "excellent",
        "exactly",
        "true",
        "fair",
        "definitely",
        "certainly",
        "agreed",
        "correct",
        "indeed",
        "interesting",
    }
)
TURN_TAKING_CUES = frozenset({"well", "so", "but", "actually", "anyway", "however", "let's", "now"})

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

    # Normalize curly quotes to straight quotes for better sentence tokenization
    # NLTK handles straight quotes more reliably for sentence boundary detection
    normalized = normalized.replace("\u201c", '"').replace("\u201d", '"')  # "..."
    normalized = normalized.replace("\u2018", "'").replace("\u2019", "'")  # '...'
    normalized = normalized.replace("\u2014", "—")  # em dash

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
    - Acknowledgments (yes, no, yeah, okay, sure, right, exactly, etc.)
    - Exclamations (Ha!, Wow!, Nice!, Cool!)
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
    first_word_clean = first_word.rstrip(".,!?")
    if first_word_clean in ACKNOWLEDGMENTS:
        markers["is_acknowledgment"] = True

    # Check for exclamation acknowledgments (Ha!, Wow!, Nice!, Cool!)
    # These typically indicate a speaker change - someone is reacting
    exclamation_acks = {"ha", "haha", "wow", "nice", "cool", "whoa", "oh", "aha", "ooh"}
    if first_word_clean in exclamation_acks:
        markers["is_acknowledgment"] = True

    # Check for turn-taking cues at start
    if first_word_clean in TURN_TAKING_CUES:
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


def violates_identity_constraints(
    group1_indices: list[int],
    group2_indices: list[int],
    constraints: list["IdentityConstraint"],
) -> bool:
    """Check if merging two sentence groups would violate identity constraints.

    Two groups cannot be merged if they contain sentences with conflicting
    self-identifications (e.g., "I'm Peter Parker" in group1 and
    "I'm Fred Flintstone" in group2).

    Args:
        group1_indices: Sentence indices in first group
        group2_indices: Sentence indices in second group
        constraints: List of identity constraints

    Returns:
        True if merging would violate constraints, False otherwise
    """
    # Extract self-identification constraints from both groups
    group1_identities: set[str] = set()
    group2_identities: set[str] = set()

    for constraint in constraints:
        if constraint.constraint_type == "self_identification":
            if constraint.sentence_idx in group1_indices:
                # Normalize to first name for comparison
                first_name = constraint.name.split()[0]
                group1_identities.add(first_name)
            elif constraint.sentence_idx in group2_indices:
                first_name = constraint.name.split()[0]
                group2_identities.add(first_name)

    # If either group has no identities, no conflict
    if not group1_identities or not group2_identities:
        return False

    # Check if groups have different identities
    # If they do, merging would violate the constraint
    return group1_identities.isdisjoint(group2_identities)


def group_sentences_by_similarity(
    sentences: list[str],
    change_points: list[int],
    num_speakers: int,
    constraints: list["IdentityConstraint"] | None = None,
) -> list[int]:
    """Group sentences into speaker clusters based on similarity.

    Uses a hybrid approach:
    1. Each change point starts a potential new speaker segment
    2. For 3+ speakers with few change points, cycle through speakers
    3. Otherwise, use similarity matching to cluster sentences
    4. Identity constraints prevent merging incompatible speakers

    Args:
        sentences: List of sentences in the transcript
        change_points: Indices where speaker changes were detected
        num_speakers: Number of distinct speakers to assign
        constraints: Optional list of identity constraints to enforce

    Returns:
        List of speaker indices (0 to num_speakers-1) for each sentence
    """
    if not sentences:
        return []

    if num_speakers < 2:
        return [0] * len(sentences)

    # Default to empty constraints if none provided
    if constraints is None:
        constraints = []

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
    # Also use round-robin when segments are roughly divisible by speakers
    # (suggesting a regular turn-taking pattern)
    use_round_robin = (
        len(segments) <= num_speakers
        or len(change_points) <= num_speakers
        or (
            len(segments) >= num_speakers * MIN_ROUND_ROBIN_RATIO
            and len(segments) <= num_speakers * MAX_ROUND_ROBIN_RATIO
        )
    )

    if use_round_robin:
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
        current_segment_indices = list(range(start, end))

        # Compute average similarity to each existing speaker cluster
        best_speaker = -1
        best_score = -1.0

        for speaker_idx in range(num_speakers):
            if not speaker_clusters[speaker_idx]:
                continue

            # Check if merging would violate identity constraints
            if violates_identity_constraints(
                speaker_clusters[speaker_idx], current_segment_indices, constraints
            ):
                # Skip this speaker - merging would violate constraints
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
        # use round-robin to ensure speaker variety.
        # Also prioritize filling empty clusters if we don't have a very strong match.

        # Check if we have empty clusters
        has_empty_clusters = any(not c for c in speaker_clusters)

        # If we have empty clusters and match isn't perfect (>0.9), force use of empty cluster
        if has_empty_clusters and best_score < 0.9:
            best_speaker = -1

        if best_speaker < 0 or best_score > 0.85:
            # Find first empty cluster that doesn't violate constraints
            for speaker_idx in range(num_speakers):
                if not speaker_clusters[speaker_idx] and not violates_identity_constraints(
                    speaker_clusters[speaker_idx],
                    current_segment_indices,
                    constraints,
                ):
                    best_speaker = speaker_idx
                    break

            if best_speaker < 0:
                # All clusters have sentences - find next speaker that doesn't violate
                prev_speaker = assignments[start - 1] if start > 0 else 0
                for attempt in range(num_speakers):
                    candidate = (prev_speaker + 1 + attempt) % num_speakers
                    if not violates_identity_constraints(
                        speaker_clusters[candidate],
                        current_segment_indices,
                        constraints,
                    ):
                        best_speaker = candidate
                        break
                else:
                    # No valid speaker found (shouldn't happen with proper constraints)
                    # Fall back to round-robin
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


def extract_speaker_identities(sentences: list[str]) -> dict[int, str]:
    """Extract speaker identities from self-identification sentences.

    Detects patterns like:
    - "I'm [Name]"
    - "My name is [Name]"
    - "This is [Name]"

    Args:
        sentences: List of sentences to analyze

    Returns:
        Dictionary mapping sentence index to identified name
    """
    identities: dict[int, str] = {}

    # Patterns for self-identification
    patterns = [
        r"(?:i'm|i am)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        r"my name is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        r"this is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
    ]

    for i, sentence in enumerate(sentences):
        for pattern in patterns:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                name = match.group(1)
                identities[i] = name
                break

    return identities


def resolve_addresses_other_violations(
    sentences: list[str],
    assignments: list[int],
    constraints: list["IdentityConstraint"],
    num_speakers: int,
) -> list[int]:
    """Fix speaker assignments where someone addresses another by name.

    This post-processing step handles "addresses_other" constraints:
    - "Thanks Frank" should NOT be assigned to Frank
    - "Peter, what do you think?" should NOT be assigned to Peter

    Self-identification constraints are already enforced during grouping (Phase 2),
    so this function ONLY handles addresses_other violations.

    Args:
        sentences: List of sentences
        assignments: Speaker assignments from similarity grouping
        constraints: Identity constraints extracted from sentences
        num_speakers: Number of speakers

    Returns:
        Refined speaker assignments with addresses_other violations fixed
    """
    if num_speakers < 3:
        # For 2 speakers, alternation already prevents self-addressing issues
        return assignments

    # Build mapping from self-identification constraints: speaker_idx -> name
    speaker_to_name: dict[int, str] = {}
    for constraint in constraints:
        if constraint.constraint_type == "self_identification":
            speaker_idx = assignments[constraint.sentence_idx]
            first_name = constraint.name.split()[0]
            speaker_to_name[speaker_idx] = first_name

    if not speaker_to_name:
        # No identities established, can't resolve addresses
        return assignments

    # Create reverse mapping: name -> speaker_idx
    name_to_speaker: dict[str, int] = {name: idx for idx, name in speaker_to_name.items()}

    # Start with a copy of assignments
    refined = list(assignments)

    # Track which sentences have been reassigned for follow-through logic
    reassigned_indices: set[int] = set()

    # Find and fix addresses_other violations
    for constraint in constraints:
        if constraint.constraint_type != "addresses_other":
            continue

        sent_idx = constraint.sentence_idx
        addressed_name = constraint.name.split()[0]  # First name only

        # Check if the addressed person is known
        if addressed_name not in name_to_speaker:
            # We don't know who this person is, skip
            logger.debug(
                f"Cannot resolve address constraint for unknown person '{addressed_name}' "
                f"in sentence {sent_idx}"
            )
            continue

        addressed_speaker_idx = name_to_speaker[addressed_name]
        current_speaker_idx = refined[sent_idx]

        # Check for violation: speaker is assigned to the person they're addressing
        if current_speaker_idx == addressed_speaker_idx:
            # Violation detected! Try to find a safe reassignment
            speaker_letter = chr(ord("A") + addressed_speaker_idx)
            logger.debug(
                f"Address violation: sentence {sent_idx} "
                f"('{sentences[sent_idx][:50]}...') "
                f"addresses {addressed_name} but is assigned to Speaker {speaker_letter}"
            )

            # Strategy: Find a different speaker that doesn't violate constraints
            replacement_speaker = _find_safe_replacement_speaker(
                sent_idx,
                addressed_speaker_idx,
                refined,
                constraints,
                speaker_to_name,
                num_speakers,
            )

            if replacement_speaker is not None:
                refined[sent_idx] = replacement_speaker
                reassigned_indices.add(sent_idx)
                old_letter = chr(ord("A") + current_speaker_idx)
                new_letter = chr(ord("A") + replacement_speaker)
                logger.debug(
                    f"Reassigned sentence {sent_idx} "
                    f"from Speaker {old_letter} to Speaker {new_letter}"
                )

                # Follow-through logic: Check if immediately following sentence
                # should also be reassigned to maintain speaker continuity
                # This handles cases like: "Thanks Frank. Fred?" where both
                # sentences are from the same speaker
                next_idx = sent_idx + 1
                if next_idx < len(sentences):
                    next_sent = sentences[next_idx].strip()
                    next_speaker = refined[next_idx]

                    # Check if next sentence is short and likely a continuation
                    # (questions, names, brief acknowledgments)
                    is_short = len(next_sent.split()) <= 3
                    is_question = next_sent.endswith("?")
                    is_name_call = (
                        next_sent.rstrip("?").strip().istitle() and len(next_sent.split()) == 1
                    )

                    # If next sentence was assigned to the addressed speaker
                    # and it's a short continuation, reassign it too
                    if next_speaker == addressed_speaker_idx and (
                        is_short or is_question or is_name_call
                    ):
                        refined[next_idx] = replacement_speaker
                        reassigned_indices.add(next_idx)
                        logger.debug(
                            f"Follow-through: Reassigned sentence {next_idx} "
                            f"('{next_sent}') to Speaker {new_letter} for continuity"
                        )
            else:
                logger.warning(
                    f"Could not resolve address violation in sentence {sent_idx}: "
                    f"no safe speaker available (would create new conflicts)"
                )

    # Additional heuristic: Handle closing/wrap-up statements
    # After the last self-identification, remaining sentences are likely from
    # the meeting organizer (usually the first self-identified speaker)
    if speaker_to_name:
        # Find the last self-identification
        last_self_id_idx = max(
            (c.sentence_idx for c in constraints if c.constraint_type == "self_identification"),
            default=-1,
        )

        logger.debug(f"Last self-identification at sentence {last_self_id_idx}")

        if last_self_id_idx >= 0 and last_self_id_idx < len(sentences) - 1:
            # Find the first speaker who self-identified (likely the meeting organizer)
            first_self_id_speaker = None
            for constraint in constraints:
                if constraint.constraint_type == "self_identification":
                    first_self_id_speaker = refined[constraint.sentence_idx]
                    speaker_letter = chr(ord("A") + first_self_id_speaker)
                    logger.debug(
                        f"First self-identified speaker: Speaker {speaker_letter} "
                        f"({constraint.name})"
                    )
                    break

            if first_self_id_speaker is not None:
                # Check sentences after the last self-identification
                for idx in range(last_self_id_idx + 1, len(sentences)):
                    sent = sentences[idx].strip()

                    # Skip sentences that have addresses_other constraints
                    # These are mid-conversation and not closing statements
                    has_addresses_other = any(
                        c.sentence_idx == idx and c.constraint_type == "addresses_other"
                        for c in constraints
                    )
                    if has_addresses_other:
                        logger.debug(
                            f"Sentence {idx} has addresses_other constraint, "
                            f"skipping closing statement logic"
                        )
                        continue

                    # Check if this is a short acknowledgment or closing statement
                    # (e.g., "Great.", "Thank you both", "Thanks everyone")
                    is_acknowledgment = sent.lower().startswith(
                        ("great", "perfect", "excellent", "wonderful")
                    )
                    is_thanks = "thank" in sent.lower()
                    is_short = len(sent.split()) <= 4

                    logger.debug(
                        f"Sentence {idx} ('{sent}'): "
                        f"ack={is_acknowledgment}, thanks={is_thanks}, short={is_short}"
                    )

                    # If it's a closing/acknowledgment and not assigned to someone with
                    # self-identification, assign it to the first speaker (organizer)
                    current_speaker = refined[idx]
                    if (
                        (is_acknowledgment or is_thanks)
                        and is_short
                        and current_speaker != first_self_id_speaker
                    ):
                        # Reassign to first speaker (organizer)
                        old_letter = chr(ord("A") + current_speaker)
                        new_letter = chr(ord("A") + first_self_id_speaker)
                        refined[idx] = first_self_id_speaker
                        logger.debug(
                            f"Closing statement: Reassigned sentence {idx} "
                            f"('{sent}') from Speaker {old_letter} to Speaker {new_letter} "
                            f"(meeting organizer)"
                        )

    return refined


def _find_safe_replacement_speaker(
    sent_idx: int,
    excluded_speaker: int,
    assignments: list[int],
    constraints: list["IdentityConstraint"],
    speaker_to_name: dict[int, str],
    num_speakers: int,
) -> int | None:
    """Find a speaker to reassign a sentence to without creating new violations.

    Args:
        sent_idx: Index of sentence to reassign
        excluded_speaker: Speaker that cannot be assigned (violation would remain)
        assignments: Current speaker assignments
        constraints: All identity constraints
        speaker_to_name: Mapping of speaker index to their name
        num_speakers: Number of speakers

    Returns:
        A safe speaker index to assign, or None if no safe option exists
    """
    # Get constraints for this specific sentence
    sentence_constraints = [c for c in constraints if c.sentence_idx == sent_idx]

    # Get all names addressed in this sentence
    addressed_names = {
        c.name.split()[0] for c in sentence_constraints if c.constraint_type == "addresses_other"
    }

    # Build set of speakers that cannot be assigned
    excluded_speakers = {excluded_speaker}
    name_to_speaker: dict[str, int] = {name: idx for idx, name in speaker_to_name.items()}
    for name in addressed_names:
        if name in name_to_speaker:
            excluded_speakers.add(name_to_speaker[name])

    # Try adjacent context first (more natural flow)
    # Check previous sentence's speaker
    if sent_idx > 0:
        prev_speaker = assignments[sent_idx - 1]
        if prev_speaker not in excluded_speakers:
            return prev_speaker

    # Check next sentence's speaker
    if sent_idx < len(assignments) - 1:
        next_speaker = assignments[sent_idx + 1]
        if next_speaker not in excluded_speakers:
            return next_speaker

    # Fallback: find any non-excluded speaker
    for candidate in range(num_speakers):
        if candidate not in excluded_speakers:
            return candidate

    # No safe option found
    return None


def resolve_speaker_assignments_by_identity(
    sentences: list[str],
    assignments: list[int],
    num_speakers: int,
) -> list[int]:
    """Refine speaker assignments using name-based identity resolution.

    NOTE: This function is DEPRECATED in favor of the two-phase approach:
    - Phase 2: Self-identification constraints enforced during grouping
    - Phase 3: Address violations fixed via resolve_addresses_other_violations()

    This function is kept for backward compatibility but delegates to the new API.

    Args:
        sentences: List of sentences
        assignments: Initial speaker assignments (0 to num_speakers-1)
        num_speakers: Number of speakers

    Returns:
        Refined speaker assignments
    """
    if num_speakers < 3:
        # Identity resolution is most valuable for 3+ speakers
        return assignments

    # Import here to avoid circular imports
    from transcript_etl_pipeline.transform.identity_constraints import (
        extract_identity_constraints,
    )

    constraints = extract_identity_constraints(sentences)

    if not constraints:
        return assignments

    return resolve_addresses_other_violations(sentences, assignments, constraints, num_speakers)
