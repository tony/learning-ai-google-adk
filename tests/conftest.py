"""Shared fixtures for tests."""

from __future__ import annotations

import typing as t

import pytest


class FakeToolContext:
    """Minimal stand-in for ADK ToolContext in tests."""

    def __init__(self) -> None:
        self.state: dict[str, t.Any] = {}


@pytest.fixture()
def fake_tool_context() -> FakeToolContext:
    """Return a lightweight ToolContext replacement."""
    return FakeToolContext()
