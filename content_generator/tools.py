"""ADK FunctionTool-compatible wrapper functions.

Each function in this module is designed to be wrapped by ADK's FunctionTool.
They have complete type annotations, NumPy docstrings, and return strings
for reliable serialization back to the LLM agent.
"""

from __future__ import annotations

from google.adk.agents import Context

from . import analyzers, domains, validators
from .models import PROJECT_CATEGORIES, TargetProject, TemplateCategory
from .project_registry import get_project_path, validate_path


def analyze_target_project(project_name: str) -> str:
    """Analyze a target project's configuration and conventions.

    Reads pyproject.toml, AGENTS.md, and scans source directories
    to extract the project's coding standards and structure.

    Parameters
    ----------
    project_name : str
        One of: learning-dsa, learning-asyncio, learning-litestar,
        learning-fastapi.

    Returns
    -------
    str
        Formatted analysis of project configuration.
    """
    project = TargetProject(project_name)
    config = analyzers.analyze_project_config(project)
    return (
        f"Project: {config.name}\n"
        f"Python: {config.python_version}\n"
        f"Doctest modules: {config.has_doctest_modules}\n"
        f"Mypy strict: {config.mypy_strict}\n"
        f"Ruff target: {config.ruff_target_version}\n"
        f"Source dirs: {', '.join(config.source_dirs)}"
    )


def get_existing_content(project_name: str) -> str:
    """List existing lesson files in a target project.

    Parameters
    ----------
    project_name : str
        One of: learning-dsa, learning-asyncio, learning-litestar,
        learning-fastapi.

    Returns
    -------
    str
        Formatted list of existing lessons with paths.
    """
    project = TargetProject(project_name)
    lessons = analyzers.analyze_existing_lessons(project)
    if not lessons:
        return "No existing lessons found."
    lines = [f"- {lesson['name']} ({lesson['path']})" for lesson in lessons]
    return f"Found {len(lessons)} existing files:\n" + "\n".join(lines)


def read_template(project_name: str) -> str:
    """Read the lesson template and conventions for a target project.

    Parameters
    ----------
    project_name : str
        One of: learning-dsa, learning-asyncio, learning-litestar,
        learning-fastapi.

    Returns
    -------
    str
        Template content and project conventions.
    """
    project = TargetProject(project_name)
    template = analyzers.extract_template_patterns(project)
    parts = []
    if template.template_content:
        parts.append(f"=== TEMPLATE ===\n{template.template_content}")
    if template.conventions:
        parts.append(f"=== CONVENTIONS ===\n{template.conventions}")
    if template.example_lessons:
        parts.append(
            "=== EXAMPLES ===\n" + "\n".join(template.example_lessons),
        )
    return "\n\n".join(parts) if parts else "No template data found."


def read_progression_plan(project_name: str) -> str:
    """Read progression plan files for a target project.

    Parameters
    ----------
    project_name : str
        One of: learning-dsa, learning-asyncio, learning-litestar,
        learning-fastapi.

    Returns
    -------
    str
        Combined progression plan text.
    """
    project = TargetProject(project_name)
    text = analyzers.read_progression(project)
    return text if text else "No progression plan found."


def read_source_reference(project_name: str, relative_path: str) -> str:
    """Read a source file from a target project for reference.

    Parameters
    ----------
    project_name : str
        One of: learning-dsa, learning-asyncio, learning-litestar,
        learning-fastapi.
    relative_path : str
        Path relative to the project root.

    Returns
    -------
    str
        File contents.
    """
    project = TargetProject(project_name)
    project_path = get_project_path(project)
    file_path = project_path / relative_path
    validate_path(file_path)
    return analyzers.read_source_file(file_path)


def write_generated_file(
    project_name: str,
    relative_path: str,
    content: str,
    tool_context: Context,
) -> str:
    """Write generated content to a file in a target project.

    Parameters
    ----------
    project_name : str
        One of: learning-dsa, learning-asyncio, learning-litestar,
        learning-fastapi.
    relative_path : str
        Path relative to the project root.
    content : str
        The file content to write.
    tool_context : Context
        ADK context for state management.

    Returns
    -------
    str
        Success or error message.
    """
    project = TargetProject(project_name)
    project_path = get_project_path(project)
    file_path = project_path / relative_path
    validated_path = validate_path(file_path)

    validated_path.parent.mkdir(parents=True, exist_ok=True)
    validated_path.write_text(content, encoding="utf-8")

    # Store the written file path in session state for the validator
    tool_context.state["last_written_file"] = str(validated_path)
    tool_context.state["last_written_project"] = project_name

    return f"Successfully wrote {len(content)} bytes to {relative_path}"


