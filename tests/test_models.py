"""Tests for content_generator.models."""

from __future__ import annotations

import pathlib

import pytest

from content_generator.models import (
    PROJECT_CATEGORIES,
    AppTemplate,
    GeneratedContent,
    LessonPlan,
    LessonTemplate,
    ProjectConfig,
    TargetProject,
    TemplateCategory,
    ValidationResult,
)


def test_target_project_values() -> None:
    assert TargetProject.DSA.value == "learning-dsa"
    assert TargetProject.ASYNCIO.value == "learning-asyncio"
    assert TargetProject.LITESTAR.value == "learning-litestar"
    assert TargetProject.FASTAPI.value == "learning-fastapi"


def test_target_project_all_have_categories() -> None:
    for project in TargetProject:
        assert project in PROJECT_CATEGORIES


def test_template_category_lesson_based() -> None:
    assert PROJECT_CATEGORIES[TargetProject.DSA] == TemplateCategory.LESSON_BASED
    assert PROJECT_CATEGORIES[TargetProject.ASYNCIO] == TemplateCategory.LESSON_BASED


def test_template_category_app_based() -> None:
    assert PROJECT_CATEGORIES[TargetProject.LITESTAR] == TemplateCategory.APP_BASED
    assert PROJECT_CATEGORIES[TargetProject.FASTAPI] == TemplateCategory.APP_BASED


def test_project_config_defaults() -> None:
    config = ProjectConfig(name="test")
    assert config.python_version == "3.10"
    assert config.has_doctest_modules is False
    assert config.mypy_strict is False
    assert config.source_dirs == []


def test_project_config_full() -> None:
    config = ProjectConfig(
        name="learning-dsa",
        python_version="3.14",
        has_doctest_modules=True,
        mypy_strict=True,
        ruff_target_version="py314",
        source_dirs=["src"],
    )
    assert config.name == "learning-dsa"
    assert config.has_doctest_modules is True


def test_lesson_template_defaults() -> None:
    template = LessonTemplate(project=TargetProject.DSA)
    assert template.template_content == ""
    assert template.example_lessons == []
    assert template.conventions == ""


def test_lesson_template_with_content() -> None:
    template = LessonTemplate(
        project=TargetProject.ASYNCIO,
        template_content="# template",
        example_lessons=["001_intro.py"],
    )
    assert template.project == TargetProject.ASYNCIO
    assert len(template.example_lessons) == 1


def test_app_template_defaults() -> None:
    template = AppTemplate(project=TargetProject.LITESTAR)
    assert template.app_structure == ""
    assert template.test_patterns == []


def test_app_template_with_patterns() -> None:
    template = AppTemplate(
        project=TargetProject.FASTAPI,
        test_patterns=["tests/test_*.py"],
    )
    assert len(template.test_patterns) == 1


def test_lesson_plan_defaults() -> None:
    plan = LessonPlan(title="Binary Search", topic="binary_search")
    assert plan.lesson_number == 1
    assert plan.concepts == []
    assert plan.narrative == ""


def test_lesson_plan_full() -> None:
    plan = LessonPlan(
        title="Binary Search",
        topic="binary_search",
        lesson_number=5,
        concepts=["divide and conquer", "logarithmic time"],
        functions=["def binary_search(arr: list[int], target: int) -> int"],
        doctest_scenarios=[">>> binary_search([1, 2, 3], 2)\n1"],
        narrative="A search algorithm that halves the search space.",
    )
    assert plan.lesson_number == 5
    assert len(plan.concepts) == 2


def test_generated_content_creation() -> None:
    content = GeneratedContent(
        file_path=pathlib.Path("/tmp/test.py"),
        content="print('hello')",
        project=TargetProject.DSA,
    )
    assert content.file_path == pathlib.Path("/tmp/test.py")
    assert content.project == TargetProject.DSA


def test_validation_result_defaults() -> None:
    result = ValidationResult()
    assert result.passed is False
    assert result.ruff_format == ""
    assert result.ruff_lint == ""
    assert result.mypy == ""
    assert result.pytest == ""


def test_validation_result_passing() -> None:
    result = ValidationResult(
        passed=True,
        ruff_format="All checks passed!",
        ruff_lint="All checks passed!",
        mypy="Success: no issues found",
        pytest="1 passed",
    )
    assert result.passed is True


def test_enum_target_project_from_string() -> None:
    assert TargetProject("learning-dsa") == TargetProject.DSA


def test_enum_target_project_invalid() -> None:
    with pytest.raises(ValueError, match="not a valid"):
        TargetProject("nonexistent")


def test_enum_template_category_from_string() -> None:
    assert TemplateCategory("lesson_based") == TemplateCategory.LESSON_BASED
