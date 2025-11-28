"""Speaker detection and normalization for transcript text.

This module handles speaker identification, including special logic to identify
Dan Moisan and provide UI fallback for unresolved speakers.
"""

import logging
import re
from typing import Protocol

from english_words import get_english_words_set

from transcript_etl_pipeline.transform.name import Name

logger = logging.getLogger(__name__)

# Load English dictionary once at module level for performance
# Currently unused but available for future dictionary-based checks
_english_words: set[str] | None = None


def _get_english_words() -> set[str]:  # pyright: ignore[reportUnusedFunction]
    """Get English words dictionary, loading it once and caching.

    Returns:
        Set of lowercase English words
    """
    global _english_words
    if _english_words is None:
        _english_words = get_english_words_set(["web2"], lower=True)
    return _english_words


__all__ = [
    "SpeakerResolutionUI",
    "resolve_speakers",
    "_extract_speaker_labels",
    "_identify_speaker_by_name",
    "_identify_dan_moisan",
    "_extract_names_from_metadata",
    "_extract_names_from_dialogue",
    "_extract_speaker_samples",
    "_apply_speaker_mappings",
    "_is_speaker_line",
    "_extract_speaker_from_line",
    "_is_direct_address_to_person",
    "_extract_names_from_line",
    "_apply_proximity_heuristics",
    "_extract_title_case_chains",
    "_is_proper_noun",
    "_is_likely_person_name",
]


class SpeakerResolutionUI(Protocol):
    """Protocol for UI callback to resolve unknown speakers."""

    def __call__(self, speaker_label: str, sample_utterances: list[str]) -> str | None:
        """Prompt user to resolve a speaker.

        Args:
            speaker_label: The original speaker label (e.g., "Speaker B")
            sample_utterances: List of 2-3 sample utterances from this speaker

        Returns:
            The resolved name, or None if user cancelled
        """
        ...


def resolve_speakers(
    text: str, ui_callback: SpeakerResolutionUI | None = None
) -> tuple[str, dict[str, str]]:
    """Resolve speaker labels to actual names.

    Identifies speakers using:
    - Contextual references in the text
    - Special handling for Dan Moisan
    - UI callback for unresolved speakers

    Args:
        text: Normalized text with CRLF line endings
        ui_callback: Optional UI callback for resolving unknown speakers

    Returns:
        Tuple of (modified text with resolved speakers, mapping of old->new labels)
    """
    if not text or not text.strip():
        return text, {}

    # Find all unique speaker labels
    speaker_labels = _extract_speaker_labels(text)
    logger.debug(f"Found speaker labels: {speaker_labels}")

    # Build mapping of speaker labels to resolved names
    speaker_map: dict[str, str] = {}

    # Extract all potential names from metadata and dialogue
    metadata_names = _extract_names_from_metadata(text, speaker_labels)
    # dialogue_names = _extract_names_from_dialogue(text)
    # available_names = metadata_names | dialogue_names
    available_names = extract_person_names_from_text(text, metadata_names)
    logger.debug(f"Metadata names: {[n.full_name for n in metadata_names]}")
    # logger.debug(f"Dialogue names: {[n.full_name for n in dialogue_names]}")
    logger.debug(f"Available names: {[n.full_name for n in available_names]}")

    # Build a mapping of Name -> possible speakers
    name_to_speakers: dict[Name, list[str]] = {}
    for name in available_names:
        candidates = _identify_speaker_by_name(text, speaker_labels, name)
        if candidates:
            name_to_speakers[name] = candidates
            logger.debug(f"Name '{name.full_name}' matched to speakers: {candidates}")

    # Handle Dan Moisan specially - always use full name
    # Find any Name with first_name Dan/Daniel (using variants)
    dan_name = Name(first_name="Dan")
    for name in list(name_to_speakers.keys()):
        if dan_name.matches(name):
            dan_candidates = name_to_speakers[name]
            if len(dan_candidates) == 1:
                speaker_map[dan_candidates[0]] = "Dan Moisan"
                logger.debug(f"Mapped Dan Moisan: {dan_candidates[0]} -> Dan Moisan")
            # Remove from further processing
            del name_to_speakers[name]
            break

    # Resolve unambiguous mappings (1 name -> 1 speaker)
    for name, candidates in name_to_speakers.items():
        if len(candidates) == 1:
            speaker = candidates[0]
            if speaker not in speaker_map:  # Don't overwrite existing
                speaker_map[speaker] = name.full_name
                logger.debug(f"Mapped unambiguous: {speaker} -> {name.full_name}")

    # Try to match remaining speakers to available names
    unresolved_speakers = [s for s in speaker_labels if s not in speaker_map]
    logger.debug(f"Unresolved speakers: {unresolved_speakers}")

    # FALLBACK: For metadata names that had no dialogue matches,
    # try process of elimination with remaining speakers
    if unresolved_speakers and metadata_names:
        unused_metadata_names = [name for name in metadata_names if name not in name_to_speakers]
        unused_full_names = [n.full_name for n in unused_metadata_names]
        logger.debug(f"Unused metadata names (no dialogue match): {unused_full_names}")

        # Prefer names with last names (more specific) over first-name-only
        preferred_names = [name for name in unused_metadata_names if name.last_name]
        if not preferred_names:
            # If no names with last names, use all unused names
            preferred_names = unused_metadata_names
        logger.debug(f"Preferred names: {[n.full_name for n in preferred_names]}")

        # If we have exactly 1 unresolved speaker and at least 1 preferred name
        if len(unresolved_speakers) == 1 and len(preferred_names) >= 1:
            # Use the first preferred name as a fallback
            chosen_name = preferred_names[0]
            speaker_map[unresolved_speakers[0]] = chosen_name.full_name
            logger.debug(
                f"Matched by elimination (first available): "
                f"{unresolved_speakers[0]} -> {chosen_name.full_name}"
            )
            unresolved_speakers = []  # All resolved
        # Otherwise, if exactly 1 unused name total, use that
        elif len(unresolved_speakers) == 1 and len(unused_metadata_names) == 1:
            unused_name = unused_metadata_names[0].full_name
            speaker_map[unresolved_speakers[0]] = unused_name
            logger.debug(f"Matched by elimination: {unresolved_speakers[0]} -> {unused_name}")
            unresolved_speakers = []  # All resolved

    # For any still-unresolved speakers, use UI callback if provided
    if ui_callback:
        unresolved_speakers = [s for s in speaker_labels if s not in speaker_map]
        for speaker in unresolved_speakers:
            if speaker not in speaker_map:
                samples = _extract_speaker_samples(speaker, text, count=3)
                resolved = ui_callback(speaker, samples)
                if resolved:
                    speaker_map[speaker] = resolved

    # Apply the mappings to the text
    modified_text = _apply_speaker_mappings(text, speaker_map)

    return modified_text, speaker_map


