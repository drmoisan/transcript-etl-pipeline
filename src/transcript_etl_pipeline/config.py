"""Configuration management for the transcript ETL pipeline.

This module handles storing and retrieving user preferences such as
the last output folder used.
"""

import json
from pathlib import Path
from typing import Any


def get_config_dir() -> Path:
    """Get the configuration directory path.

    Creates the directory if it doesn't exist.

    Returns:
        Path to the configuration directory (~/.transcript_etl/)
    """
    config_dir = Path.home() / ".transcript_etl"
    config_dir.mkdir(exist_ok=True)
    return config_dir


def get_config_file() -> Path:
    """Get the path to the main config file.

    Returns:
        Path to last_output_folder.json
    """
    return get_config_dir() / "last_output_folder.json"


def load_last_output_folder() -> str | None:
    """Load the last output folder from config.

    Returns:
        Path to the last output folder, or None if not set
    """
    config_file = get_config_file()
    if not config_file.exists():
        return None

    try:
        with open(config_file, encoding="utf-8") as f:
            data: dict[str, Any] = json.load(f)
            folder = data.get("last_output_folder")
            if folder and Path(folder).exists():
                return folder
            return None
    except (json.JSONDecodeError, OSError):
        return None


def save_last_output_folder(folder_path: str) -> None:
    """Save the last output folder to config.

    Args:
        folder_path: Path to save as the last output folder
    """
    config_file = get_config_file()
    data = {"last_output_folder": folder_path}

    try:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError:
        # Silently fail if we can't save config
        pass
