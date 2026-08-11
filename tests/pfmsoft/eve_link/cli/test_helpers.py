"""Tests for CLI helper utilities."""

from pathlib import Path
from types import SimpleNamespace

import pytest
import typer

from pfmsoft.eve_link.cli import helpers
from pfmsoft.eve_link.settings import SETTINGS_KEY, EsiLinkSettings, get_settings


class _FakeStdin:
    """Simple stdin stub with controllable TTY behavior."""

    def __init__(self, text: str, *, is_tty: bool) -> None:
        self._text = text
        self._is_tty = is_tty

    def isatty(self) -> bool:
        """Report whether stdin is interactive."""
        return self._is_tty

    def read(self) -> str:
        """Return the prepared stdin payload."""
        return self._text


class _FakeConsole:
    """Collect console messages for assertions."""

    def __init__(self) -> None:
        self.messages: list[str] = []

    def print(self, message: str) -> None:
        """Store printed messages."""
        self.messages.append(message)


class _FakeSchemaManager:
    """Minimal schema cache manager stub for get_schema tests."""

    def __init__(
        self,
        *,
        entries: list[SimpleNamespace] | None = None,
        loaded: dict[str, object] | None = None,
        load_error: Exception | None = None,
    ) -> None:
        self._entries = entries or []
        self._loaded = loaded or {}
        self._load_error = load_error
        self.load_calls: list[str] = []

    def list_entries(self) -> list[SimpleNamespace]:
        """Return configured cache entries."""
        return self._entries

    def load(self, *, compatibility_date: str) -> object:
        """Load a schema or raise the configured error."""
        self.load_calls.append(compatibility_date)
        if self._load_error is not None:
            raise self._load_error
        return self._loaded[compatibility_date]


@pytest.fixture
def settings(tmp_path: Path) -> EsiLinkSettings:
    """Build EsiLink settings rooted in the pytest temp directory."""
    application_directory = tmp_path / "app"
    return get_settings(application_directory=application_directory)


def test_get_stdin_reads_non_interactive_input(monkeypatch: pytest.MonkeyPatch) -> None:
    """Return piped stdin content when stdin is not a TTY."""
    monkeypatch.setattr(helpers.sys, "stdin", _FakeStdin("payload", is_tty=False))

    assert helpers.get_stdin() == "payload"


def test_get_stdin_rejects_interactive_terminal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Require a file or pipe instead of interactive stdin."""
    monkeypatch.setattr(helpers.sys, "stdin", _FakeStdin("", is_tty=True))

    with pytest.raises(ValueError, match="pipe data via stdin"):
        helpers.get_stdin()


def test_get_eve_link_settings_from_context_returns_stored_settings(
    settings: EsiLinkSettings,
) -> None:
    """Read the app settings from the Typer context object."""
    ctx = SimpleNamespace(obj={SETTINGS_KEY: settings})

    assert helpers.get_eve_link_settings_from_context(ctx) is settings