def _extract_speaker_labels(text: str) -> list[str]:
    """Extract all unique speaker labels from text.

    Args:
        text: The text to analyze

    Returns:
        List of unique speaker labels in order of first appearance
    """
    # Match patterns like "Speaker A:", "Speaker: B", "John:", etc.
    pattern = r"^([A-Z][A-Za-z0-9\s]*?):\s"
    labels: list[str] = []
    seen: set[str] = set()

    lines = text.split("\r\n")

    # Check if text contains "Transcript:" label
    has_transcript_label = any(line.strip().startswith("Transcript:") for line in lines)

    # If Transcript: label exists, only process lines after it
    # Otherwise, process all lines (for backward compatibility with tests)
    in_transcript = not has_transcript_label

    for line in lines:
        # Check if we've reached the transcript section
        if not in_transcript:
            if line.strip().startswith("Transcript:"):
                in_transcript = True
            continue

        # Now we're in the transcript, extract speaker labels
        match = re.match(pattern, line)
        if match:
            label = match.group(1).strip()
            if label not in seen:
                labels.append(label)
                seen.add(label)

    return labels


def _identify_speaker_by_name(text: str, speaker_labels: list[str], name: Name) -> list[str]:
    """Identify which speaker label(s) could correspond to a person.

    Uses a two-pass approach:
    1. Direct inference: Identify speakers who address the person (they are NOT that person)
    2. Proximity heuristics: If ambiguous, use response patterns to narrow candidates

    Proximity patterns:
    - Immediate response after direct address (likely the addressed person)
    - Self-identification ("Sorry, I was saying..." after being muted/frozen)
    - Third-person references by others ("her screen", "she is on mute")

    Args:
        text: The text to analyze
        speaker_labels: List of speaker labels
        name: The Name object to identify

    Returns:
        List of possible speaker labels for the named person
        (may be empty or contain multiple candidates)
    """
    lines = text.split("\r\n")

    # PASS 1: Direct inference - find who addresses the person
    speakers_addressing_person: list[str] = []
    direct_address_locations: list[int] = []  # Track where direct addresses occur

    # Check all name variants (first name, shortened forms)
    name_variants = name.shortened_variants

    for i, line in enumerate(lines):
        # Look for any variant of the name in dialogue (not as a speaker label)
        # Check if this is a direct address (not hypothetical/third-person)
        line_lower = line.lower()
        found_variant = None
        for variant in name_variants:
            variant_lower = variant.lower()
            if (
                not line_lower.startswith(f"{variant_lower}:")
                and variant_lower in line_lower
                and _is_direct_address_to_person(line, variant)
            ):
                found_variant = variant
                break

        if found_variant:
            # Found a direct address to the person
            # Find which speaker said this (they are addressing the person)
            for j in range(i, -1, -1):
                if _is_speaker_line(lines[j], speaker_labels):
                    speaker = _extract_speaker_from_line(lines[j])
                    if speaker and speaker not in name_variants:
                        speakers_addressing_person.append(speaker)
                        direct_address_locations.append(i)
                    break

    # Calculate possible speakers from direct inference
    if speakers_addressing_person:
        speakers_addressing_person_set: set[str] = set(speakers_addressing_person)
        possible_speakers = [
            speaker
            for speaker in speaker_labels
            if speaker not in speakers_addressing_person_set and speaker not in name_variants
        ]

        # PASS 2: Proximity heuristics if multiple candidates remain
        if len(possible_speakers) > 1:
            refined_candidates = _apply_proximity_heuristics(
                lines, speaker_labels, name, possible_speakers, direct_address_locations
            )
            if refined_candidates:
                return refined_candidates

        return possible_speakers

    return []


def _apply_proximity_heuristics(
    lines: list[str],
    speaker_labels: list[str],
    name: Name,
    candidates: list[str],
    address_locations: list[int],
) -> list[str]:
    """Apply proximity heuristics to narrow down speaker candidates.

    Heuristics used:
    1. Third-person exclusion: Remove candidates who refer to person in 3rd person
    2. Immediate response: Speaker who responds right after being addressed
    3. Self-identification: Apologies or explanations indicating identity

    Args:
        lines: All lines of text split by CRLF
        speaker_labels: List of all speaker labels
        name: The Name object being identified
        candidates: Current list of possible speakers for this name
        address_locations: Line indices where direct addresses to name occurred

    Returns:
        Refined list of candidates, or empty list if heuristics don't help
    """
    # Use first name and variants for matching
    name_variants_lower = {v.lower() for v in name.shortened_variants}
    name_lower = name.first_name.lower()

    # FIRST: Exclude speakers who use third-person references
    # These speakers are definitively NOT the person
    # Check for any name variant in third-person context
    third_person_patterns: list[str] = []
    for variant_lower in name_variants_lower:
        third_person_patterns.extend(
            [
                # Gendered pronouns with name
                rf"\b(her|she|she'?s)\b.*{variant_lower}",
                rf"{variant_lower}.*\b(her|she|she'?s)\b",
                rf"\b(his|he|he'?s)\b.*{variant_lower}",
                rf"{variant_lower}.*\b(his|he|he'?s)\b",
                # Possession with name
                rf"{variant_lower}'?s\s+(screen|audio|connection|microphone)",
                # Status references with name
                rf"{variant_lower}\s+is\s+(muted?|frozen|disconnected)",
            ]
        )
    # Add generic third-person patterns
    third_person_patterns.extend(
        [
            # Generic third-person tech references
            r"\b(her|his)\s+(screen|audio|connection|microphone|video)\b",
            r"\b(she|he)\s+is\s+(muted?|frozen|disconnected)\b",
            # Generic third-person pronouns
            r"\b(she|he)\b",
        ]
    )

    speakers_using_third_person: set[str] = set()
    for line in lines:
        line_lower = line.lower()
        speaker = _extract_speaker_from_line(line)
        if speaker:
            for pattern in third_person_patterns:
                if re.search(pattern, line_lower):
                    speakers_using_third_person.add(speaker)
                    break

    # Filter out candidates who used third-person references
    candidates = [c for c in candidates if c not in speakers_using_third_person]

    # If we've narrowed down to one candidate, return immediately
    if len(candidates) == 1:
        return candidates

    # If no candidates remain, return empty (heuristics failed)
    if not candidates:
        return []

    # THEN: Score remaining candidates
    candidate_scores: dict[str, int] = {speaker: 0 for speaker in candidates}

    # Heuristic 1: Immediate response pattern
    # If a candidate responds immediately after being addressed, score +3
    # BUT: Check that the response is self-referential, not asking about the person
    # Also filter out: speakers building on the question (not the actual response)
    # Exception: "can you hear ME" is self-referential, "can you hear" (without ME) is asking
    asking_about_patterns = [
        r"\bare\s+you\s+there\b",
        r"\bwhere\s+(is|are)\s+you\b",
        r"\bcan\s+you\s+hear\b(?!\s+me)",  # "can you hear" but NOT "can you hear me"
        rf"\b{name_lower},?\s+are\s+you\b",
        r"\bdid\s+you\s+(hear|get|see)\b",
        r"\byou\s+(are|is)\s+on\s+mute\b",  # Telling someone they're muted
        r"\byou\s+(are|is)\s+(muted|frozen|disconnected)\b",  # Technical issue notifications
        r"\byour\s+(audio|video|screen|connection)\b",  # Referring to their tech
    ]

    # Patterns indicating someone is building on the question, not responding to it
    building_on_question_patterns = [
        r"\b(let\s+me\s+)?build(ing)?\b",  # "let me build", "building on that"
        r"\bto\s+add\s+to\s+that\b",
        r"\balso\b.*\b(can|could|would)\s+you\b",  # "also can you", "also could you"
        r"\band\s+(can|could|would)\s+you\b",  # "and can you", "and would you"
        r"\b(can|could|would)\s+you\s+(also|tell|share|explain)\b",  # continuing to ask
    ]

    for addr_line_idx in address_locations:
        # Find the next speaker line after the address
        responding_speaker = None
        response_line = None
        for i in range(addr_line_idx + 1, len(lines)):
            if _is_speaker_line(lines[i], speaker_labels):
                responding_speaker = _extract_speaker_from_line(lines[i])
                response_line = lines[i].lower()
                break
            # Stop if we hit another address or too many non-speaker lines
            if i - addr_line_idx > 5:
                break

        if responding_speaker and responding_speaker in candidates and response_line:
            # Check if this is actually asking ABOUT the person (not a self-response)
            is_asking_about = any(
                re.search(pattern, response_line) for pattern in asking_about_patterns
            )

            # Check if this is building on the question (not the actual response)
            is_building_on_question = any(
                re.search(pattern, response_line) for pattern in building_on_question_patterns
            )

            if not is_asking_about and not is_building_on_question:
                candidate_scores[responding_speaker] += 3

    # Heuristic 2: Self-identification patterns
    # Look for apologetic or clarifying phrases that indicate identity
    self_id_patterns = [
        r"\bsorry,?\s+i\b",  # "Sorry, I was..."
        r"\bno,?\s+i'?m\s+here\b",  # "No, I'm here"
        r"\bapologies?\b.*\bi\b",  # "Apologies, I..."
        r"\bi\s+was\s+(saying|trying|just)\b",  # "I was saying..."
        r"\bcan\s+you\s+hear\s+me\s+now\b",  # "Can you hear me now"
        r"\bi\s+lost\s+(you|connection)\b",  # "I lost you"
        r"^[^:]+:\s*sure,?\s+(let\s+me|i('ll)?|i\s+can)\b",  # "Sure, let me...", "Sure, I'll..."
        r"\blet\s+me\s+(begin|start|explain|share)\b",  # "let me begin", "let me start"
    ]

    for line in lines:
        line_lower = line.lower()
        speaker = _extract_speaker_from_line(line)

        if speaker and speaker in candidates:
            for pattern in self_id_patterns:
                if re.search(pattern, line_lower):
                    candidate_scores[speaker] += 2
                    break

    # Return candidates with highest scores (if there's a clear winner)
    if not candidate_scores:
        return []

    max_score = max(candidate_scores.values())
    if max_score == 0:
        # No heuristics helped
        return []

    # Return candidates with the maximum score
    # Only return if there's a meaningful score (> 1)
    if max_score > 1:
        top_candidates = [s for s, score in candidate_scores.items() if score == max_score]
        return top_candidates

    return []


