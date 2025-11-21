"""Speaker detection and normalization for transcript text.

This module handles speaker identification, including special logic to identify
Dan Moisan and provide UI fallback for unresolved speakers.
"""

import re
from typing import Protocol

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

    # Build mapping of speaker labels to resolved names
    speaker_map: dict[str, str] = {}

    # Extract all potential names from metadata and dialogue
    metadata_names = _extract_names_from_metadata(text, speaker_labels)
    dialogue_names = _extract_names_from_dialogue(text)
    available_names = metadata_names | dialogue_names

    # Build a mapping of name -> possible speakers
    name_to_speakers: dict[str, list[str]] = {}
    for name in available_names:
        candidates = _identify_speaker_by_name(text, speaker_labels, name)
        if candidates:
            name_to_speakers[name] = candidates

    # Handle Dan Moisan specially - always use full name
    if "Dan" in name_to_speakers:
        dan_candidates = name_to_speakers["Dan"]
        if len(dan_candidates) == 1:
            speaker_map[dan_candidates[0]] = "Dan Moisan"
        # Remove Dan from further processing
        del name_to_speakers["Dan"]

    # Resolve unambiguous mappings (1 name -> 1 speaker)
    for name, candidates in name_to_speakers.items():
        if len(candidates) == 1:
            speaker = candidates[0]
            if speaker not in speaker_map:  # Don't overwrite existing
                speaker_map[speaker] = name

    # Try to match remaining speakers to available names
    unresolved_speakers = [s for s in speaker_labels if s not in speaker_map]

    # For any still-unresolved speakers, use UI callback if provided
    if ui_callback:
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


