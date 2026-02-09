"""Unit tests for configuration helpers."""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from transcript_etl_pipeline import config


def test_get_config_dir_creates_directory(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure the config directory path is created and returned."""
    home_path = Path("/home/tester")
    created: dict[str, Path] = {}

    def _home() -> Path:
        return home_path

    monkeypatch.setattr(Path, "home", _home, raising=False)

    def _mkdir(self: Path, exist_ok: bool = False) -> None:  # noqa: ARG001 - signature match
        created["path"] = self

    monkeypatch.setattr(Path, "mkdir", _mkdir, raising=False)

    result = config.get_config_dir()

    assert result == home_path / ".transcript_etl"
    assert created["path"] == result


def test_load_last_output_folder_returns_none_when_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Return None if the config file does not exist."""
    monkeypatch.setattr(config, "get_config_file", lambda: Path("missing.json"))

    def _exists(self: Path) -> bool:
        return False

    monkeypatch.setattr(Path, "exists", _exists, raising=False)

    assert config.load_last_output_folder() is None


def test_load_last_output_folder_reads_valid_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """Read and validate the stored output folder."""
    config_path = Path("config.json")
    folder_path = Path("/output/folder")
    monkeypatch.setattr(config, "get_config_file", lambda: config_path)

    def _exists(self: Path) -> bool:
        return self in {config_path, folder_path}

    monkeypatch.setattr(Path, "exists", _exists, raising=False)

    payload = json.dumps({"last_output_folder": str(folder_path)})

    def _open(*_args: object, **_kwargs: object) -> io.StringIO:
        return io.StringIO(payload)

    monkeypatch.setattr("builtins.open", _open)

    assert config.load_last_output_folder() == str(folder_path)


def test_load_last_output_folder_invalid_json(monkeypatch: pytest.MonkeyPatch) -> None:
    """Return None if the config file contents are invalid."""
    config_path = Path("config.json")
    monkeypatch.setattr(config, "get_config_file", lambda: config_path)

    def _exists_all(self: Path) -> bool:
        return True

    monkeypatch.setattr(Path, "exists", _exists_all, raising=False)

    def _open_invalid(*_args: object, **_kwargs: object) -> io.StringIO:
        return io.StringIO("{bad json")

    monkeypatch.setattr("builtins.open", _open_invalid)

    assert config.load_last_output_folder() is None


def test_save_last_output_folder_writes_json(monkeypatch: pytest.MonkeyPatch) -> None:
    """Write the output folder path to the config file."""
    config_path = Path("config.json")
    monkeypatch.setattr(config, "get_config_file", lambda: config_path)

    class _NonClosingStringIO(io.StringIO):
        def close(self) -> None:
            return None

    buffer = _NonClosingStringIO()

    def _open(*args: object, **kwargs: object) -> io.StringIO:
        return buffer

    monkeypatch.setattr("builtins.open", _open)

    config.save_last_output_folder("/output/folder")

    buffer.seek(0)
    saved = json.load(buffer)
    assert saved["last_output_folder"] == "/output/folder"


def test_save_last_output_folder_ignores_os_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure save errors are swallowed as designed."""
    monkeypatch.setattr(config, "get_config_file", lambda: Path("config.json"))

    def _open(*args: object, **kwargs: object) -> io.StringIO:
        raise OSError("cannot write")

    monkeypatch.setattr("builtins.open", _open)

    config.save_last_output_folder("/output/folder")
