"""Structural tests for the content_generator_agent.

Verifies the SequentialAgent pipeline structure without requiring
an API key or making any LLM calls.
"""

from __future__ import annotations

from google.adk.agents import Agent, SequentialAgent

from content_generator_agent.agent import (
    code_generator,
    content_planner,
    root_agent,
    template_analyzer,
    validator,
)


class TestRootAgent:
    """Tests for the root SequentialAgent."""

    def test_is_sequential_agent(self) -> None:
        assert isinstance(root_agent, SequentialAgent)

    def test_has_four_sub_agents(self) -> None:
        assert len(root_agent.sub_agents) == 4

    def test_sub_agent_order(self) -> None:
        names = [agent.name for agent in root_agent.sub_agents]
        assert names == [
            "template_analyzer",
            "content_planner",
            "code_generator",
            "validator",
        ]

    def test_agent_name(self) -> None:
        assert root_agent.name == "content_generator"


class TestTemplateAnalyzer:
    """Tests for the template_analyzer sub-agent."""

    def test_is_llm_agent(self) -> None:
        assert isinstance(template_analyzer, Agent)

    def test_output_key(self) -> None:
        assert template_analyzer.output_key == "template_analysis"

    def test_include_contents_default(self) -> None:
        assert template_analyzer.include_contents == "default"

    def test_disallow_transfers(self) -> None:
        assert template_analyzer.disallow_transfer_to_parent is True
        assert template_analyzer.disallow_transfer_to_peers is True

    def test_has_tools(self) -> None:
        assert len(template_analyzer.tools) == 4

    def test_temperature(self) -> None:
        config = template_analyzer.generate_content_config
        assert config is not None
        assert config.temperature == 0.0


class TestContentPlanner:
    """Tests for the content_planner sub-agent."""

    def test_is_llm_agent(self) -> None:
        assert isinstance(content_planner, Agent)

    def test_output_key(self) -> None:
        assert content_planner.output_key == "lesson_plan"

    def test_include_contents_none(self) -> None:
        assert content_planner.include_contents == "none"

    def test_disallow_transfers(self) -> None:
        assert content_planner.disallow_transfer_to_parent is True
        assert content_planner.disallow_transfer_to_peers is True

    def test_instruction_references_template_analysis(self) -> None:
        assert isinstance(content_planner.instruction, str)
        assert "{template_analysis}" in content_planner.instruction

    def test_temperature(self) -> None:
        config = content_planner.generate_content_config
        assert config is not None
        assert config.temperature == 0.5


class TestCodeGenerator:
    """Tests for the code_generator sub-agent."""

    def test_is_llm_agent(self) -> None:
        assert isinstance(code_generator, Agent)

    def test_output_key(self) -> None:
        assert code_generator.output_key == "generated_code_summary"

    def test_include_contents_none(self) -> None:
        assert code_generator.include_contents == "none"

    def test_disallow_transfers(self) -> None:
        assert code_generator.disallow_transfer_to_parent is True
        assert code_generator.disallow_transfer_to_peers is True

    def test_instruction_references_lesson_plan(self) -> None:
        assert isinstance(code_generator.instruction, str)
        assert "{lesson_plan}" in code_generator.instruction

    def test_temperature(self) -> None:
        config = code_generator.generate_content_config
        assert config is not None
        assert config.temperature == 0.1


class TestValidator:
    """Tests for the validator sub-agent."""

    def test_is_llm_agent(self) -> None:
        assert isinstance(validator, Agent)

    def test_no_output_key(self) -> None:
        assert validator.output_key is None

    def test_include_contents_none(self) -> None:
        assert validator.include_contents == "none"

    def test_disallow_transfers(self) -> None:
        assert validator.disallow_transfer_to_parent is True
        assert validator.disallow_transfer_to_peers is True

    def test_instruction_references_generated_code(self) -> None:
        assert isinstance(validator.instruction, str)
        assert "{generated_code_summary}" in validator.instruction

    def test_has_validation_tools(self) -> None:
        assert len(validator.tools) == 6

    def test_temperature(self) -> None:
        config = validator.generate_content_config
        assert config is not None
        assert config.temperature == 0.0


class TestStatePlaceholders:
    """Tests that state placeholders form a valid chain."""

    def test_output_keys_match_placeholders(self) -> None:
        # template_analyzer outputs "template_analysis"
        assert template_analyzer.output_key == "template_analysis"
        assert isinstance(content_planner.instruction, str)
        assert "{template_analysis}" in content_planner.instruction

        # content_planner outputs "lesson_plan"
        assert content_planner.output_key == "lesson_plan"
        assert isinstance(code_generator.instruction, str)
        assert "{lesson_plan}" in code_generator.instruction

        # code_generator outputs "generated_code_summary"
        assert code_generator.output_key == "generated_code_summary"
        assert isinstance(validator.instruction, str)
        assert "{generated_code_summary}" in validator.instruction

    def test_no_optional_placeholders(self) -> None:
        for agent in [content_planner, code_generator, validator]:
            assert isinstance(agent.instruction, str)
            assert "{?" not in agent.instruction, (
                f"{agent.name} uses optional placeholder syntax"
            )
