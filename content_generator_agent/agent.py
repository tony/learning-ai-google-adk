"""Agent definition for the Content Generator SequentialAgent pipeline.

Orchestrates a 4-stage pipeline: template analysis, content planning,
code generation, and validation with automated repair.
"""

from __future__ import annotations

from google.adk.agents import Agent, SequentialAgent
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

template_analyzer = Agent(
    name="template_analyzer",
    model="gemini-2.5-flash",
    instruction="""\
You are a project analyzer for Python learning content generation.

Given a user request to generate content for a specific topic and project type,
analyze the target project thoroughly using your tools.

Steps:
1. Use analyze_target_project to read the project configuration
2. Use get_existing_content to see what lessons already exist
3. Use read_template to get the lesson template and conventions
4. Use read_progression_plan to understand the learning progression

Produce a comprehensive analysis including:
- Project configuration (Python version, linting rules, type checking)
- Template structure and conventions
- Existing lessons and next lesson number
- Key requirements (doctests, type hints, docstring format)
- Any progression plan context

Your final response should be a complete structured analysis that the
content planner can use to create an accurate lesson plan.""",
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
    instruction="""\
You are a content planner for Python learning materials.

Based on the template analysis:
{template_analysis}

Create a detailed lesson plan that includes:
1. Lesson title and number (based on existing content)
2. Key concepts to teach
3. Function signatures with type hints
4. Doctest scenarios (at least 3 per function)
5. Teaching narrative connecting the concepts
6. The specific template structure to follow

If needed, use read_source_reference to examine existing lessons for style.

Your final response must be a complete, detailed lesson plan with all
function signatures, doctest examples, and narrative text fully specified.""",
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
    instruction="""\
You are a Python code generator for learning content.

Based on the lesson plan:
{lesson_plan}

Generate the complete Python source file following these rules:
1. Start with `from __future__ import annotations`
2. Use NumPy-style docstrings for all functions
3. Include working doctests that are self-contained and deterministic
4. Use strict type hints (compatible with mypy --strict)
5. Follow the exact template structure from the analysis
6. Include a main() function with demonstration code
7. End with `if __name__ == "__main__": doctest.testmod(); main()`

Use write_generated_file to save the complete file.

Your final response should summarize what was written, including:
- File path
- Project name
- Functions implemented
- Number of doctests included""",
    tools=[write_generated_file],
    output_key="generated_code_summary",
    include_contents="none",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
)

validator = Agent(
    name="validator",
    model="gemini-2.5-flash",
    instruction="""\
You are a code validator and repair agent.

Validate the generated code:
{generated_code_summary}

Run validation in this order:
1. run_ruff_format - Check formatting
2. run_ruff_check - Check linting
3. run_mypy_check - Check types
4. run_pytest_doctest - Check doctests

If ANY check fails:
- Analyze the error messages carefully
- Fix the code using write_generated_file
- Re-run the failing checks
- Maximum 3 repair cycles

After validation, use validate_generated_content for a final comprehensive check.

Your final response should report:
- PASS or FAIL status
- Any fixes applied
- Final validation results""",
    tools=[
        run_ruff_format,
        run_ruff_check,
        run_mypy_check,
        run_pytest_doctest,
        write_generated_file,
        validate_generated_content,
    ],
    include_contents="none",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    generate_content_config=types.GenerateContentConfig(temperature=0.0),
)

root_agent = SequentialAgent(
    name="content_generator",
    sub_agents=[template_analyzer, content_planner, code_generator, validator],
)