def _identify_dan_moisan(text: str, speaker_labels: list[str]) -> str | None:
    """Identify which speaker label corresponds to Dan Moisan.

    This is a convenience wrapper around _identify_speaker_by_name.
    Returns the first candidate if multiple are found, or None if no candidates.

    Args:
        text: The text to analyze
        speaker_labels: List of speaker labels

    Returns:
        The speaker label for Dan Moisan, or None if not found
    """
    dan_name = Name(first_name="Dan")
    candidates = _identify_speaker_by_name(text, speaker_labels, dan_name)
    return candidates[0] if candidates else None


def _is_direct_address_to_person(line: str, name: str) -> bool:
    """Check if a line contains a direct address to a person vs hypothetical/third-person reference.

    Direct address patterns:
    - "Name, what..." (vocative with comma at start)
    - "..., Name." (vocative with comma at end)
    - "...to Name." (prepositional phrases)
    - "Name mentioned/said..." (attribution)

    NOT direct address (hypothetical/third-person):
    - "is Name a..." (third-person question)
    - "if ... is Name" (conditional/hypothetical)
    - "Is Name ..." (question about Name, not to Name)

    Args:
        line: The line to check
        name: The first name to check for (e.g., "Dan", "John", "Alice")

    Returns:
        True if this is a direct address to the named person
    """
    line_lower = line.lower()
    name_lower = name.lower()

    # Exclude third-person questions about the person
    # Pattern: "is Name [article] [noun]" like "is Dan a leader"
    if re.search(rf"\bis {name_lower} (a|an|the)\b", line_lower):
        return False

    # Exclude questions that start with "Is Name"
    # These are questions ABOUT the person, not TO them
    if re.search(rf"\bis {name_lower}\b", line_lower):
        return False

    # Exclude hypothetical framing
    # "if you were to say" or "the question is"
    hypothetical_markers = [
        r"if you were to say",
        r"if someone were to ask",
        rf"the question is.*{name_lower}",
        rf"you might ask.*{name_lower}",
        rf"one might say.*{name_lower}",
    ]
    for marker in hypothetical_markers:
        if re.search(marker, line_lower):
            return False

    # Check for direct address patterns
    # "Name, " with vocative comma
    if re.search(rf"\b{name_lower},\s", line_lower):
        return True

    # "Name " at start followed by question or imperative
    # Examples: "Dan what do you think?" "Alice tell me about..."
    # Match name at word boundary followed by space and question word or verb
    if re.search(
        rf"\b{name_lower}\s+(what|where|when|why|how|who|can|could|would|will|tell|explain|show)",
        line_lower,
    ):
        return True

    # ", Name" at end of sentence or phrase (vocative)
    # Examples: "Thanks, Dan." "I'm learning about you, Dan."
    if re.search(rf",\s*{name_lower}\b", line_lower):
        return True

    # "to Name" or "with Name" (but we already excluded "is Name")
    if re.search(rf"\b(to|with|for|about|from)\s+{name_lower}\b", line_lower):
        return True

    # "Name mentioned" or "Name said" (third person but attributive)
    return bool(
        re.search(rf"\b{name_lower}\s+(mentioned|said|thinks|believes|suggested)\b", line_lower)
    )


def _extract_names_from_metadata(text: str, speaker_labels: list[str] | None = None) -> set[Name]:
    """Extract names from metadata section of transcript.

    Metadata is everything before the "Transcript:" label.
    Everything after "Transcript:" is dialogue.

    Args:
        text: The text to analyze
        speaker_labels: Optional list of known speaker labels (unused, kept for compatibility)

    Returns:
        Set of Name objects found in metadata
    """
    names: set[Name] = set()
    lines = text.split("\r\n")

    # Metadata is everything before "Transcript:" label
    for line in lines:
        # Stop when we hit the Transcript section
        if line.strip().startswith("Transcript:"):
            break

        # Extract names from metadata lines
        if any(keyword in line.lower() for keyword in ["attendee", "participant", "present"]):
            found_names = _extract_names_from_line(line)
            names.update(found_names)

    return names


def _extract_title_case_chains(text: str) -> list[tuple[str, int]]:
    """Extract chains of consecutive title-cased words from text.

    Identifies sequences of title-cased words (e.g., "Dan Moisan", "New York")
    and returns them as word groups along with their position.

    Args:
        text: The text to analyze

    Returns:
        List of tuples (word_group, start_position) where word_group is the
        space-joined title-cased words
    """
    # Pattern to match title-cased words
    title_case_pattern = r"\b[A-Z][a-z]+\b"

    chains: list[tuple[str, int]] = []
    words = list(re.finditer(title_case_pattern, text))

    if not words:
        return chains

    # Group consecutive title-cased words
    current_chain = [words[0]]

    for i in range(1, len(words)):
        prev_end = words[i - 1].end()
        curr_start = words[i].start()

        # Check if words are consecutive (only whitespace between)
        between = text[prev_end:curr_start]
        if between.strip() == "":
            current_chain.append(words[i])
        else:
            # Save current chain if it exists
            if current_chain:
                chain_text = " ".join(m.group() for m in current_chain)
                chains.append((chain_text, current_chain[0].start()))
            current_chain = [words[i]]

    # Don't forget the last chain
    if current_chain:
        chain_text = " ".join(m.group() for m in current_chain)
        chains.append((chain_text, current_chain[0].start()))

    return chains


