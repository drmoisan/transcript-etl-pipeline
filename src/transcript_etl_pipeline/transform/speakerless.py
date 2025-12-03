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

from transcript_etl_pipeline.transform.identity_constraints import (
    extract_identity_constraints,
)
from transcript_etl_pipeline.transform.speaker_helpers import (
    analyze_pronoun_patterns,
    detect_dialogue_markers,
    group_sentences_by_similarity,
    resolve_addresses_other_violations,
    tokenize_into_sentences,
)

logger = logging.getLogger(__name__)

# Number of characters to check at start of sentence for first-person pronouns
SENTENCE_START_CHECK_LENGTH = 10

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


def _is_rhetorical_question(sentence: str, sentences: list[str], current_idx: int) -> bool:
    """Check if a sentence is a rhetorical question continuing from the same speaker.

    Rhetorical questions are short questions that don't expect a response and
    are often followed by a continuation from the same speaker. Examples:
    - "Right?" followed by "And the booster..."
    - "You know?" followed by a continuation
    - "Isn't it?" tag questions

    Args:
        sentence: The current sentence
        sentences: All sentences in the transcript
        current_idx: Index of the current sentence

    Returns:
        True if the sentence appears to be a rhetorical question
    """
    sentence_lower = sentence.lower().strip()

    # Check if it's a short question (likely rhetorical or tag question)
    word_count = len(sentence.split())
    is_question = sentence.endswith("?")

    # Short questions (1-3 words) that are likely rhetorical
    rhetorical_patterns = [
        "right?",
        "right!?",
        "you know?",
        "isn't it?",
        "don't you think?",
        "wouldn't you say?",
        "know what i mean?",
        "see what i mean?",
        "huh?",
        "yeah?",
        "no?",
        "true?",
    ]

    # Check for explicit rhetorical patterns
    for pattern in rhetorical_patterns:
        if sentence_lower == pattern or sentence_lower.endswith(f" {pattern}"):
            return True

    # Short questions (1-3 words) followed by continuation words are likely rhetorical
    if is_question and word_count <= 3 and current_idx + 1 < len(sentences):
        # Check if next sentence starts with continuation words
        next_sentence = sentences[current_idx + 1].lower().strip()
        continuation_starters = ["and", "but", "so", "also", "plus", "i mean", "like"]
        for starter in continuation_starters:
            if next_sentence.startswith(starter + " ") or next_sentence.startswith(starter + ","):
                return True

    return False


def _detect_topic_shift(prev_sentence: str, curr_sentence: str) -> bool:
    """Detect if there's a topic or focus shift between sentences.

    This heuristic detects when a new speaker might be starting by looking for:
    1. Contrastive personal experience ("I missed it" after descriptions)
    2. New first-person experience after third-person or general statements
    3. Shift from one personal experience to a different one

    Args:
        prev_sentence: The previous sentence
        curr_sentence: The current sentence

    Returns:
        True if a topic shift is detected that might indicate a new speaker
    """
    prev_lower = prev_sentence.lower()
    curr_lower = curr_sentence.lower()

    # Don't detect topic shift for very short sentences - they're usually continuations
    # "Oh, interesting." + "I didn't know that." should stay together
    if len(prev_lower.split()) <= 5:
        return False

    # Contrastive patterns suggesting a different speaker sharing their experience
    # "I missed it" or "I wasn't able to" after someone else talked suggests new speaker
    contrastive_starters = [
        "i missed",
    ]

    for starter in contrastive_starters:
        # Combine conditions: starts with contrastive starter AND previous doesn't have "i"
        if (
            curr_lower.startswith(starter)
            and "i " not in prev_lower[:SENTENCE_START_CHECK_LENGTH]
            and not prev_lower.startswith("i")
        ):
            return True

    return False


