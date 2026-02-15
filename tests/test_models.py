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


class TestTargetProject:
    """Tests for the TargetProject enum."""

    def test_values(self) -> None:
        assert TargetProject.DSA.value == "learning-dsa"
        assert TargetProject.ASYNCIO.value == "learning-asyncio"
        assert TargetProject.LITESTAR.value == "learning-litestar"
        assert TargetProject.FASTAPI.value == "learning-fastapi"

    def test_all_projects_have_categories(self) -> None:
        for project in TargetProject:
            assert project in PROJECT_CATEGORIES


class TestTemplateCategory:
    """Tests for the TemplateCategory enum."""

    def test_lesson_based_projects(self) -> None:
        assert PROJECT_CATEGORIES[TargetProject.DSA] == TemplateCategory.LESSON_BASED
        assert (
            PROJECT_CATEGORIES[TargetProject.ASYNCIO] == TemplateCategory.LESSON_BASED
        )

    def test_app_based_projects(self) -> None:
        assert PROJECT_CATEGORIES[TargetProject.LITESTAR] == TemplateCategory.APP_BASED
        assert PROJECT_CATEGORIES[TargetProject.FASTAPI] == TemplateCategory.APP_BASED


class TestProjectConfig:
    """Tests for the ProjectConfig model."""

    def test_defaults(self) -> None:
        config = ProjectConfig(name="test")
        assert config.python_version == "3.10"
        assert config.has_doctest_modules is False
        assert config.mypy_strict is False
        assert config.source_dirs == []

    def test_full_config(self) -> None:
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


class TestLessonTemplate:
    """Tests for the LessonTemplate model."""

    def test_defaults(self) -> None:
        template = LessonTemplate(project=TargetProject.DSA)
        assert template.template_content == ""
        assert template.example_lessons == []
        assert template.conventions == ""

    def test_with_content(self) -> None:
        template = LessonTemplate(
            project=TargetProject.ASYNCIO,
            template_content="# template",
            example_lessons=["001_intro.py"],
        )
        assert template.project == TargetProject.ASYNCIO
        assert len(template.example_lessons) == 1


class TestAppTemplate:
    """Tests for the AppTemplate model."""

    def test_defaults(self) -> None:
        template = AppTemplate(project=TargetProject.LITESTAR)
        assert template.app_structure == ""
        assert template.test_patterns == []

    def test_with_patterns(self) -> None:
        template = AppTemplate(
            project=TargetProject.FASTAPI,
            test_patterns=["tests/test_*.py"],
        )
        assert len(template.test_patterns) == 1


class TestLessonPlan:
    """Tests for the LessonPlan model."""

    def test_defaults(self) -> None:
        plan = LessonPlan(title="Binary Search", topic="binary_search")
        assert plan.lesson_number == 1
        assert plan.concepts == []
        assert plan.narrative == ""

    def test_full_plan(self) -> None:
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


class TestGeneratedContent:
    """Tests for the GeneratedContent model."""

    def test_creation(self) -> None:
        content = GeneratedContent(
            file_path=pathlib.Path("/tmp/test.py"),
            content="print('hello')",
            project=TargetProject.DSA,
        )
        assert content.file_path == pathlib.Path("/tmp/test.py")
        assert content.project == TargetProject.DSA


class TestValidationResult:
    """Tests for the ValidationResult model."""

    def test_defaults(self) -> None:
        result = ValidationResult()
        assert result.passed is False
        assert result.ruff_format == ""
        assert result.ruff_lint == ""
        assert result.mypy == ""
        assert result.pytest == ""

    def test_passing_result(self) -> None:
        result = ValidationResult(
            passed=True,
            ruff_format="All checks passed!",
            ruff_lint="All checks passed!",
            mypy="Success: no issues found",
            pytest="1 passed",
        )
        assert result.passed is True


class TestEnumFromString:
    """Tests for creating enums from string values."""

    def test_target_project_from_string(self) -> None:
        assert TargetProject("learning-dsa") == TargetProject.DSA

    def test_target_project_invalid(self) -> None:
        with pytest.raises(ValueError, match="not a valid"):
            TargetProject("nonexistent")

    def test_template_category_from_string(self) -> None:
        assert TemplateCategory("lesson_based") == TemplateCategory.LESSON_BASED