def _is_proper_noun(word_group: str) -> bool:
    """Check if a word or word group is a proper noun.

    Enhanced logic:
    - Looks for title case chains (consecutive title-cased words are entities)
    - For single words, checks against English dictionary
    - Whitelists common first names that are in the dictionary
    - Word groups >3 tokens are rejected (unlikely to be names)

    Args:
        word_group: The word or phrase to check (may be multiple words)

    Returns:
        True if the word group appears to be a proper noun
    """
    if not word_group or not word_group.strip():
        return False

    tokens = word_group.strip().split()

    # Word groups >3 tokens are unlikely to be names
    if len(tokens) > 3:
        return False

    # All tokens must be title-cased
    for token in tokens:
        if len(token) < 2:
            return False
        if not token[0].isupper():
            return False
        if token.isupper():  # All caps (acronym)
            return False
        if not any(c.islower() for c in token):
            return False

    # For single-word groups, check if it's in the English dictionary
    # However, whitelist common first names that are in the dictionary
    if len(tokens) == 1:
        word_lower = tokens[0].lower()

        # Whitelist of common first names that should not be filtered
        # even though they're in the English dictionary
        common_first_names = {
            "dan",
            "john",
            "alice",
            "bob",
            "jane",
            "mary",
            "james",
            "michael",
            "david",
            "robert",
            "william",
            "richard",
            "joseph",
            "thomas",
            "charles",
            "christopher",
            "daniel",
            "matthew",
            "anthony",
            "mark",
            "donald",
            "steven",
            "paul",
            "andrew",
            "joshua",
            "kenneth",
            "kevin",
            "brian",
            "george",
            "edward",
            "ronald",
            "timothy",
            "jason",
            "jeffrey",
            "ryan",
            "jacob",
            "gary",
            "nicholas",
            "eric",
            "jonathan",
            "stephen",
            "larry",
            "justin",
            "scott",
            "brandon",
            "benjamin",
            "samuel",
            "frank",
            "gregory",
            "raymond",
            "patrick",
            "alexander",
            "jack",
            "dennis",
            "jerry",
            "tyler",
            "aaron",
            "jose",
            "henry",
            "adam",
            "douglas",
            "nathan",
            "peter",
            "zachary",
            "kyle",
            "walter",
            "harold",
            "jeremy",
            "ethan",
            "carl",
            "keith",
            "roger",
            "gerald",
            "christian",
            "terry",
            "sean",
            "arthur",
            "austin",
            "noah",
            "lawrence",
            "jesse",
            "joe",
            "bryan",
            "billy",
            "jordan",
            "albert",
            "dylan",
            "bruce",
            "willie",
            "gabriel",
            "logan",
            "alan",
            "juan",
            "ralph",
            "roy",
            "eugene",
            "randy",
            "vincent",
            "russell",
            "louis",
            "philip",
            "bobby",
            "johnny",
            "bradley",
            # Common female names
            "sarah",
            "jennifer",
            "lisa",
            "michelle",
            "nancy",
            "karen",
            "betty",
            "helen",
            "sandra",
            "donna",
            "carol",
            "ruth",
            "sharon",
            "laura",
            "kimberly",
            "deborah",
            "jessica",
            "shirley",
            "cynthia",
            "angela",
            "melissa",
            "brenda",
            "amy",
            "anna",
            "rebecca",
            "virginia",
            "kathleen",
            "pamela",
            "martha",
            "debra",
            "amanda",
            "stephanie",
            "carolyn",
            "christine",
            "marie",
            "janet",
            "catherine",
            "frances",
            "ann",
            "joyce",
            "diane",
            "julie",
            "heather",
            "teresa",
            "doris",
            "gloria",
            "evelyn",
            "jean",
            "cheryl",
            "mildred",
            "katherine",
            "joan",
            "ashley",
            "judith",
            "rose",
            "janice",
            "kelly",
            "nicole",
            "judy",
            "christina",
            "kathy",
            "theresa",
            "beverly",
            "denise",
            "tammy",
            "irene",
            "lori",
            "rachel",
            "marilyn",
            "andrea",
            "kathryn",
            "louise",
            "sara",
            "anne",
            "jacqueline",
            "wanda",
            "bonnie",
            "julia",
            "ruby",
            "lois",
            "tina",
            "phyllis",
            "norma",
            "paula",
            "diana",
            "annie",
            "lillian",
            "emily",
            "robin",
            "peggy",
            "crystal",
            "gladys",
            "rita",
            "dawn",
            "connie",
            "florence",
            "tracy",
            "edna",
            "tiffany",
            "carmen",
            "rosa",
            "cindy",
            "grace",
            "wendy",
            "victoria",
            "edith",
            "kim",
            "sherry",
            "sylvia",
            "josephine",
            "thelma",
            "shannon",
            "sheila",
            "ethel",
            "ellen",
            "elaine",
            "marjorie",
            "carrie",
            "charlotte",
            "monica",
            "esther",
            "pauline",
            "emma",
            "juanita",
            "anita",
            "rhonda",
            "hazel",
            "amber",
            "eva",
            "debbie",
            "april",
            "leslie",
            "clara",
            "lucille",
            "jamie",
            "joanne",
            "eleanor",
            "valerie",
            "danielle",
            "megan",
            "alicia",
            "suzanne",
            "michele",
            "gail",
            "bertha",
            "darlene",
            "veronica",
            "jill",
            "erin",
            "geraldine",
            "lauren",
            "cathy",
            "joann",
            "lorraine",
            "lynn",
            "sally",
            "regina",
            "erica",
            "beatrice",
            "dolores",
            "bernice",
            "audrey",
            "yvonne",
            "annette",
            "june",
            "samantha",
            "marion",
            "dana",
            "stacy",
            "ana",
            "renee",
            "ida",
            "vivian",
            "roberta",
            "holly",
            "brittany",
            "melanie",
            "loretta",
            "yolanda",
            "jeanette",
            "laurie",
            "katie",
            "kristen",
            "vanessa",
            "alma",
            "sue",
            "elsie",
            "beth",
            "jeanne",
            "vicki",
            "carla",
            "tara",
            "rosemary",
            "eileen",
            "terri",
            "gertrude",
            "lucy",
            "tonya",
            "ella",
            "stacey",
            "wilma",
            "gina",
            "kristin",
            "jessie",
            "natalie",
            "agnes",
            "vera",
            "charlene",
            "bessie",
            "delores",
            "melinda",
            "pearl",
            "arlene",
            "maureen",
            "colleen",
            "allison",
            "tamara",
            "joy",
            "georgia",
            "constance",
            "lillie",
            "claudia",
            "jackie",
            "marcia",
            "tanya",
            "nellie",
            "minnie",
            "marlene",
            "heidi",
            "glenda",
            "lydia",
            "viola",
            "courtney",
            "marian",
            "stella",
            "caroline",
            "dora",
            "jo",
            "vickie",
            "mattie",
            "maxine",
            "irma",
            "mabel",
            "marsha",
            "myrtle",
            "lena",
            "christy",
            "deanna",
            "patsy",
            "hilda",
            "gwendolyn",
            "jennie",
            "nora",
            "margie",
            "nina",
            "cassandra",
            "leah",
            "penny",
            "kay",
            "priscilla",
            "naomi",
            "carole",
            "brandy",
            "olga",
            "billie",
            "dianne",
            "tracey",
            "leona",
            "jenny",
            "felicia",
            "sonia",
            "miriam",
            "velma",
            "becky",
            "bobbie",
            "violet",
            "kristina",
            "toni",
            "misty",
            "mae",
            "shelly",
            "daisy",
            "ramona",
            "sherri",
            "erika",
            "katrina",
        }

        # If it's a common first name, treat it as a proper noun
        if word_lower in common_first_names:
            logger.debug(f"'{word_group}' is a whitelisted common first name")
            return True

        # Otherwise check against dictionary
        english_words = _get_english_words()
        english_words.add("okay")
        if word_lower in english_words:
            logger.debug(f"Skipping '{word_group}': found in English dictionary")
            return False

    return True


