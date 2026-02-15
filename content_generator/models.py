"""Domain models for the content generator system.

Defines Pydantic models and enums that represent target projects,
template categories, lesson plans, generated content, and validation results.
"""

from __future__ import annotations

import enum
import pathlib

from pydantic import BaseModel, Field


class TargetProject(enum.StrEnum):
    """Supported target learning projects."""

    DSA = "learning-dsa"
    ASYNCIO = "learning-asyncio"
    LITESTAR = "learning-litestar"
    FASTAPI = "learning-fastapi"


class TemplateCategory(enum.StrEnum):
    """Template categories that determine generation strategy.

    LESSON_BASED projects use numbered Python files with doctests as
    primary tests (DSA, asyncio). APP_BASED projects use separate
    test files with integration tests (Litestar, FastAPI).
    """

    LESSON_BASED = "lesson_based"
    APP_BASED = "app_based"


#: Maps each project to its template category.
PROJECT_CATEGORIES: dict[TargetProject, TemplateCategory] = {
    TargetProject.DSA: TemplateCategory.LESSON_BASED,
    TargetProject.ASYNCIO: TemplateCategory.LESSON_BASED,
    TargetProject.LITESTAR: TemplateCategory.APP_BASED,
    TargetProject.FASTAPI: TemplateCategory.APP_BASED,
}


class PedagogyStyle(enum.StrEnum):
    """Teaching approach for content generation.

    Each style maps to a different lesson structure and emphasis.
    """

    CONCEPT_FIRST = "concept_first"
    """DSA, asyncio: heavy doctests, pure Python, algorithmic focus."""

    INTEGRATION_FIRST = "integration_first"
    """Framework integration patterns."""

    APPLICATION_FIRST = "application_first"
    """Litestar, FastAPI: functioning server/app with tests."""


class LessonMetadata(BaseModel):
    """Metadata for a generated lesson.

    Parameters
    ----------
    number : int
        Lesson sequence number.
    title : str
        Human-readable lesson title.
    filename : str
        Output filename (e.g. ``"003_hash_tables.py"``).
    prerequisites : list[str]
        List of prerequisite lesson names.
    narrative : str
        Brief narrative context for the lesson.
    """

    number: int
    title: str
    filename: str
    prerequisites: list[str] = Field(default_factory=list)
    narrative: str = ""


class ProjectConfig(BaseModel):
    """Configuration extracted from a target project's pyproject.toml.

    Parameters
    ----------
    name : str
        Project name from pyproject.toml.
    python_version : str
        Minimum Python version required.
    has_doctest_modules : bool
        Whether pytest is configured with ``--doctest-modules``.
    mypy_strict : bool
        Whether mypy strict mode is enabled.
    ruff_target_version : str
        Ruff target Python version string.
    source_dirs : list[str]
        Source directories configured for the project.
    """

    name: str
    python_version: str = "3.10"
    has_doctest_modules: bool = False
    mypy_strict: bool = False
    ruff_target_version: str = "py310"
    source_dirs: list[str] = Field(default_factory=list)


class LessonTemplate(BaseModel):
    """Template data for lesson-based content generation.

    Parameters
    ----------
    project : TargetProject
        The target project this template is for.
    template_content : str
        Raw template file content.
    example_lessons : list[str]
        Paths to existing example lessons.
    conventions : str
        Extracted coding conventions from AGENTS.md.
    """

    project: TargetProject
    template_content: str = ""
    example_lessons: list[str] = Field(default_factory=list)
    conventions: str = ""


class AppTemplate(BaseModel):
    """Template data for app-based content generation.

    Parameters
    ----------
    project : TargetProject
        The target project this template is for.
    app_structure : str
        Description of the app directory layout.
    test_patterns : list[str]
        Glob patterns for existing test files.
    conventions : str
        Extracted coding conventions from AGENTS.md.
    """

    project: TargetProject
    app_structure: str = ""
    test_patterns: list[str] = Field(default_factory=list)
    conventions: str = ""


class LessonPlan(BaseModel):
    """Structured plan for generating a single lesson.

    Parameters
    ----------
    title : str
        Lesson title.
    topic : str
        Primary topic covered.
    lesson_number : int
        Lesson sequence number.
    concepts : list[str]
        Key concepts to teach.
    functions : list[str]
        Function signatures to implement.
    doctest_scenarios : list[str]
        Planned doctest examples.
    narrative : str
        Teaching narrative connecting concepts.
    """

    title: str
    topic: str
    lesson_number: int = 1
    concepts: list[str] = Field(default_factory=list)
    functions: list[str] = Field(default_factory=list)
    doctest_scenarios: list[str] = Field(default_factory=list)
    narrative: str = ""


class GeneratedContent(BaseModel):
    """Represents a piece of generated content with metadata.

    Parameters
    ----------
    file_path : pathlib.Path
        Absolute path where the file was written.
    content : str
        The generated source code.
    project : TargetProject
        Which project this content targets.
    """

    file_path: pathlib.Path
    content: str
    project: TargetProject


class ValidationResult(BaseModel):
    """Structured result from running validation tools.

    Parameters
    ----------
    passed : bool
        Whether all validation checks passed.
    ruff_format : str
        Output from ``ruff format --check``.
    ruff_lint : str
        Output from ``ruff check``.
    mypy : str
        Output from mypy.
    pytest : str
        Output from pytest doctest run.
    """

    passed: bool = False
    errors: list[str] = Field(default_factory=list)
    ruff_format: str = ""
    ruff_lint: str = ""
    mypy: str = ""
    pytest: str = ""