def _is_continuation_after_question(
    prev_sentence: str, curr_sentence: str, prev_is_question: bool
) -> bool:
    """Check if current sentence is a continuation from the same speaker after a question.

    When a speaker asks a question and then immediately follows with their own
    statement, this is NOT a speaker change. Examples:
    - "Did you see that? I thought it was amazing."
    - "What do you think? I personally believe..."
    - "Do you remember when...? It was headline news."

    This pattern is common when someone:
    1. Asks a question to others
    2. Then shares their own perspective before others respond
    3. Continues answering their own rhetorical question

    Args:
        prev_sentence: The previous sentence
        curr_sentence: The current sentence
        prev_is_question: Whether the previous sentence was a question

    Returns:
        True if the current sentence is likely a continuation from the same speaker
    """
    if not prev_is_question:
        return False

    prev_lower = prev_sentence.lower()
    curr_lower = curr_sentence.lower()

    # Check if the question was addressed to others (contains "you" or names)
    has_you_in_question = " you " in prev_lower or prev_lower.endswith(" you?")

    # Pattern 1: If the previous question addressed others and current sentence starts with "I"
    # it's likely the same speaker continuing (sharing their own experience after asking)
    starts_with_i = curr_lower.startswith("i ") or curr_lower.startswith("i'")
    if has_you_in_question and starts_with_i:
        return True

    # Pattern 2: Rhetorical question followed by the speaker's own answer
    # "Do you remember when X happened? It was Y."
    # Check if it's a statement that could be answering the question
    is_memory_question = "remember" in prev_lower or "recall" in prev_lower
    is_context_answer = (
        curr_lower.startswith("it was")
        or curr_lower.startswith("it's")
        or curr_lower.startswith("that was")
    )
    return bool(is_memory_question and is_context_answer)