def _is_likely_person_name(word_group: str) -> bool:
    """Determine if a proper noun is likely a person name vs. place/thing.

    Enhanced logic:
    - Multi-token groups with English words are likely company names/titles
    - Exception: honorifics like "Mr.", "Mrs.", "Dr." are not company names
    - Single-token groups are checked against exclusion lists

    Args:
        word_group: The proper noun to classify (may be multiple words)

    Returns:
        True if the word group is likely a person name
    """
    tokens = word_group.strip().split()

    # Honorifics that indicate a person name follows
    honorifics = {"mr", "mrs", "ms", "dr", "prof", "sir", "dame", "lord", "lady"}

    # Whitelist of common first names (same as in _is_proper_noun)
    common_first_names = {
        "dan",
        "john",
        "alice",
        "bob",
        "jane",
        "mary",
        "james",
        "michael",
        "david",
        "robert",
        "william",
        "richard",
        "joseph",
        "thomas",
        "charles",
        "christopher",
        "daniel",
        "matthew",
        "anthony",
        "mark",
        "donald",
        "steven",
        "paul",
        "andrew",
        "joshua",
        "kenneth",
        "kevin",
        "brian",
        "george",
        "edward",
        "ronald",
        "timothy",
        "jason",
        "jeffrey",
        "ryan",
        "jacob",
        "gary",
        "nicholas",
        "eric",
        "jonathan",
        "stephen",
        "larry",
        "justin",
        "scott",
        "brandon",
        "benjamin",
        "samuel",
        "frank",
        "gregory",
        "raymond",
        "patrick",
        "alexander",
        "jack",
        "dennis",
        "jerry",
        "tyler",
        "aaron",
        "jose",
        "henry",
        "adam",
        "douglas",
        "nathan",
        "peter",
        "zachary",
        "kyle",
        "walter",
        "harold",
        "jeremy",
        "ethan",
        "carl",
        "keith",
        "roger",
        "gerald",
        "christian",
        "terry",
        "sean",
        "arthur",
        "austin",
        "noah",
        "lawrence",
        "jesse",
        "joe",
        "bryan",
        "billy",
        "jordan",
        "albert",
        "dylan",
        "bruce",
        "willie",
        "gabriel",
        "logan",
        "alan",
        "juan",
        "ralph",
        "roy",
        "eugene",
        "randy",
        "vincent",
        "russell",
        "louis",
        "philip",
        "bobby",
        "johnny",
        "bradley",
        # Common female names
        "sarah",
        "jennifer",
        "lisa",
        "michelle",
        "nancy",
        "karen",
        "betty",
        "helen",
        "sandra",
        "donna",
        "carol",
        "ruth",
        "sharon",
        "laura",
        "kimberly",
        "deborah",
        "jessica",
        "shirley",
        "cynthia",
        "angela",
        "melissa",
        "brenda",
        "amy",
        "anna",
        "rebecca",
        "virginia",
        "kathleen",
        "pamela",
        "martha",
        "debra",
        "amanda",
        "stephanie",
        "carolyn",
        "christine",
        "marie",
        "janet",
        "catherine",
        "frances",
        "ann",
        "joyce",
        "diane",
        "julie",
        "heather",
        "teresa",
        "doris",
        "gloria",
        "evelyn",
        "jean",
        "cheryl",
        "mildred",
        "katherine",
        "joan",
        "ashley",
        "judith",
        "rose",
        "janice",
        "kelly",
        "nicole",
        "judy",
        "christina",
        "kathy",
        "theresa",
        "beverly",
        "denise",
        "tammy",
        "irene",
        "lori",
        "rachel",
        "marilyn",
        "andrea",
        "kathryn",
        "louise",
        "sara",
        "anne",
        "jacqueline",
        "wanda",
        "bonnie",
        "julia",
        "ruby",
        "lois",
        "tina",
        "phyllis",
        "norma",
        "paula",
        "diana",
        "annie",
        "lillian",
        "emily",
        "robin",
        "peggy",
        "crystal",
        "gladys",
        "rita",
        "dawn",
        "connie",
        "florence",
        "tracy",
        "edna",
        "tiffany",
        "carmen",
        "rosa",
        "cindy",
        "grace",
        "wendy",
        "victoria",
        "edith",
        "kim",
        "sherry",
        "sylvia",
        "josephine",
        "thelma",
        "shannon",
        "sheila",
        "ethel",
        "ellen",
        "elaine",
        "marjorie",
        "carrie",
        "charlotte",
        "monica",
        "esther",
        "pauline",
        "emma",
        "juanita",
        "anita",
        "rhonda",
        "hazel",
        "amber",
        "eva",
        "debbie",
        "april",
        "leslie",
        "clara",
        "lucille",
        "jamie",
        "joanne",
        "eleanor",
        "valerie",
        "danielle",
        "megan",
        "alicia",
        "suzanne",
        "michele",
        "gail",
        "bertha",
        "darlene",
        "veronica",
        "jill",
        "erin",
        "geraldine",
        "lauren",
        "cathy",
        "joann",
        "lorraine",
        "lynn",
        "sally",
        "regina",
        "erica",
        "beatrice",
        "dolores",
        "bernice",
        "audrey",
        "yvonne",
        "annette",
        "june",
        "samantha",
        "marion",
        "dana",
        "stacy",
        "ana",
        "renee",
        "ida",
        "vivian",
        "roberta",
        "holly",
        "brittany",
        "melanie",
        "loretta",
        "yolanda",
        "jeanette",
        "laurie",
        "katie",
        "kristen",
        "vanessa",
        "alma",
        "sue",
        "elsie",
        "beth",
        "jeanne",
        "vicki",
        "carla",
        "tara",
        "rosemary",
        "eileen",
        "terri",
        "gertrude",
        "lucy",
        "tonya",
        "ella",
        "stacey",
        "wilma",
        "gina",
        "kristin",
        "jessie",
        "natalie",
        "agnes",
        "vera",
        "charlene",
        "bessie",
        "delores",
        "melinda",
        "pearl",
        "arlene",
        "maureen",
        "colleen",
        "allison",
        "tamara",
        "joy",
        "georgia",
        "constance",
        "lillie",
        "claudia",
        "jackie",
        "marcia",
        "tanya",
        "nellie",
        "minnie",
        "marlene",
        "heidi",
        "glenda",
        "lydia",
        "viola",
        "courtney",
        "marian",
        "stella",
        "caroline",
        "dora",
        "jo",
        "vickie",
        "mattie",
        "maxine",
        "irma",
        "mabel",
        "marsha",
        "myrtle",
        "lena",
        "christy",
        "deanna",
        "patsy",
        "hilda",
        "gwendolyn",
        "jennie",
        "nora",
        "margie",
        "nina",
        "cassandra",
        "leah",
        "penny",
        "kay",
        "priscilla",
        "naomi",
        "carole",
        "brandy",
        "olga",
        "billie",
        "dianne",
        "tracey",
        "leona",
        "jenny",
        "felicia",
        "sonia",
        "miriam",
        "velma",
        "becky",
        "bobbie",
        "violet",
        "kristina",
        "toni",
        "misty",
        "mae",
        "shelly",
        "daisy",
        "ramona",
        "sherri",
        "erika",
        "katrina",
    }

    # Whitelist of common last names that are also in the dictionary
    common_last_names = {
        "smith",
        "johnson",
        "williams",
        "jones",
        "brown",
        "davis",
        "miller",
        "wilson",
        "moore",
        "taylor",
        "anderson",
        "thomas",
        "jackson",
        "white",
        "harris",
        "martin",
        "thompson",
        "garcia",
        "martinez",
        "robinson",
        "clark",
        "rodriguez",
        "lewis",
        "lee",
        "walker",
        "hall",
        "allen",
        "young",
        "hernandez",
        "king",
        "wright",
        "lopez",
        "hill",
        "scott",
        "green",
        "adams",
        "baker",
        "gonzalez",
        "nelson",
        "carter",
        "mitchell",
        "perez",
        "roberts",
        "turner",
        "phillips",
        "campbell",
        "parker",
        "evans",
        "edwards",
        "collins",
        "stewart",
        "sanchez",
        "morris",
        "rogers",
        "reed",
        "cook",
        "morgan",
        "bell",
        "murphy",
        "bailey",
        "rivera",
        "cooper",
        "richardson",
        "cox",
        "howard",
        "ward",
        "torres",
        "peterson",
        "gray",
        "ramirez",
        "james",
        "watson",
        "brooks",
        "kelly",
        "sanders",
        "price",
        "bennett",
        "wood",
        "barnes",
        "ross",
        "henderson",
        "coleman",
        "jenkins",
        "perry",
        "powell",
        "long",
        "patterson",
        "hughes",
        "flores",
        "washington",
        "butler",
        "simmons",
        "foster",
        "gonzales",
        "bryant",
        "alexander",
        "russell",
        "griffin",
        "diaz",
        "hayes",
        "myers",
        "ford",
        "hamilton",
        "graham",
        "sullivan",
        "wallace",
        "woods",
        "cole",
        "west",
        "jordan",
        "owens",
        "reynolds",
        "fisher",
        "ellis",
        "harrison",
        "gibson",
        "mcdonald",
        "cruz",
        "marshall",
        "ortiz",
        "gomez",
        "murray",
        "freeman",
        "wells",
        "webb",
        "simpson",
        "stevens",
        "tucker",
        "porter",
        "hunter",
        "hicks",
        "crawford",
        "henry",
        "boyd",
        "mason",
        "morales",
        "kennedy",
        "warren",
        "dixon",
        "ramos",
        "reyes",
        "burns",
        "gordon",
        "shaw",
        "holmes",
        "rice",
        "robertson",
        "hunt",
        "black",
        "daniels",
        "palmer",
        "mills",
        "nichols",
        "grant",
        "knight",
        "ferguson",
        "rose",
        "stone",
        "hawkins",
        "dunn",
        "perkins",
        "hudson",
        "spencer",
        "gardner",
        "stephens",
        "payne",
        "pierce",
        "berry",
        "matthews",
        "arnold",
        "wagner",
        "willis",
        "ray",
        "watkins",
        "olson",
        "carroll",
        "duncan",
        "snyder",
        "hart",
        "cunningham",
        "bradley",
        "lane",
        "andrews",
        "ruiz",
        "harper",
        "fox",
        "riley",
        "armstrong",
        "carpenter",
        "weaver",
        "greene",
        "lawrence",
        "elliott",
        "chavez",
        "sims",
        "austin",
        "peters",
        "kelley",
        "franklin",
        "lawson",
        "fields",
        "gutierrez",
        "ryan",
        "schmidt",
        "carr",
        "vasquez",
        "castillo",
        "wheeler",
        "chapman",
        "oliver",
        "montgomery",
        "richards",
        "williamson",
        "johnston",
        "banks",
        "meyer",
        "bishop",
        "mccoy",
        "howell",
        "alvarez",
        "morrison",
        "hansen",
        "fernandez",
        "garza",
        "harvey",
        "little",
        "burton",
        "stanley",
        "nguyen",
        "george",
        "jacobs",
        "reid",
        "kim",
        "fuller",
        "lynch",
        "dean",
        "gilbert",
        "garrett",
        "romero",
        "welch",
        "larson",
        "frazier",
        "burke",
        "hanson",
        "day",
        "mendoza",
        "moreno",
        "bowman",
        "medina",
        "fowler",
        "brewer",
        "hoffman",
        "carlson",
        "silva",
        "pearson",
        "holland",
        "douglas",
        "fleming",
        "jensen",
        "vargas",
        "byrd",
        "davidson",
        "hopkins",
        "may",
        "terry",
        "herrera",
        "wade",
        "soto",
        "walters",
        "curtis",
        "neal",
        "caldwell",
        "lowe",
        "jennings",
        "barnett",
        "graves",
        "jimenez",
        "horton",
        "shelton",
        "barrett",
        "obrien",
        "castro",
        "sutton",
        "gregory",
        "mckinney",
        "lucas",
        "miles",
        "craig",
        "rodriquez",
        "chambers",
        "holt",
        "lambert",
        "fletcher",
        "watts",
        "bates",
        "hale",
        "rhodes",
        "pena",
        "beck",
        "newman",
        "haynes",
        "mcdaniel",
        "mendez",
        "bush",
        "vaughn",
        "parks",
        "dawson",
        "santiago",
        "norris",
        "hardy",
        "love",
        "steele",
        "curry",
        "powers",
        "schultz",
        "barker",
        "guzman",
        "page",
        "munoz",
        "ball",
        "keller",
        "chandler",
        "weber",
        "leonard",
        "walsh",
        "lyons",
        "ramsey",
        "wolfe",
        "schneider",
        "mullins",
        "benson",
        "sharp",
        "bowen",
        "daniel",
        "barber",
        "cummings",
        "hines",
        "baldwin",
        "griffith",
        "valdez",
        "hubbard",
        "salazar",
        "reeves",
        "warner",
        "stevenson",
        "burgess",
        "santos",
        "tate",
        "cross",
        "garner",
        "mann",
        "mack",
        "moss",
        "thornton",
        "dennis",
        "mcgee",
        "farmer",
        "delgado",
        "aguilar",
        "vega",
        "glover",
        "manning",
        "cohen",
        "harmon",
        "rodgers",
        "robbins",
        "newton",
        "todd",
        "blair",
        "higgins",
        "ingram",
        "reese",
        "cannon",
        "strickland",
        "townsend",
        "potter",
        "goodman",
        "walton",
        "rowe",
        "hampton",
        "ortega",
        "patton",
        "swanson",
        "joseph",
        "francis",
        "goodwin",
        "maldonado",
        "yates",
        "becker",
        "erickson",
        "hodges",
        "rios",
        "conner",
        "adkins",
        "webster",
        "norman",
        "malone",
        "hammond",
        "flowers",
        "cobb",
        "moody",
        "quinn",
        "blake",
        "maxwell",
        "pope",
        "floyd",
        "osborne",
        "paul",
        "mccarthy",
        "guerrero",
        "lindsey",
        "estrada",
        "sandoval",
        "gibbs",
        "tyler",
        "gross",
        "fitzgerald",
        "stokes",
        "doyle",
        "sherman",
        "saunders",
        "wise",
        "colon",
        "gill",
        "alvarado",
        "greer",
        "padilla",
        "simon",
        "waters",
        "nunez",
        "ballard",
        "schwartz",
        "mcbride",
        "houston",
        "christensen",
        "klein",
        "pratt",
        "briggs",
        "parsons",
        "mclaughlin",
        "zimmerman",
        "french",
        "buchanan",
        "moran",
        "copeland",
        "roy",
        "pittman",
        "brady",
        "mccormick",
        "holloway",
        "brock",
        "poole",
        "frank",
        "logan",
        "owen",
        "bass",
        "marsh",
        "drake",
        "wong",
        "jefferson",
        "park",
        "morton",
        "abbott",
        "sparks",
        "patrick",
        "norton",
        "huff",
        "clayton",
        "massey",
        "lloyd",
        "figueroa",
        "carson",
        "bowers",
        "roberson",
        "barton",
        "tran",
        "lamb",
        "harrington",
        "casey",
        "boone",
        "cortez",
        "clarke",
        "mathis",
        "singleton",
        "wilkins",
        "cain",
        "bryan",
        "underwood",
        "hogan",
        "mckenzie",
        "collier",
        "luna",
        "phelps",
        "mcguire",
        "allison",
        "bridges",
        "wilkerson",
        "nash",
        "summers",
        "atkins",
    }

    # Check if multi-token group contains English words
    # This likely indicates a company name or title
    # Exception: Common first/last names are whitelisted
    if len(tokens) > 1:
        english_words = _get_english_words()

        # Check each token (excluding honorifics and common names)
        for token in tokens:
            token_lower = token.lower().rstrip(".")

            # Skip honorifics
            if token_lower in honorifics:
                continue

            # Skip common first/last names (whitelisted)
            if token_lower in common_first_names or token_lower in common_last_names:
                continue

            # If we find an English word (not a name), it's likely a company/title
            if token_lower in english_words:
                logger.debug(f"Skipping '{word_group}': multi-token with English word '{token}'")
                return False

    # For single tokens, check exclusion lists
    if len(tokens) == 1:
        word_lower = tokens[0].lower()

        # Common places to exclude
        places = {
            "america",
            "north",
            "south",
            "east",
            "west",
            "africa",
            "asia",
            "europe",
            "australia",
            "canada",
            "mexico",
            "california",
            "texas",
            "florida",
            "york",
            "london",
            "paris",
            "tokyo",
            "beijing",
            "moscow",
            "boston",
            "chicago",
            "seattle",
            "atlanta",
            "denver",
            "portland",
            "austin",
        }

        # Temporal words to exclude
        temporal = {
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
        }

        # Organizations/products to exclude
        organizations = {
            "microsoft",
            "apple",
            "google",
            "amazon",
            "facebook",
            "twitter",
            "linkedin",
            "github",
            "windows",
            "linux",
            "android",
            "iphone",
            "internet",
            "email",
        }

        if word_lower in places or word_lower in temporal or word_lower in organizations:
            logger.debug(f"Skipping '{word_group}': in exclusion list")
            return False

    return True


