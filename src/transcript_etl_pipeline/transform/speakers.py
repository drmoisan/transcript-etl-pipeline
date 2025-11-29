"""Speaker detection and normalization for transcript text.

This module handles speaker identification, including special logic to identify
Dan Moisan and provide UI fallback for unresolved speakers.
"""

import logging
import re
from typing import Protocol

from transcript_etl_pipeline.transform import dialogue_names_deprecated
from transcript_etl_pipeline.transform.name import Name

logger = logging.getLogger(__name__)

# Legacy dialogue name extraction helpers are re-exported for backward compatibility.
# Preferred approach is extract_person_names_from_text.


def _extract_names_from_dialogue(text: str) -> set[Name]:
    """Deprecated: delegate to legacy dialogue name extractor."""

    return dialogue_names_deprecated._extract_names_from_dialogue(  # pyright: ignore[reportPrivateUsage]
        text
    )


def _extract_title_case_chains(text: str) -> list[tuple[str, int]]:
    """Deprecated: delegate to legacy dialogue title-case chain extractor."""

    return (
        dialogue_names_deprecated._extract_title_case_chains(  # pyright: ignore[reportPrivateUsage]
            text
        )
    )


def _is_likely_person_name(word_group: str) -> bool:
    """Deprecated: delegate to legacy likelihood heuristic."""

    return dialogue_names_deprecated._is_likely_person_name(  # pyright: ignore[reportPrivateUsage]
        word_group
    )


def _is_proper_noun(word_group: str) -> bool:
    """Deprecated: delegate to legacy proper-noun heuristic."""

    return dialogue_names_deprecated._is_proper_noun(  # pyright: ignore[reportPrivateUsage]
        word_group
    )


