"""Structural tests for the content_generator_agent.

Verifies the SequentialAgent pipeline structure without requiring
an API key or making any LLM calls.
"""

from __future__ import annotations

from google.adk.agents import Agent, LoopAgent, SequentialAgent

from content_generator_agent.agent import (
    code_generator,
    content_planner,
    root_agent,
    template_analyzer,
    validation_loop,
    validator,
)


def test_root_agent_is_sequential() -> None:
    assert isinstance(root_agent, SequentialAgent)


def test_root_agent_has_four_sub_agents() -> None:
    assert len(root_agent.sub_agents) == 4


def test_root_agent_sub_agent_order() -> None:
    names = [agent.name for agent in root_agent.sub_agents]
    assert names == [
        "template_analyzer",
        "content_planner",
        "code_generator",
        "validation_loop",
    ]


def test_root_agent_name() -> None:
    assert root_agent.name == "content_generator"


def test_template_analyzer_is_llm_agent() -> None:
    assert isinstance(template_analyzer, Agent)


def test_template_analyzer_output_key() -> None:
    assert template_analyzer.output_key == "template_analysis"


def test_template_analyzer_include_contents_default() -> None:
    assert template_analyzer.include_contents == "default"


def test_template_analyzer_disallow_transfers() -> None:
    assert template_analyzer.disallow_transfer_to_parent is True
    assert template_analyzer.disallow_transfer_to_peers is True


def test_template_analyzer_has_tools() -> None:
    assert len(template_analyzer.tools) == 4


def test_template_analyzer_temperature() -> None:
    config = template_analyzer.generate_content_config
    assert config is not None
    assert config.temperature == 0.0


def test_content_planner_is_llm_agent() -> None:
    assert isinstance(content_planner, Agent)


def test_content_planner_output_key() -> None:
    assert content_planner.output_key == "lesson_plan"


def test_content_planner_include_contents_none() -> None:
    assert content_planner.include_contents == "none"


def test_content_planner_disallow_transfers() -> None:
    assert content_planner.disallow_transfer_to_parent is True
    assert content_planner.disallow_transfer_to_peers is True


def test_content_planner_references_template_analysis() -> None:
    assert isinstance(content_planner.instruction, str)
    assert "{template_analysis}" in content_planner.instruction


def test_content_planner_temperature() -> None:
    config = content_planner.generate_content_config
    assert config is not None
    assert config.temperature == 0.5


def test_code_generator_is_llm_agent() -> None:
    assert isinstance(code_generator, Agent)


def test_code_generator_output_key() -> None:
    assert code_generator.output_key == "generated_code_summary"


def test_code_generator_include_contents_none() -> None:
    assert code_generator.include_contents == "none"


def test_code_generator_disallow_transfers() -> None:
    assert code_generator.disallow_transfer_to_parent is True
    assert code_generator.disallow_transfer_to_peers is True


def test_code_generator_references_lesson_plan() -> None:
    assert isinstance(code_generator.instruction, str)
    assert "{lesson_plan}" in code_generator.instruction


def test_code_generator_temperature() -> None:
    config = code_generator.generate_content_config
    assert config is not None
    assert config.temperature == 0.1


def _tool_name(tool: object) -> str:
    """Extract tool name from FunctionTool or plain function."""
    return getattr(tool, "name", getattr(tool, "__name__", ""))


def test_code_generator_has_strip_fences_tool() -> None:
    """code_generator should have strip_code_fences for cleaning LLM output."""
    tool_names = [_tool_name(t) for t in code_generator.tools]
    assert "strip_code_fences" in tool_names


def test_validator_is_llm_agent() -> None:
    assert isinstance(validator, Agent)


def test_validator_no_output_key() -> None:
    assert validator.output_key is None


def test_validator_include_contents_none() -> None:
    assert validator.include_contents == "none"


def test_validator_disallow_transfers() -> None:
    assert validator.disallow_transfer_to_parent is True
    assert validator.disallow_transfer_to_peers is True


def test_validator_references_generated_code() -> None:
    assert isinstance(validator.instruction, str)
    assert "{generated_code_summary}" in validator.instruction


def test_validator_has_validation_tools() -> None:
    assert len(validator.tools) == 7


def test_validator_has_exit_loop_tool() -> None:
    """Validator must have exit_loop to signal successful completion."""
    tool_names = [_tool_name(t) for t in validator.tools]
    assert "exit_loop" in tool_names


def test_validator_temperature() -> None:
    config = validator.generate_content_config
    assert config is not None
    assert config.temperature == 0.0


def test_validation_loop_is_loop_agent() -> None:
    """The validation stage should be wrapped in a LoopAgent."""
    assert isinstance(validation_loop, LoopAgent)


def test_validation_loop_max_iterations() -> None:
    """LoopAgent should have a deterministic retry ceiling."""
    assert validation_loop.max_iterations == 3


def test_validator_inside_loop() -> None:
    """The validator agent should be the sole sub-agent of the loop."""
    assert len(validation_loop.sub_agents) == 1
    assert validation_loop.sub_agents[0] is validator


def test_state_placeholders_output_keys_match() -> None:
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


def test_state_placeholders_no_optional() -> None:
    for agent in [content_planner, code_generator, validator]:
        assert isinstance(agent.instruction, str)
        assert "{?" not in agent.instruction, (
            f"{agent.name} uses optional placeholder syntax"
        )
