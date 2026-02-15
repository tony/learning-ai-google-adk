"""Tests for content_generator_agent.prompts."""

from __future__ import annotations

from content_generator_agent.prompts import (
    CODE_GENERATOR_INSTRUCTION,
    CONTENT_PLANNER_INSTRUCTION,
    TEMPLATE_ANALYZER_INSTRUCTION,
    VALIDATOR_INSTRUCTION,
)


def test_template_analyzer_instruction_non_empty() -> None:
    assert len(TEMPLATE_ANALYZER_INSTRUCTION) > 0


def test_content_planner_instruction_non_empty() -> None:
    assert len(CONTENT_PLANNER_INSTRUCTION) > 0


def test_code_generator_instruction_non_empty() -> None:
    assert len(CODE_GENERATOR_INSTRUCTION) > 0


def test_validator_instruction_non_empty() -> None:
    assert len(VALIDATOR_INSTRUCTION) > 0


def test_content_planner_references_template_analysis() -> None:
    """Content planner must receive template_analysis from previous agent."""
    assert "{template_analysis}" in CONTENT_PLANNER_INSTRUCTION


def test_code_generator_references_lesson_plan() -> None:
    """Code generator must receive lesson_plan from previous agent."""
    assert "{lesson_plan}" in CODE_GENERATOR_INSTRUCTION


def test_validator_references_generated_code_summary() -> None:
    """Validator must receive generated_code_summary from previous agent."""
    assert "{generated_code_summary}" in VALIDATOR_INSTRUCTION


def test_validator_mentions_exit_loop() -> None:
    """Validator instruction must mention exit_loop for LoopAgent integration."""
    assert "exit_loop" in VALIDATOR_INSTRUCTION


def test_validator_no_maximum_cycles_text() -> None:
    """Validator should not have text retry limits (LoopAgent handles this)."""
    assert "Maximum 3" not in VALIDATOR_INSTRUCTION
    assert "maximum 3" not in VALIDATOR_INSTRUCTION
