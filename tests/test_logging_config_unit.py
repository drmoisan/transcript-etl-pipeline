"""Unit tests for logging configuration helpers."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from transcript_etl_pipeline import logging_config


class _DummyHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def test_setup_logging_without_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure console handler is configured when no file is provided."""
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    logging_config.setup_logging(log_file=None, level=logging.INFO)

    assert root_logger.level == logging.INFO
    assert len(root_logger.handlers) == 1
    assert isinstance(root_logger.handlers[0], logging.StreamHandler)


def test_setup_logging_with_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure file handler is added when a log file is specified."""
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    created: dict[str, Path] = {}

    def _mkdir(self: Path, parents: bool = False, exist_ok: bool = False) -> None:  # noqa: ARG001
        created["path"] = self

    monkeypatch.setattr(Path, "mkdir", _mkdir, raising=False)

    dummy_handler = _DummyHandler()

    def _file_handler(*_args: object, **_kwargs: object) -> _DummyHandler:
        return dummy_handler

    monkeypatch.setattr(logging, "FileHandler", _file_handler)

    logging_config.setup_logging(log_file="logs/output.log", level=logging.DEBUG)

    assert root_logger.level == logging.DEBUG
    assert len(root_logger.handlers) == 2
    assert dummy_handler in root_logger.handlers
    assert created["path"].name == "logs"


def test_get_logger_returns_named_logger() -> None:
    """Ensure get_logger returns the expected named logger."""
    logger = logging_config.get_logger("transcript_etl_pipeline.test")
    assert logger.name == "transcript_etl_pipeline.test"
