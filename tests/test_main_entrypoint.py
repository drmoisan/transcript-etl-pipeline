"""Unit tests for the package entrypoint."""

from __future__ import annotations

import builtins

import pytest

import transcript_etl_pipeline.__main__ as entrypoint


def test_main_delegates_to_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure entrypoint delegates to CLI main."""
    monkeypatch.setattr(entrypoint, "cli_main", lambda: 0)

    exit_codes: list[int] = []

    def _exit(code: int) -> None:
        exit_codes.append(code)
        raise SystemExit(code)

    monkeypatch.setattr(builtins, "SystemExit", SystemExit)
    monkeypatch.setattr(entrypoint.sys, "exit", _exit)

    with pytest.raises(SystemExit):
        entrypoint.main()

    assert exit_codes == [0]
