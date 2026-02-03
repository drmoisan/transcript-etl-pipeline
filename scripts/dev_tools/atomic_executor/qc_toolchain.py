"""
Shared QC toolchain definitions for atomic executor.

Defines step names, command templates, and plan-detection patterns for
supported toolchains (Python and TypeScript).
"""

from __future__ import annotations

import re
from enum import Enum


class QCToolchain(str, Enum):
    """Supported QC toolchains."""

    PYTHON = "python"
    TYPESCRIPT = "typescript"


PYTHON_TOOLCHAIN_STEPS: tuple[str, ...] = ("black", "ruff", "pyright", "pytest")
TYPESCRIPT_TOOLCHAIN_STEPS: tuple[str, ...] = (
    "format",
    "lint",
    "typecheck",
    "test-unit",
)

PYTHON_QC_STEP_PATTERNS: dict[str, re.Pattern[str]] = {
    "black": re.compile(r"poetry\s+run\s+black\b", re.IGNORECASE),
    "ruff": re.compile(r"poetry\s+run\s+ruff\s+check\b", re.IGNORECASE),
    "pyright": re.compile(r"poetry\s+run\s+pyright\b", re.IGNORECASE),
    "pytest": re.compile(r"poetry\s+run\s+pytest\b", re.IGNORECASE),
}

TYPESCRIPT_QC_STEP_PATTERNS: dict[str, re.Pattern[str]] = {
    "format": re.compile(r"npm\s+run\s+format\b", re.IGNORECASE),
    "lint": re.compile(r"npm\s+run\s+lint\b", re.IGNORECASE),
    "typecheck": re.compile(r"npm\s+run\s+typecheck\b", re.IGNORECASE),
    "test-unit": re.compile(r"npm\s+run\s+test:unit\b", re.IGNORECASE),
}

PYTHON_TOOLCHAIN_COMMANDS: dict[str, list[str]] = {
    "black": ["poetry", "run", "black", "--check", "."],
    "ruff": ["poetry", "run", "ruff", "check"],
    "pyright": ["poetry", "run", "pyright"],
    "pytest": [
        "poetry",
        "run",
        "pytest",
        "--color=no",
        "--cov=src/lexile_corpus_tuner",
        "--cov=scripts/dev_tools",
        "--cov-report=term-missing",
    ],
}

TYPESCRIPT_TOOLCHAIN_COMMANDS: dict[str, list[str]] = {
    "format": ["npm", "run", "format"],
    "lint": ["npm", "run", "lint"],
    "typecheck": ["npm", "run", "typecheck"],
    "test-unit": ["npm", "run", "test:unit"],
}

TOOLCHAIN_STEPS: dict[QCToolchain, tuple[str, ...]] = {
    QCToolchain.PYTHON: PYTHON_TOOLCHAIN_STEPS,
    QCToolchain.TYPESCRIPT: TYPESCRIPT_TOOLCHAIN_STEPS,
}

TOOLCHAIN_PATTERNS: dict[QCToolchain, dict[str, re.Pattern[str]]] = {
    QCToolchain.PYTHON: PYTHON_QC_STEP_PATTERNS,
    QCToolchain.TYPESCRIPT: TYPESCRIPT_QC_STEP_PATTERNS,
}

TOOLCHAIN_COMMANDS: dict[QCToolchain, dict[str, list[str]]] = {
    QCToolchain.PYTHON: PYTHON_TOOLCHAIN_COMMANDS,
    QCToolchain.TYPESCRIPT: TYPESCRIPT_TOOLCHAIN_COMMANDS,
}
