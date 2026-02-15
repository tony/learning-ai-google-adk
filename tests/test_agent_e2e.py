"""End-to-end tests for the content_generator_agent.

These tests require a GOOGLE_API_KEY environment variable and make
actual API calls. They are skipped in CI without the key.
"""

from __future__ import annotations

import os

import pytest

_skip_no_api_key = pytest.mark.skipif(
    not os.environ.get("GOOGLE_API_KEY"),
    reason="GOOGLE_API_KEY not set",
)


@_skip_no_api_key
async def test_content_generator_e2e_agent_responds() -> None:
    """Verify the agent pipeline can process a simple request."""
    from google.adk.runners import InMemoryRunner

    from content_generator_agent.agent import root_agent

    runner = InMemoryRunner(
        agent=root_agent,
        app_name="test_content_generator",
    )

    session = await runner.session_service.create_session(
        app_name="test_content_generator",
        user_id="test_user",
    )

    from google.genai import types

    user_content = types.Content(
        role="user",
        parts=[
            types.Part(
                text=(
                    "Generate a DSA lesson about binary search for"
                    " learning-dsa project."
                ),
            ),
        ],
    )

    events = [
        event
        async for event in runner.run_async(
            user_id="test_user",
            session_id=session.id,
            new_message=user_content,
        )
    ]

    assert len(events) > 0
