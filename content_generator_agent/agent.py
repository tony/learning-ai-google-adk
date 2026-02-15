"""Agent definition for the Content Generator SequentialAgent pipeline.

Orchestrates a 4-stage pipeline: template analysis, content planning,
code generation, and validation with structural retry via LoopAgent.
"""

from __future__ import annotations

from google.adk.agents import Agent, LoopAgent, SequentialAgent
from google.adk.tools.exit_loop_tool import exit_loop
from google.genai import types

from content_generator.tools import (
    analyze_target_project,
    get_existing_content,
    read_progression_plan,
    read_source_reference,
    read_template,
    run_mypy_check,
    run_pytest_doctest,
    run_ruff_check,
    run_ruff_format,
    validate_generated_content,
    write_generated_file,
)
from content_generator.utils import strip_code_fences

from .prompts import (
    CODE_GENERATOR_INSTRUCTION,
    CONTENT_PLANNER_INSTRUCTION,
    TEMPLATE_ANALYZER_INSTRUCTION,
    VALIDATOR_INSTRUCTION,
)

template_analyzer = Agent(
    name="template_analyzer",
    model="gemini-2.5-flash",
    instruction=TEMPLATE_ANALYZER_INSTRUCTION,
    tools=[
        analyze_target_project,
        get_existing_content,
        read_template,
        read_progression_plan,
    ],
    output_key="template_analysis",
    include_contents="default",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    generate_content_config=types.GenerateContentConfig(temperature=0.0),
)

content_planner = Agent(
    name="content_planner",
    model="gemini-2.5-flash",
    instruction=CONTENT_PLANNER_INSTRUCTION,
    tools=[read_source_reference],
    output_key="lesson_plan",
    include_contents="none",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    generate_content_config=types.GenerateContentConfig(temperature=0.5),
)

code_generator = Agent(
    name="code_generator",
    model="gemini-2.5-flash",
    instruction=CODE_GENERATOR_INSTRUCTION,
    tools=[write_generated_file, strip_code_fences],
    output_key="generated_code_summary",
    include_contents="none",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
)

validator = Agent(
    name="validator",
    model="gemini-2.5-flash",
    instruction=VALIDATOR_INSTRUCTION,
    tools=[
        run_ruff_format,
        run_ruff_check,
        run_mypy_check,
        run_pytest_doctest,
        write_generated_file,
        validate_generated_content,
        exit_loop,
    ],
    include_contents="none",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    generate_content_config=types.GenerateContentConfig(temperature=0.0),
)

validation_loop = LoopAgent(
    name="validation_loop",
    sub_agents=[validator],
    max_iterations=3,
)

root_agent = SequentialAgent(
    name="content_generator",
    sub_agents=[template_analyzer, content_planner, code_generator, validation_loop],
)
