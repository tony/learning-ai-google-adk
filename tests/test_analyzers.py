"""Tests for content_generator.analyzers."""

from __future__ import annotations

import pathlib

import pytest

from content_generator.analyzers import (
    analyze_existing_lessons,
    analyze_project_config,
    extract_template_patterns,
    read_progression,
    read_source_file,
)
from content_generator.models import TargetProject
from content_generator.project_registry import get_project_path

_DSA_PATH = get_project_path(TargetProject.DSA)
_ASYNCIO_PATH = get_project_path(TargetProject.ASYNCIO)


_skip_no_dsa = pytest.mark.skipif(
    not _DSA_PATH.exists(),
    reason="learning-dsa project not found",
)
_skip_no_asyncio = pytest.mark.skipif(
    not _ASYNCIO_PATH.exists(),
    reason="learning-asyncio project not found",
)


class TestAnalyzeProjectConfig:
    """Tests for analyze_project_config."""

    @_skip_no_dsa
    def test_dsa_config(self) -> None:
        config = analyze_project_config(TargetProject.DSA)
        assert config.name is not None
        assert config.mypy_strict is True
        assert config.has_doctest_modules is True

    @_skip_no_asyncio
    def test_asyncio_config(self) -> None:
        config = analyze_project_config(TargetProject.ASYNCIO)
        assert config.name is not None
        assert config.mypy_strict is True

    @_skip_no_dsa
    def test_source_dirs_detected(self) -> None:
        config = analyze_project_config(TargetProject.DSA)
        assert "src" in config.source_dirs

    def test_missing_project_raises(self, tmp_path: pathlib.Path) -> None:
        """Verify FileNotFoundError when pyproject.toml is absent."""
        # This test uses monkeypatching indirectly - the registry points
        # to real paths, so we test with the real projects.
        # If FASTAPI project doesn't exist, this will naturally raise.
        fastapi_path = get_project_path(TargetProject.FASTAPI)
        if fastapi_path.exists():
            pytest.skip("FASTAPI project exists, can't test missing")
        with pytest.raises(FileNotFoundError):
            analyze_project_config(TargetProject.FASTAPI)


class TestAnalyzeExistingLessons:
    """Tests for analyze_existing_lessons."""

    @_skip_no_dsa
    def test_dsa_has_lessons(self) -> None:
        lessons = analyze_existing_lessons(TargetProject.DSA)
        assert len(lessons) > 0
        assert all("name" in lesson for lesson in lessons)
        assert all("path" in lesson for lesson in lessons)

    @_skip_no_dsa
    def test_dsa_lessons_have_structure(self) -> None:
        lessons = analyze_existing_lessons(TargetProject.DSA)
        # Each lesson should have name and path keys
        for lesson in lessons:
            assert "name" in lesson
            assert "path" in lesson
            assert lesson["path"].endswith(".py")

    @_skip_no_asyncio
    def test_asyncio_has_lessons(self) -> None:
        lessons = analyze_existing_lessons(TargetProject.ASYNCIO)
        assert len(lessons) > 0

    @_skip_no_dsa
    def test_excludes_dunder_files(self) -> None:
        lessons = analyze_existing_lessons(TargetProject.DSA)
        for lesson in lessons:
            assert not lesson["name"].startswith("__")


class TestExtractTemplatePatterns:
    """Tests for extract_template_patterns."""

    @_skip_no_dsa
    def test_dsa_template(self) -> None:
        template = extract_template_patterns(TargetProject.DSA)
        assert template.project == TargetProject.DSA
        assert len(template.template_content) > 0
        assert len(template.conventions) > 0

    @_skip_no_asyncio
    def test_asyncio_template(self) -> None:
        template = extract_template_patterns(TargetProject.ASYNCIO)
        assert template.project == TargetProject.ASYNCIO

    @_skip_no_dsa
    def test_example_lessons_limited(self) -> None:
        template = extract_template_patterns(TargetProject.DSA)
        assert len(template.example_lessons) <= 3


class TestReadProgression:
    """Tests for read_progression."""

    @_skip_no_dsa
    def test_dsa_progression(self) -> None:
        progression = read_progression(TargetProject.DSA)
        # May or may not have progression files
        assert isinstance(progression, str)

    @_skip_no_asyncio
    def test_asyncio_progression(self) -> None:
        progression = read_progression(TargetProject.ASYNCIO)
        assert isinstance(progression, str)


class TestReadSourceFile:
    """Tests for read_source_file."""

    def test_reads_existing_file(self, tmp_path: pathlib.Path) -> None:
        test_file = tmp_path / "test.py"
        test_file.write_text("# test", encoding="utf-8")
        content = read_source_file(test_file)
        assert content == "# test"

    def test_raises_on_missing(self) -> None:
        with pytest.raises(FileNotFoundError):
            read_source_file(pathlib.Path("/nonexistent/file.py"))
