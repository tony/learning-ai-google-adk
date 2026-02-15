"""Agent definition for the Google Search agent."""

from __future__ import annotations

from google.adk.agents import Agent
from google.adk.tools import google_search  # type: ignore[attr-defined]

root_agent = Agent(
    name="google_search_agent",
    model="gemini-2.5-flash",
    instruction=(
        "Answer questions using Google Search when needed."
        " Always cite sources."
    ),
    description="Professional search assistant with Google Search capabilities.",
    tools=[google_search],
)
