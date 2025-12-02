"""Paragraph detection and formatting for transcript text.

Uses NLTK-powered segmentation to detect paragraph boundaries even when the
source lacks explicit speaker labels or blank lines.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any, cast

from nltk.tokenize import TextTilingTokenizer, sent_tokenize  # type: ignore[import-untyped]

__all__ = [
    "detect_paragraphs",
    "_is_label_line",
    "_ends_with_sentence_terminator",
    "_should_add_paragraph_break",
]


_sent_tokenizer_ready = False
_CONVERSATION_CUES = {
    "yes",
    "yeah",
    "yup",
    "no",
    "nope",
    "okay",
    "ok",
    "absolutely",
    "sure",
    "great",
    "right",
    "well",
    "so",
    "thanks",
    "thank",
    "totally",
    "definitely",
    "indeed",
    "awesome",
}
_MAX_PARAGRAPH_CHARS = 480


def detect_paragraphs(text: str) -> str:
    """Detect and format paragraphs in transcript text.

    Uses heuristics to identify paragraph boundaries:
    - Sentence endings (., ?, !)
    - Label boundaries (lines starting with capitalized word followed by colon)
    - Metadata termination (first label marks end of metadata)
    - Line length analysis (short lines after long lines may indicate pauses)

    Inserts CRLF after each paragraph but NOT at the very end of the document.

    Args:
        text: Normalized text with CRLF line endings

    Returns:
        Text with paragraph breaks inserted
    """
    if not text or not text.strip():
        return text

    lines = text.split("\r\n")
    result_lines: list[str] = []
    in_metadata = True
    freeform_block: list[str] = []

    def flush_block() -> None:
        if not freeform_block:
            return
        if _needs_semantic_segmentation(freeform_block):
            segments = _segment_freeform_block(freeform_block)
            _extend_with_segments(result_lines, segments)
        else:
            _append_block_with_classic_breaks(result_lines, freeform_block)
        freeform_block.clear()

    for line in lines:
        stripped = line.strip()

        if in_metadata:
            result_lines.append(line)
            if _is_label_line(line) or stripped.lower().startswith("transcript"):
                in_metadata = False
            continue

        if _is_label_line(line):
            flush_block()
            result_lines.append(line)
            continue

        if not stripped:
            flush_block()
            result_lines.append(line)
            continue

        freeform_block.append(line)

    flush_block()

    while result_lines and not result_lines[-1].strip():
        result_lines.pop()

    return "\r\n".join(result_lines)


def _is_label_line(line: str) -> bool:
    """Check if a line starts with a label (e.g., 'Speaker:', 'John:').

    Args:
        line: The line to check

    Returns:
        True if line starts with a label
    """
    # Match single-word capitalized token ending with colon at line start
    pattern = r"^[A-Z][A-Za-z0-9]*:\s"
    return bool(re.match(pattern, line))


def _should_add_paragraph_break(
    current_line: str, all_lines: list[str], current_index: int
) -> bool:
    """Determine if a paragraph break should be added after the current line.

    Args:
        current_line: The current line being processed
        all_lines: All lines in the text
        current_index: Index of current line

    Returns:
        True if a paragraph break should be added
    """
    # Empty lines don't need paragraph breaks
    if not current_line.strip():
        return False

    # Check for sentence endings
    if _ends_with_sentence_terminator(current_line):
        return True

    # Check for major pause indicator (long line followed by shorter line)
    if current_index + 1 < len(all_lines):
        next_line = all_lines[current_index + 1].strip()
        if next_line and not _is_label_line(next_line):
            current_len = len(current_line.strip())
            next_len = len(next_line)
            # If current line is long and next is significantly shorter, might be a pause
            if current_len > 60 and next_len < current_len * 0.6:
                return True

    return False


def _needs_semantic_segmentation(lines: list[str]) -> bool:
    """Determine if a block of lines requires semantic paragraphing."""

    meaningful = [line.strip() for line in lines if line.strip()]
    if not meaningful:
        return False

    if len(meaningful) == 1:
        return _has_multiple_sentences(meaningful[0])

    return any(_has_multiple_sentences(line) for line in meaningful)


def _append_block_with_classic_breaks(result_lines: list[str], block_lines: list[str]) -> None:
    """Apply the legacy line-based heuristics to a block of lines."""

    if not block_lines:
        return

    if result_lines:
        previous_line = result_lines[-1]
        if previous_line.strip():
            preview = [previous_line, block_lines[0]]
            if _should_add_paragraph_break(previous_line, preview, 0):
                result_lines.append("")

    for idx, line in enumerate(block_lines):
        result_lines.append(line)
        has_next = idx < len(block_lines) - 1
        if has_next and _should_add_paragraph_break(line, block_lines, idx):
            result_lines.append("")


def _segment_freeform_block(lines: list[str]) -> list[str]:
    """Segment a block without speaker markers into paragraphs."""

    text_block = " ".join(line.strip() for line in lines if line.strip())
    if not text_block:
        return lines

    _ensure_sentence_tokenizer()

    # Prefer TextTiling for broader semantic shifts
    try:
        tiler = TextTilingTokenizer()
        raw_segments_obj = cast(Any, tiler).tokenize(text_block)
        if isinstance(raw_segments_obj, tuple):
            candidate_segments = cast(Iterable[Any], raw_segments_obj[0])
        else:
            candidate_segments = cast(Iterable[Any], raw_segments_obj)
        raw_segments = [str(cast(object, segment)) for segment in candidate_segments]
        segments = [segment.replace("\n", " ").strip() for segment in raw_segments]
        segments = [segment for segment in segments if segment]
        if len(segments) > 1:
            return segments
    except (ValueError, LookupError):
        pass

    sentences = [sentence.strip() for sentence in sent_tokenize(text_block)]
    if not sentences:
        return [text_block]

    return _group_sentences_into_paragraphs(sentences)


def _group_sentences_into_paragraphs(sentences: list[str]) -> list[str]:
    paragraphs: list[str] = []
    current: list[str] = []
    current_chars = 0

    for index, sentence in enumerate(sentences):
        current.append(sentence)
        current_chars += len(sentence)
        next_sentence = sentences[index + 1] if index + 1 < len(sentences) else None

        if _should_break_sentence(sentence, next_sentence, current_chars):
            paragraphs.append(" ".join(current).strip())
            current = []
            current_chars = 0

    if current:
        paragraphs.append(" ".join(current).strip())

    return paragraphs


def _should_break_sentence(
    last_sentence: str, next_sentence: str | None, current_chars: int
) -> bool:
    if next_sentence is None:
        return True

    next_starts_with_cue = _starts_with_conversation_cue(next_sentence)

    if last_sentence.endswith("?") and next_starts_with_cue:
        return True

    if current_chars >= _MAX_PARAGRAPH_CHARS:
        return True

    if last_sentence.endswith("!") and next_starts_with_cue:
        return True

    if len(last_sentence) > 140 and len(next_sentence) < 60:
        return True

    return next_starts_with_cue and current_chars >= 120


def _starts_with_conversation_cue(sentence: str) -> bool:
    first_word = sentence.strip().split(" ", 1)[0].lower() if sentence.strip() else ""
    normalized = first_word.strip(',.:;!?"')
    return normalized in _CONVERSATION_CUES


def _extend_with_segments(result_lines: list[str], segments: Iterable[str]) -> None:
    for segment in segments:
        cleaned = segment.strip()
        if not cleaned:
            continue
        if result_lines and result_lines[-1] != "":
            result_lines.append("")
        result_lines.append(cleaned)


def _has_multiple_sentences(line: str) -> bool:
    _ensure_sentence_tokenizer()
    return len(sent_tokenize(line)) > 1


def _ensure_sentence_tokenizer() -> None:
    global _sent_tokenizer_ready
    if _sent_tokenizer_ready:
        return
    import nltk  # type: ignore[import-untyped]

    nltk_module = cast(Any, nltk)

    try:
        nltk_module.data.find("tokenizers/punkt")
    except LookupError:
        nltk_module.download("punkt", quiet=True)
    _sent_tokenizer_ready = True


def _ends_with_sentence_terminator(line: str) -> bool:
    """Check if a line ends with a sentence terminator.

    Args:
        line: The line to check

    Returns:
        True if line ends with ., ?, or !
    """
    stripped = line.rstrip()
    if not stripped:
        return False
    return stripped[-1] in ".?!"