def _identify_speaker_by_name(text: str, speaker_labels: list[str], name: str) -> list[str]:
    """Identify which speaker label(s) could correspond to a person by their first name.

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
        name: The first name to identify (e.g., "Dan", "John", "Alice")

    Returns:
        List of possible speaker labels for the named person
        (may be empty or contain multiple candidates)
    """
    lines = text.split("\r\n")

    # PASS 1: Direct inference - find who addresses the person
    speakers_addressing_person: list[str] = []
    direct_address_locations: list[int] = []  # Track where direct addresses occur

    for i, line in enumerate(lines):
        # Look for the name in dialogue (not as a speaker label)
        # Check if this is a direct address (not hypothetical/third-person)
        if (
            not line.lower().startswith(f"{name.lower()}:")
            and name.lower() in line.lower()
            and _is_direct_address_to_person(line, name)
        ):
            # Found a direct address to the person
            # Find which speaker said this (they are addressing the person)
            for j in range(i, -1, -1):
                if _is_speaker_line(lines[j], speaker_labels):
                    speaker = _extract_speaker_from_line(lines[j])
                    if speaker and speaker != name:
                        speakers_addressing_person.append(speaker)
                        direct_address_locations.append(i)
                    break

    # Calculate possible speakers from direct inference
    if speakers_addressing_person:
        speakers_addressing_person_set: set[str] = set(speakers_addressing_person)
        possible_speakers = [
            speaker
            for speaker in speaker_labels
            if speaker not in speakers_addressing_person_set and speaker != name
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
    name: str,
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
        name: The name being identified
        candidates: Current list of possible speakers for this name
        address_locations: Line indices where direct addresses to name occurred

    Returns:
        Refined list of candidates, or empty list if heuristics don't help
    """
    name_lower = name.lower()

    # FIRST: Exclude speakers who use third-person references
    # These speakers are definitively NOT the person
    third_person_patterns = [
        # Gendered pronouns with name
        rf"\b(her|she|she'?s)\b.*{name_lower}",
        rf"{name_lower}.*\b(her|she|she'?s)\b",
        rf"\b(his|he|he'?s)\b.*{name_lower}",
        rf"{name_lower}.*\b(his|he|he'?s)\b",
        # Possession with name
        rf"{name_lower}'?s\s+(screen|audio|connection|microphone)",
        # Status references with name
        rf"{name_lower}\s+is\s+(muted?|frozen|disconnected)",
        # Generic third-person tech references (context clue after address)
        r"\b(her|his)\s+(screen|audio|connection|microphone|video)\b",
        r"\b(she|he)\s+is\s+(muted?|frozen|disconnected)\b",
        # Generic third-person pronouns near address context
        # (If someone says "she" or "he" right after addressing the person, they're not that person)
        r"\b(she|he)\b",  # Any use of "she" or "he" is third-person
    ]

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
    candidates = _identify_speaker_by_name(text, speaker_labels, "Dan")
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


def _extract_names_from_metadata(text: str, speaker_labels: list[str] | None = None) -> set[str]:
    """Extract names from metadata section of transcript.

    Args:
        text: The text to analyze
        speaker_labels: Optional list of known speaker labels

    Returns:
        Set of names found in metadata
    """
    names: set[str] = set()
    lines = text.split("\r\n")

    # Metadata is before the first actual speaker utterance
    # Speaker lines typically have text after the colon that looks like dialogue
    in_metadata = True
    for line in lines:
        # Check if this looks like a speaker with dialogue (not metadata)
        if _is_speaker_line(line, speaker_labels) and _looks_like_dialogue(line):
            in_metadata = False
            break

        if in_metadata and any(
            keyword in line.lower() for keyword in ["attendee", "participant", "present"]
        ):
            # Extract names from the line
            found_names = _extract_names_from_line(line)
            names.update(found_names)

    return names


def _looks_like_dialogue(line: str) -> bool:
    """Check if a speaker line looks like dialogue rather than metadata.

    Args:
        line: The line to check

    Returns:
        True if this looks like actual dialogue
    """
    # Extract the content after the label
    if ":" not in line:
        return False

    label, content = line.split(":", 1)
    label = label.strip()
    content = content.strip()

    # Metadata labels we want to exclude
    metadata_keywords = [
        "attendee",
        "participant",
        "meeting",
        "date",
        "time",
        "location",
        "subject",
        "present",
        "transcript",
    ]

    # If the label itself is a metadata keyword, it's not dialogue
    if label.lower() in metadata_keywords:
        return False

    # If content is empty, not dialogue
    if not content:
        return False

    words = content.split()
    if len(words) == 0:
        return False

    # Check for common dialogue patterns
    dialogue_words = ["hello", "hi", "hey", "yes", "no", "thanks", "i", "you", "we", "what", "how"]
    first_word = words[0].lower().rstrip(",.!?")
    if first_word in dialogue_words:
        return True

    # If it has sentence punctuation, likely dialogue
    if any(content.rstrip().endswith(p) for p in [".", "?", "!"]):
        return True

    # If it's a longer phrase (more than 3 words), might be dialogue
    return len(words) > 3


def _extract_names_from_dialogue(text: str) -> set[str]:
    """Extract names mentioned in dialogue.

    Args:
        text: The text to analyze

    Returns:
        Set of names mentioned in conversations
    """
    names: set[str] = set()

    # Look for capitalized words that might be names
    # This is a simple heuristic
    pattern = r"\b([A-Z][a-z]+)\b"

    # Words to exclude (common dialogue words, not names)
    excluded_words = {
        "the",
        "this",
        "that",
        "these",
        "those",
        "what",
        "when",
        "where",
        "who",
        "why",
        "how",
        "speaker",
        "hello",
        "hi",
        "hey",
        "thanks",
        "thank",
        "yes",
        "yeah",
        "sure",
        "okay",
        "good",
        "great",
        "well",
        "now",
        "here",
        "there",
        "world",  # Common in examples
    }

    for line in text.split("\r\n"):
        # Include names from speaker lines too
        matches = re.findall(pattern, line)
        for match in matches:
            # Filter out common words that aren't names
            if match.lower() not in excluded_words:
                names.add(match)

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


def _extract_names_from_line(line: str) -> set[str]:
    """Extract potential names from a line.

    Args:
        line: The line to analyze

    Returns:
        Set of potential names
    """
    names: set[str] = set()

    # Remove the field label (e.g., "Attendees:")
    content = line.split(":", 1)[1] if ":" in line else line

    # Split by common separators
    parts = re.split(r"[,;]", content)

    for part in parts:
        # Clean and check if it looks like a name
        cleaned = part.strip()
        if cleaned and cleaned[0].isupper():
            # Simple name extraction - could be improved
            words = cleaned.split()
            for word in words:
                if word and word[0].isupper() and len(word) > 1:
                    names.add(word)

    return names
