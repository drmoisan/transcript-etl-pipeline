"""Pytest configuration for shared test fixtures."""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

import pytest


def _fallback_sent_tokenize(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text.strip())
    if not normalized:
        return []
    parts = re.split(r"(?<=[.!?])\s+", normalized)
    return [part.strip() for part in parts if part.strip()]


def _fallback_word_tokenize(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    normalized = re.sub(r"\b(you|i)('ll|'ve|'re|'d|n't)\b", r"\1", normalized)
    normalized = re.sub(r"\b(i)'m\b", r"\1", normalized)
    return [token.strip(".,!?;:\"'()[]{}") for token in normalized.split() if token]


def _apply_monkeypatches(monkeypatch: pytest.MonkeyPatch) -> None:
    import nltk  # type: ignore[import-untyped]

    def _find(_path: str) -> str:
        return "/nonexistent"

    def _download(*_args: Any, **_kwargs: Any) -> bool:
        return True

    monkeypatch.setattr(nltk.data, "find", _find, raising=True)
    monkeypatch.setattr(nltk, "download", _download, raising=True)
    monkeypatch.setattr(nltk, "sent_tokenize", _fallback_sent_tokenize, raising=True)
    monkeypatch.setattr(nltk, "word_tokenize", _fallback_word_tokenize, raising=True)

    def _pos_tag(tokens: list[str]) -> list[tuple[str, str]]:
        return [(token, "PRP") for token in tokens]

    monkeypatch.setattr(nltk, "pos_tag", _pos_tag, raising=True)

    from nltk import tokenize as nltk_tokenize  # type: ignore[import-untyped]

    monkeypatch.setattr(nltk_tokenize, "sent_tokenize", _fallback_sent_tokenize, raising=False)
    monkeypatch.setattr(nltk_tokenize, "word_tokenize", _fallback_word_tokenize, raising=False)

    _patch_project_tokenizers(monkeypatch)


def _patch_project_tokenizers(monkeypatch: pytest.MonkeyPatch) -> None:
    import transcript_etl_pipeline.transform.paragraphs as paragraphs

    monkeypatch.setattr(paragraphs, "sent_tokenize", _fallback_sent_tokenize, raising=False)
    monkeypatch.setattr(paragraphs, "_sent_tokenizer_ready", True, raising=False)

    class _DummyTextTilingTokenizer:
        def tokenize(self, text: str) -> list[str]:
            return [text]

    monkeypatch.setattr(paragraphs, "TextTilingTokenizer", _DummyTextTilingTokenizer, raising=False)

    import transcript_etl_pipeline.transform.speaker_helpers as speaker_helpers

    monkeypatch.setattr(speaker_helpers, "_sent_tokenizer_ready", True, raising=False)

    def _ensure_sentence_tokenizer() -> None:
        return None

    monkeypatch.setattr(
        speaker_helpers,
        "ensure_sentence_tokenizer",
        _ensure_sentence_tokenizer,
        raising=False,
    )


@pytest.fixture(autouse=True)
def _mock_nltk_tokenizers(  # pyright: ignore[reportUnusedFunction]
    monkeypatch: pytest.MonkeyPatch,
) -> Iterable[None]:
    """Patch NLTK tokenizers to avoid network downloads in tests."""
    _apply_monkeypatches(monkeypatch)
    yield