def _ensure_nltk_data() -> None:
    """Ensure required NLTK data packages are downloaded.

    Downloads the following if not already present:
    - punkt or punkt_tab: Sentence tokenization
    - averaged_perceptron_tagger_eng: Part-of-speech tagging (newer NLTK)
    - maxent_ne_chunker: Named entity chunking
    - words: Word corpus for NER

    This function is idempotent and safe to call multiple times.
    """
    import contextlib

    import nltk  # type: ignore[import-untyped]

    # For each package, try common names in order of preference
    packages_to_try = [
        ["punkt_tab", "punkt"],  # Sentence tokenizer
        ["averaged_perceptron_tagger_eng", "averaged_perceptron_tagger"],  # POS tagger
        ["maxent_ne_chunker"],  # NER chunker
        ["words"],  # Word corpus
    ]

    for package_variants in packages_to_try:
        downloaded = False
        for package_name in package_variants:
            if downloaded:
                break
            try:
                # Try to find the package
                nltk.data.find(package_name)  # type: ignore[attr-defined]
                downloaded = True
                logger.debug(f"NLTK package '{package_name}' already available")
            except LookupError:
                # Not found, try to download
                logger.info(f"Downloading NLTK package: {package_name}")
                with contextlib.suppress(Exception):
                    nltk.download(package_name, quiet=True)  # type: ignore[attr-defined]
                    # Verify it was actually downloaded
                    try:
                        nltk.data.find(package_name)  # type: ignore[attr-defined]
                        downloaded = True
                        logger.info(f"Successfully downloaded NLTK package: {package_name}")
                    except LookupError:
                        logger.debug(f"Download of {package_name} did not make it available")

        if not downloaded:
            logger.warning(
                f"Could not download any variant of {package_variants}. "
                "NLTK functionality may be limited."
            )


