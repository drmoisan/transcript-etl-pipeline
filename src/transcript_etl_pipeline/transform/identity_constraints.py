"""Identity constraint extraction for speaker detection.

This module provides shared utilities for detecting identity information
in transcripts, used by both speakerless.py and speakers.py modules.

Identity constraints represent hard rules about speaker assignments:
1. Self-identification: "I'm [Name]" means speaker IS [Name]
2. Addresses-other: "Thanks [Name]" means speaker is NOT [Name]

These constraints are used to:
- Guide similarity-based speaker grouping (speakerless.py)
- Resolve speaker labels to actual names (speakers.py)
"""

import logging
import re
from dataclasses import dataclass
from typing import Literal

logger = logging.getLogger(__name__)

__all__ = [
    "IdentityConstraint",
    "extract_identity_constraints",
    "detect_self_identification",
    "detect_addresses_to_person",
]


@dataclass(frozen=True)
class IdentityConstraint:
    """Represents a hard constraint on speaker identity.

    Attributes:
        sentence_idx: Index of the sentence containing this constraint
        constraint_type: Type of constraint:
            - "self_identification": Speaker identifies as this name
            - "addresses_other": Speaker addresses someone else by this name
        name: The name referenced in the constraint
    """

    sentence_idx: int
    constraint_type: Literal["self_identification", "addresses_other"]
    name: str

    def __post_init__(self) -> None:
        """Validate constraint fields."""
        if self.sentence_idx < 0:
            raise ValueError(f"sentence_idx must be non-negative, got {self.sentence_idx}")
        if not self.name or not self.name.strip():
            raise ValueError("name cannot be empty")


