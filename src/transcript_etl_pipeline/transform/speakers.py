"""Speaker detection and normalization for transcript text.

This module handles speaker identification, including special logic to identify
Dan Moisan and provide UI fallback for unresolved speakers.
"""

import re
from typing import Protocol


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

    # First, try to identify Dan Moisan
    dan_label = _identify_dan_moisan(text, speaker_labels)
    if dan_label:
        speaker_map[dan_label] = "Dan Moisan"

    # Try to auto-resolve other speakers from metadata and context
    metadata_names = _extract_names_from_metadata(text)
    dialogue_names = _extract_names_from_dialogue(text)
    available_names = metadata_names | dialogue_names

    # Remove Dan Moisan from available names since we already resolved him
    available_names.discard("Dan Moisan")
    available_names.discard("Dan")

    # Try to match remaining speakers to available names
    unresolved_speakers = [s for s in speaker_labels if s not in speaker_map]
    for speaker in unresolved_speakers:
        # Try simple matching (e.g., "John" mentioned and "Speaker A" exists)
        resolved = _try_auto_match_speaker(speaker, available_names, text)
        if resolved:
            speaker_map[speaker] = resolved
            available_names.discard(resolved)

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

    for line in text.split("\r\n"):
        match = re.match(pattern, line)
        if match:
            label = match.group(1).strip()
            if label not in seen:
                labels.append(label)
                seen.add(label)

    return labels


def _identify_dan_moisan(text: str, speaker_labels: list[str]) -> str | None:
    """Identify which speaker label corresponds to Dan Moisan.

    Looks for contextual references like:
    - "Dan, what do you think?"
    - "As Dan mentioned..."

    Args:
        text: The text to analyze
        speaker_labels: List of speaker labels

    Returns:
        The speaker label for Dan Moisan, or None if not found
    """
    # If "Dan" appears as a speaker label itself, that's NOT Dan Moisan
    # We need to find references to Dan in the dialogue

    # Look for conversational references to Dan
    speakers_addressing_dan: list[str] = []
    lines = text.split("\r\n")

    for i, line in enumerate(lines):
        # Look for "Dan" in dialogue (not as a speaker label)
        if not line.startswith("Dan:") and "Dan" in line:
            # Found a reference to Dan
            # Now find which speaker said this (they are addressing Dan)
            for j in range(i, -1, -1):
                if _is_speaker_line(lines[j]):
                    speaker = _extract_speaker_from_line(lines[j])
                    if speaker and speaker != "Dan":
                        speakers_addressing_dan.append(speaker)
                    break

    # The speakers who address Dan are NOT Dan
    # So Dan is the speaker NOT in this list
    if speakers_addressing_dan:
        speakers_addressing_dan_set: set[str] = set(speakers_addressing_dan)
        for speaker in speaker_labels:
            if speaker not in speakers_addressing_dan_set and speaker != "Dan":
                # This is likely Dan
                return speaker

    return None


def _extract_names_from_metadata(text: str) -> set[str]:
    """Extract names from metadata section of transcript.

    Args:
        text: The text to analyze

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
        if _is_speaker_line(line) and _looks_like_dialogue(line):
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


def _try_auto_match_speaker(speaker_label: str, available_names: set[str], text: str) -> str | None:
    """Try to automatically match a speaker label to an available name.

    Args:
        speaker_label: The speaker label to resolve
        available_names: Set of available names to match against
        text: The full text for context

    Returns:
        The matched name, or None if no match found
    """
    # Simple heuristic: if only one name is available, use it
    if len(available_names) == 1:
        return next(iter(available_names))

    # Try to find name mentions near this speaker's utterances
    # This is a simple implementation - could be made more sophisticated
    return None


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


def _is_speaker_line(line: str) -> bool:
    """Check if a line starts with a speaker label.

    Args:
        line: The line to check

    Returns:
        True if line starts with a speaker label
    """
    pattern = r"^[A-Z][A-Za-z0-9\s]*?:\s"
    return bool(re.match(pattern, line))


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
