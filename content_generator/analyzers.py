"""Project analysis functions for reading target project configuration.

Reads pyproject.toml, scans existing lessons, extracts template patterns,
and reads progression plans from target learning projects.
"""

from __future__ import annotations

import pathlib
import re
import tomllib

from .builtin_templates import get_builtin_template
from .models import (
    PROJECT_CATEGORIES,
    LessonTemplate,
    PedagogyStyle,
    ProjectConfig,
    TargetProject,
    TemplateCategory,
)
from .project_registry import get_project_path

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
    if isinstance(addopts, str):
        addopts = addopts.split()
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
    category = PROJECT_CATEGORIES.get(project, TemplateCategory.LESSON_BASED)

    for src_dir in _SOURCE_DIRS.get(category, ["src"]):
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
    category = PROJECT_CATEGORIES.get(project, TemplateCategory.LESSON_BASED)
    for src_dir in _SOURCE_DIRS.get(category, ["src"]):
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


# Regex to extract a leading numeric prefix from lesson filenames.
_LESSON_NUMBER_RE = re.compile(r"^(\d+)")


def next_lesson_number(project: TargetProject) -> int:
    """Determine the next lesson number for a project.

    Scans existing lessons for numeric filename prefixes and returns
    one greater than the maximum found.  Returns ``1`` if no numbered
    lessons exist.

    Parameters
    ----------
    project : TargetProject
        The project to scan.

    Returns
    -------
    int
        The next available lesson number.
    """
    lessons = analyze_existing_lessons(project)
    max_num = 0
    for lesson in lessons:
        match = _LESSON_NUMBER_RE.match(lesson["name"])
        if match:
            max_num = max(max_num, int(match.group(1)))
    return max_num + 1


def read_template_with_fallback(
    project: TargetProject,
    pedagogy: PedagogyStyle,
) -> str:
    """Read a project-specific template, falling back to a builtin.

    Attempts to load the project's own lesson template via
    :func:`extract_template_patterns`.  If no project-specific template
    is found, loads the builtin template for the given pedagogy style.

    Parameters
    ----------
    project : TargetProject
        The project to read templates from.
    pedagogy : PedagogyStyle
        Pedagogy style for builtin fallback selection.

    Returns
    -------
    str
        Template content.
    """
    template = extract_template_patterns(project)
    if template.template_content:
        return template.template_content
    return get_builtin_template(pedagogy)


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