def detect_self_identification(sentence: str) -> str | None:
    """Detect if a sentence contains self-identification.

    Patterns detected:
    - "I'm [Name]"
    - "I am [Name]"
    - "My name is [Name]"
    - "This is [Name]" (phone/intro context)

    Args:
        sentence: The sentence to analyze

    Returns:
        The identified name, or None if no self-identification found
    """
    # Patterns for self-identification
    # Match capitalized names (first + optional last name)
    # Use word boundaries and stop at common sentence connectors
    patterns = [
        r"(?:i'm|i am)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)(?:\s+and\b|\s+from\b|[,.]|\s*$)",
        r"my name is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)(?:\s+and\b|\s+from\b|[,.]|\s*$)",
        r"this is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)(?:\s+calling\b|\s+from\b|[,.]|\s*$)",
    ]

    for pattern in patterns:
        match = re.search(pattern, sentence, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            # Verify it's actually capitalized (not all lowercase match)
            if name and name[0].isupper():
                return name

    return None


def detect_addresses_to_person(sentence: str) -> list[str]:
    """Detect if a sentence addresses someone by name.

    Direct address patterns:
    - "Name, what..." (vocative with comma at start)
    - "..., Name." (vocative with comma at end)
    - "Thanks, Name" or "Thank you, Name"
    - "Name mentioned/said..." (attribution)

    NOT direct address (excluded patterns):
    - "is Name a..." (third-person question)
    - "if ... is Name" (conditional/hypothetical)
    - "Is Name ..." (question about Name, not to Name)
    - Self-identification sentences ("I'm Name", "My name is Name")

    Args:
        sentence: The sentence to analyze

    Returns:
        List of names being directly addressed (may be empty)
    """
    sentence_lower = sentence.lower().strip()
    addressed_names: list[str] = []

    # Skip sentences that contain self-identification patterns
    # The speaker cannot be addressing themselves by name in these cases
    if detect_self_identification(sentence) is not None:
        return []

    # Extract potential capitalized names from the sentence
    # Match: Capital letter followed by lowercase letters, optional additional names
    # But exclude common non-name words that are capitalized
    name_pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b"
    potential_names: list[str] = re.findall(name_pattern, sentence)

    # Filter out common non-name capitalized words and phrases starting with them
    excluded_first_words = {
        "Thanks",
        "Thank",
        "Hello",
        "Hi",
        "Hey",
        "Good",
        "Morning",
        "Afternoon",
        "Evening",
        "Yes",
        "No",
        "Sure",
        "Ok",
        "Okay",
        "Great",
        "Perfect",
        "Excellent",
        "Welcome",
        "Let",
        "Who",
        "What",
        "Where",
        "When",
        "Why",
        "How",
        "My",
        "I",
        "You",
        "We",
        "They",
        "Oh",
        "Well",
        "Now",
    }

    # Filter out excluded words and phrases
    filtered_names: list[str] = []
    for name in potential_names:
        first_word = name.split()[0]
        # Skip if first word is an excluded word
        if first_word in excluded_first_words:
            # But check if there's a valid name after the excluded word
            # e.g., "Thanks Frank" -> we want "Frank"
            parts = name.split()
            if len(parts) > 1:
                # Add the remaining parts as the name
                remaining = " ".join(parts[1:])
                if remaining and remaining not in excluded_first_words:
                    filtered_names.append(remaining)
            continue
        if len(name) < 2:
            continue
        # Check if this is a standalone question like "Fred?"
        if " " not in name and re.search(rf"\b{re.escape(name)}\s*\?\s*$", sentence):
            continue
        filtered_names.append(name)
    potential_names = filtered_names

    if not potential_names:
        return []

    for name in potential_names:
        name_lower = name.lower()

        # Exclude third-person questions about the person
        # Pattern: "is Name [article] [noun]" like "is Dan a leader"
        if re.search(rf"\bis {name_lower} (a|an|the)\b", sentence_lower):
            continue

        # Exclude questions that start with "Is Name"
        # These are questions ABOUT the person, not TO them
        if re.search(rf"^\s*is {name_lower}\b", sentence_lower):
            continue

        # Exclude hypothetical framing
        hypothetical_markers = [
            r"if you were to say",
            r"if someone were to ask",
            rf"the question is.*{name_lower}",
            rf"you might ask.*{name_lower}",
            rf"one might say.*{name_lower}",
        ]
        is_hypothetical = False
        for marker in hypothetical_markers:
            if re.search(marker, sentence_lower):
                is_hypothetical = True
                break
        if is_hypothetical:
            continue

        # Check for direct address patterns
        is_direct_address = False

        # "Name, " with vocative comma
        if (
            re.search(rf"\b{name_lower},\s", sentence_lower)
            or re.search(
                rf"^\s*{name_lower}\s+(what|where|when|why|how|who|can|could|would|will|tell|explain|show)",
                sentence_lower,
            )
            or re.search(rf",\s*{name_lower}[.,!?]?\s*$", sentence_lower)
            or re.search(rf"\b(thanks|thank you),?\s+{name_lower}\b", sentence_lower)
            or re.search(
                rf"\b{name_lower}\s+(mentioned|said|thinks|believes|suggested)\b",
                sentence_lower,
            )
        ):
            is_direct_address = True

        # Questions asking about someone: "Can Name...", "Does Name...", "Will Name..."
        # Note: This is asking ABOUT the person, but for constraint purposes, it indicates
        # the speaker is NOT that person, which is the same as addressing them.
        # However, this might be too broad. Let's be more conservative and NOT include this
        # pattern in addresses_to_person, as it's more of a "mentions" pattern.
        # Commenting out for now:
        # elif re.search(
        #     rf"\b(can|could|does|did|will|would|should|has|have)\s+{name_lower}\b",
        #     sentence_lower,
        # ):
        #     is_direct_address = True

        if is_direct_address:
            addressed_names.append(name)

    return addressed_names


def extract_identity_constraints(sentences: list[str]) -> list[IdentityConstraint]:
    """Extract all identity constraints from a list of sentences.

    Detects both:
    1. Self-identifications: "I'm Peter Parker" → speaker IS Peter Parker
    2. Addresses to others: "Thanks Frank" → speaker is NOT Frank

    Args:
        sentences: List of sentences to analyze

    Returns:
        List of IdentityConstraint objects representing hard rules about speakers
    """
    constraints: list[IdentityConstraint] = []

    for i, sentence in enumerate(sentences):
        # Check for self-identification
        self_name = detect_self_identification(sentence)
        if self_name:
            constraints.append(
                IdentityConstraint(
                    sentence_idx=i, constraint_type="self_identification", name=self_name
                )
            )

        # Check for addresses to others
        addressed_names = detect_addresses_to_person(sentence)
        for name in addressed_names:
            constraints.append(
                IdentityConstraint(sentence_idx=i, constraint_type="addresses_other", name=name)
            )

    return constraints
