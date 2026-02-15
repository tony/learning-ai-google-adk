"""Project analysis functions for reading target project configuration.

Reads pyproject.toml, scans existing lessons, extracts template patterns,
and reads progression plans from target learning projects.
"""

from __future__ import annotations

import pathlib
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore[import-not-found]

from .models import (
    LessonTemplate,
    ProjectConfig,
    TargetProject,
    TemplateCategory,
)
from .project_registry import get_project_path

#: Maps template categories to source directory glob patterns.
_SOURCE_PATTERNS: dict[TemplateCategory, list[str]] = {
    TemplateCategory.LESSON_BASED: ["src/**/*.py", "src/*.py"],
    TemplateCategory.APP_BASED: ["app/**/*.py", "src/**/*.py"],
}

#: Maps template categories to source directories to scan.
_SOURCE_DIRS: dict[TemplateCategory, list[str]] = {
    TemplateCategory.LESSON_BASED: ["src"],
    TemplateCategory.APP_BASED: ["app", "src"],
}


def analyze_project_config(project: TargetProject) -> ProjectConfig:
    """Read and parse a target project's pyproject.toml.

    Parameters
    ----------
    project : TargetProject
        The project to analyze.

    Returns
    -------
    ProjectConfig
        Extracted configuration values.

    Raises
    ------
    FileNotFoundError
        If pyproject.toml does not exist in the project root.
    """
    project_path = get_project_path(project)
    pyproject_path = project_path / "pyproject.toml"

    if not pyproject_path.exists():
        msg = f"pyproject.toml not found at {pyproject_path}"
        raise FileNotFoundError(msg)

    with pyproject_path.open("rb") as f:
        data = tomllib.load(f)

    project_section = data.get("project", {})
    tool_section = data.get("tool", {})
    # pytest config may be under [tool.pytest.ini_options] or [tool.pytest]
    pytest_section = tool_section.get("pytest", {})
    if "ini_options" in pytest_section:
        pytest_section = pytest_section["ini_options"]
    mypy_section = tool_section.get("mypy", {})
    ruff_section = tool_section.get("ruff", {})

    addopts = pytest_section.get("addopts", [])
    has_doctest = any("--doctest-modules" in opt for opt in addopts)

    python_version = project_section.get("requires-python", ">=3.10")

    source_dirs = list(
        dict.fromkeys(
            d
            for category_dirs in _SOURCE_DIRS.values()
            for d in category_dirs
            if (project_path / d).is_dir()
        )
    )

    return ProjectConfig(
        name=project_section.get("name", project.value),
        python_version=python_version,
        has_doctest_modules=has_doctest,
        mypy_strict=mypy_section.get("strict", False),
        ruff_target_version=ruff_section.get("target-version", "py310"),
        source_dirs=source_dirs,
    )


def analyze_existing_lessons(
    project: TargetProject,
) -> list[dict[str, str]]:
    """Scan a project's source directories for existing lesson files.

    Parameters
    ----------
    project : TargetProject
        The project to scan.

    Returns
    -------
    list[dict[str, str]]
        List of dicts with ``name`` and ``path`` keys for each lesson file,
        sorted by filename.
    """
    project_path = get_project_path(project)
    lessons: list[dict[str, str]] = []

    for src_dir in _SOURCE_DIRS.get(TemplateCategory.LESSON_BASED, ["src"]):
        source_path = project_path / src_dir
        if not source_path.is_dir():
            continue
        for py_file in sorted(source_path.rglob("*.py")):
            if py_file.name.startswith("__"):
                continue
            lessons.append(
                {
                    "name": py_file.stem,
                    "path": str(py_file.relative_to(project_path)),
                }
            )

    return lessons


def extract_template_patterns(project: TargetProject) -> LessonTemplate:
    """Read template files from a project's notes directory.

    Parameters
    ----------
    project : TargetProject
        The project to read templates from.

    Returns
    -------
    LessonTemplate
        Template data including content and conventions.
    """
    project_path = get_project_path(project)
    template = LessonTemplate(project=project)

    # Read lesson template
    template_path = project_path / "notes" / "lesson_template.py"
    if template_path.exists():
        template.template_content = template_path.read_text(encoding="utf-8")

    # Read AGENTS.md for conventions
    agents_path = project_path / "AGENTS.md"
    if agents_path.exists():
        template.conventions = agents_path.read_text(encoding="utf-8")

    # Collect example lesson paths
    for src_dir in _SOURCE_DIRS.get(TemplateCategory.LESSON_BASED, ["src"]):
        source_path = project_path / src_dir
        if source_path.is_dir():
            for py_file in sorted(source_path.rglob("*.py"))[:3]:
                if not py_file.name.startswith("__"):
                    template.example_lessons.append(
                        str(py_file.relative_to(project_path)),
                    )

    return template


def read_progression(project: TargetProject) -> str:
    """Read progression plan files from a project's notes directory.

    Looks for files matching ``progression*.md`` or ``progression*.txt``
    in the ``notes/`` subdirectory.

    Parameters
    ----------
    project : TargetProject
        The project to read progression from.

    Returns
    -------
    str
        Combined text of all progression files, or empty string if none found.
    """
    project_path = get_project_path(project)
    notes_path = project_path / "notes"

    if not notes_path.is_dir():
        return ""

    parts: list[str] = [
        path.read_text(encoding="utf-8")
        for pattern in ["progression*.md", "progression*.txt"]
        for path in sorted(notes_path.glob(pattern))
    ]

    return "\n\n".join(parts)


def read_source_file(file_path: pathlib.Path) -> str:
    """Read a source file from a target project.

    Parameters
    ----------
    file_path : pathlib.Path
        Path to the file to read.

    Returns
    -------
    str
        File contents as text.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    """
    if not file_path.exists():
        msg = f"File not found: {file_path}"
        raise FileNotFoundError(msg)
    return file_path.read_text(encoding="utf-8")