def validate_generated_content(
    project_name: str,
    relative_path: str,
) -> str:
    """Run full validation (ruff, mypy, pytest) on a generated file.

    Parameters
    ----------
    project_name : str
        One of: learning-dsa, learning-asyncio, learning-litestar,
        learning-fastapi.
    relative_path : str
        Path relative to the project root.

    Returns
    -------
    str
        PASS if all checks pass, or detailed error messages.
    """
    project = TargetProject(project_name)
    project_path = get_project_path(project)
    file_path = project_path / relative_path
    validate_path(file_path)

    category = PROJECT_CATEGORIES.get(project, TemplateCategory.LESSON_BASED)
    run_doctest = category == TemplateCategory.LESSON_BASED

    result = validators.validate_file(
        file_path, project_dir=project_path, run_doctest=run_doctest
    )

    if result.passed:
        return "PASS: All validation checks passed."

    sections = [
        ("RUFF FORMAT", result.ruff_format),
        ("RUFF LINT", result.ruff_lint),
        ("MYPY", result.mypy),
        ("PYTEST", result.pytest),
    ]
    errors = [f"{label}:\n{output}" for label, output in sections if output]

    return "FAIL:\n" + "\n---\n".join(errors) if errors else f"FAIL:\n{result!s}"


def list_available_domains() -> str:
    """List all registered content generation domains.

    Returns
    -------
    str
        Comma-separated list of available domain names.
    """
    names = domains.list_domains()
    if not names:
        return "No domains registered."
    return f"Available domains: {', '.join(names)}"


def get_domain_config(domain_name: str) -> str:
    """Get the configuration for a content generation domain.

    Parameters
    ----------
    domain_name : str
        Domain identifier (e.g. ``"dsa"``, ``"asyncio"``).

    Returns
    -------
    str
        Formatted domain configuration summary.
    """
    config = domains.get_domain(domain_name)
    return (
        f"Domain: {config.name}\n"
        f"Project: {config.project.value}\n"
        f"Pedagogy: {config.pedagogy.value}\n"
        f"Lesson dir: {config.lesson_dir}\n"
        f"Strict mypy: {config.strict_mypy}\n"
        f"Doctest strategy: {config.doctest_strategy}"
    )


def get_next_lesson_number(project_name: str) -> str:
    """Determine the next lesson number for a target project.

    Scans existing lessons for numeric filename prefixes and returns
    one greater than the maximum found.

    Parameters
    ----------
    project_name : str
        One of: learning-dsa, learning-asyncio, learning-litestar,
        learning-fastapi.

    Returns
    -------
    str
        The next available lesson number.
    """
    project = TargetProject(project_name)
    number = analyzers.next_lesson_number(project)
    return f"Next lesson number: {number}"


def run_ruff_format(project_name: str, relative_path: str) -> str:
    """Run ruff format --check on a generated file.

    Parameters
    ----------
    project_name : str
        One of: learning-dsa, learning-asyncio, learning-litestar,
        learning-fastapi.
    relative_path : str
        Path relative to the project root.

    Returns
    -------
    str
        PASS or error output.
    """
    project = TargetProject(project_name)
    project_path = get_project_path(project)
    file_path = project_path / relative_path
    validate_path(file_path)

    ok, output = validators.run_ruff_format(file_path, project_dir=project_path)
    return f"PASS: {output}" if ok else f"FAIL: {output}"


def run_ruff_check(project_name: str, relative_path: str) -> str:
    """Run ruff check on a generated file.

    Parameters
    ----------
    project_name : str
        One of: learning-dsa, learning-asyncio, learning-litestar,
        learning-fastapi.
    relative_path : str
        Path relative to the project root.

    Returns
    -------
    str
        PASS or error output.
    """
    project = TargetProject(project_name)
    project_path = get_project_path(project)
    file_path = project_path / relative_path
    validate_path(file_path)

    ok, output = validators.run_ruff_check(file_path, project_dir=project_path)
    return f"PASS: {output}" if ok else f"FAIL: {output}"


def run_mypy_check(project_name: str, relative_path: str) -> str:
    """Run mypy on a generated file.

    Parameters
    ----------
    project_name : str
        One of: learning-dsa, learning-asyncio, learning-litestar,
        learning-fastapi.
    relative_path : str
        Path relative to the project root.

    Returns
    -------
    str
        PASS or error output.
    """
    project = TargetProject(project_name)
    project_path = get_project_path(project)
    file_path = project_path / relative_path
    validate_path(file_path)

    ok, output = validators.run_mypy_check(file_path, project_dir=project_path)
    return f"PASS: {output}" if ok else f"FAIL: {output}"


def run_pytest_doctest(project_name: str, relative_path: str) -> str:
    """Run pytest --doctest-modules on a generated file.

    Parameters
    ----------
    project_name : str
        One of: learning-dsa, learning-asyncio, learning-litestar,
        learning-fastapi.
    relative_path : str
        Path relative to the project root.

    Returns
    -------
    str
        PASS or error output.
    """
    project = TargetProject(project_name)
    project_path = get_project_path(project)
    file_path = project_path / relative_path
    validate_path(file_path)

    ok, output = validators.run_pytest_doctest(file_path, project_dir=project_path)
    return f"PASS: {output}" if ok else f"FAIL: {output}"