def strip_before_transcript(text: str, marker: str = "Transcript:") -> str:
    """
    If `marker` is present, remove everything before it (keep the marker).
    If not present, return the text unchanged.
    """
    idx = text.find(marker)
    if idx == -1:
        return text
    start = idx + len(marker)
    return text[start:].lstrip()


def extract_person_names_from_text(text: str, existing_names: set[Name]) -> set[Name]:
    """
    Extract unique person names from a single text string using NLTK.

    Performs matching against existing names to avoid duplicates. For example,
    if "Dan Moisan" is in existing_names and "Dan" is extracted, they will be
    matched and "Dan" will not be added as a separate entry.

    If NLTK data is not available, returns the existing_names unchanged rather
    than crashing.

    Args:
        text: The text to extract names from
        existing_names: Set of Name objects already identified

    Returns:
        Set of Name objects (existing + newly extracted non-matching names)
    """
    from typing import Any

    # Import at runtime to avoid type-checking issues with untyped library
    try:
        from nltk import sent_tokenize, word_tokenize  # type: ignore[import-untyped]
        from nltk.chunk import ne_chunk  # type: ignore[import-untyped]
        from nltk.tag import pos_tag  # type: ignore[import-untyped]
        from nltk.tree import Tree  # type: ignore[import-untyped]
    except ImportError:
        logger.warning("NLTK library not available. Cannot extract names from text using NER.")
        return existing_names.copy()

    # Ensure NLTK data is available before processing
    _ensure_nltk_data()

    # Start with existing names
    result_names: set[Name] = existing_names.copy()

    text = strip_before_transcript(text, marker="Transcript:")

    try:
        # Split text into sentences
        sentences: Any = sent_tokenize(text)
        for sent in sentences:
            # Tokenize and POS-tag
            tokens: Any = word_tokenize(sent)
            tagged: Any = pos_tag(tokens)  # type: ignore[assignment]

            # Named entity chunking
            chunks: Any = ne_chunk(tagged, binary=False)

            # Traverse chunks to find PERSON entities
            for chunk in chunks:
                if isinstance(chunk, Tree) and chunk.label() == "PERSON":
                    # type: ignore on next line: NLTK Tree.leaves() returns untyped tuples
                    name_str = " ".join(token for token, _pos in chunk.leaves())  # type: ignore[misc]

                    # Parse the extracted name string into a Name object
                    try:
                        extracted_name = Name.from_string(name_str)

                        # Check if this name matches any existing name
                        already_exists = any(
                            extracted_name.matches(existing) for existing in result_names
                        )

                        # Only add if it doesn't match an existing name
                        if not already_exists:
                            result_names.add(extracted_name)
                            logger.debug(f"Added new name from NLTK: {extracted_name.full_name}")
                        else:
                            logger.debug(f"Skipping '{name_str}': matches existing name in set")
                    except ValueError as e:
                        # Name.from_string() can raise ValueError for invalid formats
                        logger.debug(f"Skipping '{name_str}': {e}")
    except LookupError as e:
        # NLTK data not available - log and return existing names
        logger.warning(
            f"NLTK data not available for name extraction: {e}. " "Returning existing names only."
        )
        return existing_names.copy()
    except Exception as e:
        # Any other error - log and return existing names
        logger.error(f"Error during NLTK name extraction: {e}. Returning existing names only.")
        return existing_names.copy()

    return result_names


