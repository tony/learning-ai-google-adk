"""Shared fixtures for tests."""

from __future__ import annotations

import typing as t

import pytest


class FakeContext:
    """Minimal stand-in for ADK Context in tests."""

    def __init__(self) -> None:
        self.state: dict[str, t.Any] = {}


@pytest.fixture()
def fake_tool_context() -> FakeContext:
    """Return a lightweight Context replacement."""
    return FakeContext()