def detect_speaker_changes(text: str) -> list[int]:
    """Detect potential speaker change points in unlabeled text.

    Uses sentence-based analysis to identify where speaker changes likely occur.
    This works on both multi-line text AND continuous text blocks without newlines.

    Heuristics applied at sentence level:
    1. Pronoun shift patterns (I/you exchanges)
    2. Question-answer sequences
    3. Dialogue markers (greetings, acknowledgments)
    4. Thank you / appreciation patterns (often signal speaker change)
    5. Rhetorical question suppression (prevents false positives)
    6. Continuation after question detection (same speaker continues)

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
    prev_was_rhetorical = False

    for i in range(1, len(sentences)):
        is_speaker_change = False
        triggered_by = ""

        sentence = sentences[i]
        prev_sentence = sentences[i - 1]
        curr_patterns = pronoun_patterns[i] if i < len(pronoun_patterns) else {}
        prev_patterns = pronoun_patterns[i - 1] if i - 1 < len(pronoun_patterns) else {}

        # Get question status from pattern analysis (more reliable)
        prev_is_question = prev_patterns.get("is_question", 0) > 0
        curr_is_question = curr_patterns.get("is_question", 0) > 0

        # Check for continuation after question (same speaker continues)
        # This must be checked BEFORE pronoun shift to prevent false positives
        is_continuation = _is_continuation_after_question(prev_sentence, sentence, prev_is_question)

        # Heuristic 1: Pronoun shift
        # If previous sentence had "I" and current has "you" or vice versa.
        # We add a check to ensure the current sentence doesn't ALSO contain the
        # pronoun from the previous sentence, which would suggest continuity.
        curr_first = curr_patterns.get("first_person", 0)
        curr_second = curr_patterns.get("second_person", 0)
        prev_first = prev_patterns.get("first_person", 0)
        prev_second = prev_patterns.get("second_person", 0)

        # Shift I -> You (Speaker A talks about self -> Speaker B talks about A)
        # Requires current sentence to NOT have first person (otherwise it's likely A continuing)
        i_to_you = prev_first > 0 and curr_second > 0 and curr_first == 0

        # Shift You -> I (Speaker A talks about B -> Speaker B talks about self)
        # Requires current sentence to NOT have second person (otherwise it's likely A continuing)
        you_to_i = prev_second > 0 and curr_first > 0 and curr_second == 0

        # Additional check: if current is a follow-up question from the same speaker
        # Pattern: "I [statement]" followed by "Did you notice..."
        # This is the same speaker asking a question after making a statement
        is_followup_question = False
        if i_to_you and curr_is_question:
            # Check if current sentence is a follow-up question pattern
            sentence_lower = sentence.lower().strip()
            followup_question_starters = [
                "did either of you",
                "did you",
                "do you",
                "have you",
                "what do you think",
                "don't you think",
            ]
            for starter in followup_question_starters:
                if sentence_lower.startswith(starter):
                    is_followup_question = True
                    break

        # Only apply pronoun shift if NOT a continuation after question
        # and NOT a follow-up question from the same speaker
        if (i_to_you or you_to_i) and not is_continuation and not is_followup_question:
            is_speaker_change = True
            triggered_by = "pronoun_shift"

        # Heuristic 2: Question-answer pattern
        # If previous sentence was a question and current is not
        # BUT: Skip if previous was a rhetorical question
        # BUT: Also skip if this is a continuation after question (same speaker)
        if (
            prev_is_question
            and not curr_is_question
            and not prev_was_rhetorical
            and not is_continuation
        ):
            is_speaker_change = True
            triggered_by = "question_answer"

        # Heuristic 3: Dialogue markers
        markers = detect_dialogue_markers(sentence)
        if markers["is_greeting"]:
            is_speaker_change = True
            triggered_by = "greeting"
        if markers["is_acknowledgment"]:
            is_speaker_change = True
            triggered_by = "acknowledgment"
        if (
            markers["is_response"]
            and prev_is_question
            and not prev_was_rhetorical
            and not is_continuation
        ):
            is_speaker_change = True
            triggered_by = "response"

        # Heuristic 4: Thank you patterns often indicate speaker change
        sentence_lower = sentence.lower().strip()
        if sentence_lower.startswith("thank you") or sentence_lower.startswith("thanks"):
            is_speaker_change = True
            triggered_by = "thank_you"

        # Heuristic 5: "That's" patterns often respond to previous speaker
        if sentence_lower.startswith("that's "):
            is_speaker_change = True
            triggered_by = "thats_response"

        # Heuristic 6: Topic shift detection (contrastive personal experience)
        # This detects when a new speaker might be starting to share their experience
        if not is_speaker_change and _detect_topic_shift(prev_sentence, sentence):
            is_speaker_change = True
            triggered_by = "topic_shift"

        # Check for rhetorical question - may override speaker change
        curr_is_rhetorical = _is_rhetorical_question(sentence, sentences, i)

        # Suppress speaker change if this is a continuation after a rhetorical question
        if prev_was_rhetorical and triggered_by == "question_answer":
            is_speaker_change = False
            logger.debug(
                f"Sentence {i}: Suppressed change after rhetorical question: "
                f"'{sentence[:50]}...'"
            )

        # Record change point if detected
        if is_speaker_change:
            change_points.append(i)
            logger.debug(
                f"Sentence {i}: Speaker change detected ({triggered_by}): " f"'{sentence[:50]}...'"
            )

        # Update for next iteration
        prev_was_rhetorical = curr_is_rhetorical

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

    # Calculate assignments for all sentences
    assignments: list[int] = []

    if num_speakers == 2:
        # For 2 speakers, use simple alternating assignment
        current_speaker_idx = 0
        change_set = set(change_points)

        for i in range(len(sentences)):
            if i in change_set and i > 0:
                # Speaker change detected - switch to other speaker
                current_speaker_idx = (current_speaker_idx + 1) % 2
            assignments.append(current_speaker_idx)
    else:
        # For 3+ speakers, use similarity-based grouping
        # This helps cluster similar-sounding sentences to the same speaker
        # Extract identity constraints to prevent grouping conflicting speakers
        constraints = extract_identity_constraints(sentences)
        assignments = group_sentences_by_similarity(
            sentences, change_points, num_speakers, constraints
        )

        # Ensure assignments is a mutable list and matches sentence count
        assignments = list(assignments)
        if len(assignments) < len(sentences):
            assignments.extend([0] * (len(sentences) - len(assignments)))

        # Phase 3: Fix "addresses_other" violations FIRST
        # This post-processing fixes cases where someone is assigned to speak
        # a sentence that addresses them by name (e.g., "Thanks Frank" assigned to Frank)
        # We do this BEFORE enforcing speaker changes to avoid conflicts
        assignments = resolve_addresses_other_violations(
            sentences, assignments, constraints, num_speakers
        )

        # Enforce speaker changes at detected change points
        # The similarity grouping might cluster adjacent segments to the same speaker
        # if they are short or semantically similar, but we must respect the
        # detected change points.
        # NOTE: This runs AFTER post-processing to avoid conflicts with identity-based reassignments

        # Sort change points to process segments sequentially
        sorted_changes = sorted(list(set(change_points)))
        if 0 not in sorted_changes:
            sorted_changes.insert(0, 0)

        for k in range(1, len(sorted_changes)):
            seg_start = sorted_changes[k]
            prev_seg_start = sorted_changes[k - 1]

            # Get speaker for previous segment
            prev_speaker = assignments[prev_seg_start]

            # Get speaker for current segment
            curr_speaker = assignments[seg_start]

            if curr_speaker == prev_speaker:
                # Conflict: Adjacent segments have same speaker despite change point.
                # However, if post-processing assigned them to the same speaker for
                # a good reason (e.g., both are from the meeting organizer), we should
                # respect that assignment.

                # Check if this change would violate identity constraints
                # If the segment contains a self-identification, we cannot reassign it
                next_change = (
                    sorted_changes[k + 1] if k + 1 < len(sorted_changes) else len(sentences)
                )

                # Check for self-identification constraints in BOTH segments
                curr_has_self_id = False
                prev_identity = None
                curr_identity = None

                for constraint in constraints:
                    if constraint.constraint_type == "self_identification":
                        if prev_seg_start <= constraint.sentence_idx < seg_start:
                            prev_identity = constraint.name.split()[0]
                        elif seg_start <= constraint.sentence_idx < next_change:
                            curr_has_self_id = True
                            curr_identity = constraint.name.split()[0]

                # If both segments have the SAME identity, don't force a change
                # (they're actually the same person)
                if prev_identity and curr_identity and prev_identity == curr_identity:
                    continue

                # If current segment has a self-identification, don't reassign it
                if curr_has_self_id:
                    continue

                # Check if current segment contains closing/acknowledgment statements
                # that were intentionally assigned to the organizer by post-processing
                is_closing_segment = False
                for idx in range(seg_start, next_change):
                    sent = sentences[idx].strip().lower()
                    if ("great" in sent or "thank" in sent or "perfect" in sent) and len(
                        sent.split()
                    ) <= 4:
                        is_closing_segment = True
                        break

                # Don't force a change for closing statements
                if is_closing_segment:
                    continue

                # Force a change by rotating to the next speaker ID
                new_speaker = (prev_speaker + 1) % num_speakers

                # Update all sentences in this segment
                for j in range(seg_start, next_change):
                    assignments[j] = new_speaker

    # Build result with grouped sentences
    result_lines: list[str] = []
    current_speaker_idx = -1
    current_block: list[str] = []

    for i, sentence in enumerate(sentences):
        speaker_idx = assignments[i] if i < len(assignments) else 0

        if speaker_idx != current_speaker_idx:
            # Flush previous block
            if current_block:
                speaker_label = f"Speaker {speaker_labels[current_speaker_idx]}"
                result_lines.append(f"{speaker_label}: {' '.join(current_block)}")

            # Start new block
            current_speaker_idx = speaker_idx
            current_block = [sentence.strip()]
        else:
            # Continue current block
            current_block.append(sentence.strip())

    # Flush final block
    if current_block:
        speaker_label = f"Speaker {speaker_labels[current_speaker_idx]}"
        result_lines.append(f"{speaker_label}: {' '.join(current_block)}")

    # Convert to CRLF for consistency with rest of pipeline
    return "\r\n".join(result_lines)