def _extract_names_from_dialogue(text: str) -> set[Name]:
    """Extract names mentioned in dialogue through direct address patterns.

    Enhanced to properly identify proper nouns and distinguish between
    person names vs. places/things. Uses title case chain detection to
    identify multi-word names.

    Only extracts names from clear direct address contexts like:
    - "Hi, Dan"
    - "Thanks, Anne"
    - "Dan, what do you think?"
    - "Hi, Dan Moisan" (multi-word names)

    The function:
    1. Extracts title case chains (e.g., "Dan Moisan", "New York")
    2. Checks if each chain is a proper noun (English dictionary check)
    3. Filters out places, organizations, and common words
    4. Only captures words/chains that are likely person names

    Args:
        text: The text to analyze

    Returns:
        Set of Name objects mentioned in direct address
    """
    names: set[Name] = set()

    # Direct address patterns - capturing one or more title-cased words (non-greedy)
    # Use [ ] instead of \s to prevent matching across lines (\s includes \r and \n)
    # Pattern captures consecutive title-cased words up to 3 words
    name_pattern = r"[A-Z][a-z]+(?:[ ][A-Z][a-z]+){0,2}"

    patterns = [
        rf"(?:Hi|Hey|Hello|Thanks|Thank you),[ ]+({name_pattern})",  # "Hi, Dan"
        rf"(?:Hi|Hey|Hello|Thanks|Thank you)[ ]+({name_pattern})",  # "Hello Alice"
        rf"\b({name_pattern}),[ ]+(?:what|how|can|could|would|do|did|thanks)",  # "Dan, what..."
        rf"(?:As|So)[ ]+({name_pattern})[ ]+(?:mentioned|said|noted)",  # "As Dan mentioned"
        rf"(?i)(?:how|where)[ ]+is[ ]+({name_pattern})",  # "How is Alice?"
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.MULTILINE)
        for match in matches:
            match = match.strip()

            # Skip if match contains newlines (captured across lines)
            if "\r" in match or "\n" in match:
                continue

            # First check: Must be a proper noun (checks dictionary for single words)
            if not _is_proper_noun(match):
                continue

            # Second check: Must be likely a person name (not place/thing/company)
            if not _is_likely_person_name(match):
                continue

            # Passed all checks, create Name object
            logger.debug(f"Extracted name from dialogue: {match}")
            try:
                # Parse multi-word names properly
                name = Name.from_string(match)
                names.add(name)
            except ValueError:
                logger.debug(f"Skipping invalid name: {match}")

    return names


def _extract_speaker_samples(speaker: str, text: str, count: int = 3) -> list[str]:
    """Extract sample utterances from a specific speaker.

    Args:
        speaker: The speaker label
        text: The text to analyze
        count: Number of samples to extract

    Returns:
        List of sample utterances
    """
    samples: list[str] = []
    lines = text.split("\r\n")

    i = 0
    while i < len(lines) and len(samples) < count:
        line = lines[i]
        if line.startswith(f"{speaker}:"):
            # Found an utterance from this speaker
            utterance = line[len(speaker) + 1 :].strip()
            if utterance:
                samples.append(utterance)
        i += 1

    return samples


def _apply_speaker_mappings(text: str, speaker_map: dict[str, str]) -> str:
    """Apply speaker name mappings to text.

    Args:
        text: The text to modify
        speaker_map: Mapping of old speaker labels to new names

    Returns:
        Modified text with resolved speaker names
    """
    if not speaker_map:
        return text

    lines = text.split("\r\n")
    result_lines: list[str] = []

    for line in lines:
        modified_line = line
        for old_label, new_label in speaker_map.items():
            # Replace speaker labels at line start
            if line.startswith(f"{old_label}:"):
                modified_line = line.replace(f"{old_label}:", f"{new_label}:", 1)
                break
        result_lines.append(modified_line)

    return "\r\n".join(result_lines)


def _is_speaker_line(line: str, speaker_labels: list[str] | None = None) -> bool:
    """Check if a line starts with a speaker label.

    Args:
        line: The line to check
        speaker_labels: List of known speaker labels to match against.
                       If None or empty, matches any valid label pattern.

    Returns:
        True if line starts with a speaker label
    """
    if not speaker_labels:
        # Fallback to pattern matching when no speaker list provided
        pattern = r"^[A-Z][A-Za-z0-9\s]*?:\s"
        return bool(re.match(pattern, line))

    # Check if line starts with any known speaker label
    return any(line.startswith(f"{speaker}:") for speaker in speaker_labels)


def _extract_speaker_from_line(line: str) -> str | None:
    """Extract speaker label from a line.

    Args:
        line: The line to analyze

    Returns:
        The speaker label, or None if not a speaker line
    """
    pattern = r"^([A-Z][A-Za-z0-9\s]*?):\s"
    match = re.match(pattern, line)
    if match:
        return match.group(1).strip()
    return None


def _extract_names_from_line(line: str) -> set[Name]:
    """Extract potential names from a line.

    Args:
        line: The line to analyze

    Returns:
        Set of Name objects
    """
    names: set[Name] = set()

    # Remove the field label (e.g., "Attendees:")
    content = line.split(":", 1)[1] if ":" in line else line

    # Split by common separators
    parts = re.split(r"[,;]", content)

    for part in parts:
        # Clean and check if it looks like a name
        cleaned = part.strip()
        if cleaned and cleaned[0].isupper():
            # Parse as full name using Name.from_string
            try:
                name = Name.from_string(cleaned)
                names.add(name)
            except ValueError:
                # Skip invalid names (e.g., too many tokens)
                logger.debug(f"Skipping invalid name: {cleaned}")
                continue

    return names