__all__ = [
    "SpeakerResolutionUI",
    "resolve_speakers",
    "_extract_generic_speaker_labels",
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
    speaker_labels = _extract_generic_speaker_labels(text)
    logger.debug(f"Found speaker labels: {speaker_labels}")

    # Build mapping of speaker labels to resolved names
    speaker_map: dict[str, str] = {}

    # Extract all potential names from metadata and dialogue
    metadata_names = _extract_names_from_metadata(text, speaker_labels)
    metadata_names.add(Name.from_string("Dan Moisan"))
    # dialogue_names = _extract_names_from_dialogue(text)
    # available_names = metadata_names | dialogue_names
    # available_names = extract_person_names_from_text(text, metadata_names)
    available_names = metadata_names.copy()
    # logger.debug(f"Metadata names: {[n.full_name for n in metadata_names]}")
    # logger.debug(f"Dialogue names: {[n.full_name for n in dialogue_names]}")
    logger.debug(f"Available names: {[n.full_name for n in available_names]}")

    # Build a mapping of Name -> possible speakers
    name_to_speakers: dict[Name, list[str]] = {}
    names_actively_ruled_out: set[Name] = set()  # Names where all speakers were excluded

    for name in available_names:
        candidates = _identify_speaker_by_name(text, speaker_labels, name)
        if candidates:
            name_to_speakers[name] = candidates
            logger.debug(f"Name '{name.full_name}' matched to speakers: {candidates}")
        else:
            # Check if name was addressed/referenced (actively ruled out)
            # vs just not mentioned
            if _was_name_referenced(text, name):
                names_actively_ruled_out.add(name)
                logger.debug(f"Name '{name.full_name}' was referenced but all speakers excluded")

    # Handle Dan Moisan specially - always use full name
    # Find any Name with first_name Dan/Daniel (using variants)
    dan_name = Name(first_name="Dan")
    resolved_dan_name: Name | None = None
    for name in list(name_to_speakers.keys()):
        if dan_name.matches(name):
            dan_candidates = name_to_speakers[name]
            if len(dan_candidates) == 1:
                speaker_map[dan_candidates[0]] = "Dan Moisan"
                logger.debug(f"Mapped Dan Moisan: {dan_candidates[0]} -> Dan Moisan")
                resolved_dan_name = name
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
    # try process of elimination ONLY if counts match exactly
    if unresolved_speakers and metadata_names:
        # Exclude names that were actively ruled out (all speakers excluded)
        # Also exclude Dan if he was already resolved
        # These names should not be available for elimination
        unused_metadata_names = [
            name
            for name in metadata_names
            if name not in name_to_speakers
            and name not in names_actively_ruled_out
            and name != resolved_dan_name
        ]
        unused_full_names = [n.full_name for n in unused_metadata_names]
        logger.debug(f"Unused metadata names (no dialogue match): {unused_full_names}")

        ruled_out_names = [n.full_name for n in names_actively_ruled_out]
        if ruled_out_names:
            logger.debug(f"Names actively ruled out (all speakers excluded): {ruled_out_names}")

        # Only use elimination if we have EXACTLY matching counts
        # This prevents incorrect automatic assignment
        if len(unresolved_speakers) == 1 and len(unused_metadata_names) == 1:
            # Exact 1:1 match - safe to map
            unused_name = unused_metadata_names[0].full_name
            speaker_map[unresolved_speakers[0]] = unused_name
            logger.debug(f"Matched by elimination (1:1): {unresolved_speakers[0]} -> {unused_name}")
            unresolved_speakers = []  # All resolved
        else:
            # Multiple possibilities or ambiguous - DO NOT auto-assign
            # Let the UI callback handle these cases
            logger.debug(
                f"Cannot auto-resolve {len(unresolved_speakers)} speaker(s) "
                f"with {len(unused_metadata_names)} unused name(s) - requiring UI input"
            )

    # For any still-unresolved speakers, use UI callback if provided
    if ui_callback:
        unresolved_speakers = [s for s in speaker_labels if s not in speaker_map]
        for speaker in unresolved_speakers:
            if speaker not in speaker_map:
                samples = _extract_speaker_samples(speaker, text, count=3)
                resolved = ui_callback(speaker, samples)
                if resolved:
                    speaker_map[speaker] = resolved
                    logger.debug(f"Resolved via UI callback: {speaker} -> {resolved}")
                else:
                    logger.debug(f"UI callback returned None for {speaker} - leaving unresolved")

    # Apply the mappings to the text
    modified_text = _apply_speaker_mappings(text, speaker_map)

    return modified_text, speaker_map


def _extract_generic_speaker_labels(text: str) -> list[str]:
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


def _was_name_referenced(text: str, name: Name) -> bool:
    """Check if a name was referenced or addressed in the dialogue.

    This helps distinguish between:
    - Names actively ruled out (referenced but all speakers excluded)
    - Names simply not mentioned (no dialogue match)

    Args:
        text: The dialogue text to check
        name: The Name object to search for

    Returns:
        True if the name was referenced/addressed in dialogue
    """
    dialog = strip_before_transcript(text)
    dialog_lower = dialog.lower()

    # Check if any name variant appears in the dialogue (not just as a speaker label)
    for variant in name.shortened_variants:
        variant_lower = variant.lower()
        # Look for the name in dialogue content (not as speaker label at line start)
        if variant_lower in dialog_lower:
            # Check that it's not just the speaker label
            lines = dialog.split("\r\n")
            for line in lines:
                line_lower = line.lower()
                if not line_lower.startswith(f"{variant_lower}:") and variant_lower in line_lower:
                    return True
    return False


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
    dialog = strip_before_transcript(text)
    lines = dialog.split("\r\n")

    # Check all name variants (first name, shortened forms)
    name_variants = name.shortened_variants

    # PASS 0: Check for self-identification patterns FIRST
    # Patterns like "this is Alice" or "Sorry, this is Alice"
    self_identifying_speakers: list[str] = []
    for line in lines:
        line_lower = line.lower()
        speaker = _extract_speaker_from_line(line)

        if speaker:
            # Check if speaker self-identifies as this person
            for variant in name_variants:
                variant_lower = variant.lower()
                # Self-identification patterns:
                # "this is <Name>", "sorry, this is <Name>", "hi, this is <Name>"
                pattern_match = re.search(rf"\bthis\s+is\s+{variant_lower}\b", line_lower)
                if pattern_match and speaker not in name_variants:
                    self_identifying_speakers.append(speaker)
                    break

    # If someone self-identifies, return them immediately
    if self_identifying_speakers:
        # Return first self-identifying speaker (most common case is one)
        return [self_identifying_speakers[0]]

    # PASS 1: Direct inference - find who addresses the person
    speakers_addressing_person: list[str] = []
    direct_address_locations: list[int] = []  # Track where direct addresses occur

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

        # Also exclude speakers who use third-person references (she/he/her/his)
        # These speakers are definitively NOT the person, regardless of other evidence
        possible_speakers = _exclude_third_person_speakers(lines, name, possible_speakers)

        # PASS 2: Proximity heuristics if multiple candidates remain
        if len(possible_speakers) > 1:
            refined_candidates = _apply_proximity_heuristics(
                lines, speaker_labels, name, possible_speakers, direct_address_locations
            )
            if refined_candidates:
                return refined_candidates

        return possible_speakers

    return []


def _exclude_third_person_speakers(
    lines: list[str], name: Name, candidates: list[str]
) -> list[str]:
    """Exclude speakers who refer to the person using third-person pronouns or constructions.

    Third-person indicators include:
    - Pronouns: she, he, her, his, she's, he's
    - Possessives: her screen, his audio, Alice's microphone
    - Status references: Alice is muted, she is frozen

    Args:
        lines: Lines of dialogue to analyze
        name: The Name object to check for third-person references
        candidates: List of candidate speakers to filter

    Returns:
        Filtered list of candidates with third-person speakers removed
    """
    name_variants_lower = [v.lower() for v in name.shortened_variants]

    # Build third-person patterns
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
    # Add generic third-person patterns (when no name variant is mentioned)
    third_person_patterns.extend(
        [
            # Generic third-person tech references
            r"\b(her|his)\s+(screen|audio|connection|microphone|video)\b",
            r"\b(she|he)\s+is\s+(muted?|frozen|disconnected)\b",
            # Generic third-person pronouns
            r"\b(she|he)\b",
        ]
    )

    # Find speakers who use third-person references
    speakers_using_third_person: set[str] = set()
    for line in lines:
        line_lower = line.lower()
        speaker = _extract_speaker_from_line(line)
        if speaker and speaker in candidates:
            for pattern in third_person_patterns:
                if re.search(pattern, line_lower):
                    speakers_using_third_person.add(speaker)
                    break

    # Filter out speakers who used third-person references
    return [c for c in candidates if c not in speakers_using_third_person]


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

    # Questions asking about someone: "Can Name...", "Does Name...", "Will Name..."
    # These indicate the speaker is asking ABOUT the person, so speaker is NOT that person
    if re.search(
        rf"\b(can|could|does|did|will|would|should|has|have)\s+{name_lower}\b", line_lower
    ):
        return True

    # Possessive references: "Name's screen", "Name's audio"
    # These indicate talking ABOUT the person, not TO them
    if re.search(rf"\b{name_lower}'?s\s+(screen|audio|connection|microphone|video)\b", line_lower):
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

    def resource_available(resource_path: str) -> bool:
        try:
            nltk.data.find(resource_path)  # type: ignore[attr-defined]
            return True
        except LookupError:
            return False

    def download_package(package_name: str, resource_path: str) -> bool:
        logger.info(f"Downloading NLTK package: {package_name}")
        with contextlib.suppress(Exception):
            nltk.download(package_name, quiet=True)  # type: ignore[attr-defined]
            if resource_available(resource_path):
                logger.info(f"Successfully downloaded NLTK package: {package_name}")
                return True
        logger.debug(f"Download of {package_name} did not make it available at {resource_path}")
        return False

    resource_variants: list[list[tuple[str, str]]] = [
        [
            ("punkt_tab", "tokenizers/punkt_tab"),  # Sentence tokenizer (newer name)
            ("punkt", "tokenizers/punkt"),  # Legacy name
        ],
        [
            (
                "averaged_perceptron_tagger_eng",
                "taggers/averaged_perceptron_tagger_eng",
            ),  # Newer tagger
            ("averaged_perceptron_tagger", "taggers/averaged_perceptron_tagger"),  # Legacy
        ],
        [
            ("maxent_ne_chunker_tab", "chunkers/maxent_ne_chunker_tab"),  # Newer chunker data
            ("maxent_ne_chunker", "chunkers/maxent_ne_chunker"),  # Legacy chunker
        ],
        [("words", "corpora/words")],  # Word corpus
    ]

    for variants in resource_variants:
        downloaded = False
        for package_name, resource_path in variants:
            if resource_available(resource_path):
                downloaded = True
                break

            if download_package(package_name, resource_path):
                downloaded = True
                break

        if not downloaded:
            logger.warning(
                "Could not download any variant of %s. NLTK functionality may be limited.",
                [pkg for pkg, _ in variants],
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
        for sentence in sentences:
            # Tokenize and POS-tag
            excluding_label = re.sub(r"([A-Za-z0-9 ]+: )", r"", sentence)
            tokens: Any = word_tokenize(excluding_label)
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
        if cleaned and cleaned[0].isalpha():
            # Normalize to title case for proper name format
            # This handles cases like "alice" -> "Alice" or "ALICE" -> "Alice"
            normalized = cleaned.title()
            # Parse as full name using Name.from_string
            try:
                name = Name.from_string(normalized)
                names.add(name)
            except ValueError:
                # Skip invalid names (e.g., too many tokens)
                logger.debug(f"Skipping invalid name: {cleaned}")
                continue

    return names
