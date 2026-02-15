"""Tests for content_generator.analyzers."""

from __future__ import annotations

import pathlib

import pytest

import content_generator.analyzers as analyzers_module
from content_generator.analyzers import (
    analyze_existing_lessons,
    analyze_project_config,
    extract_template_patterns,
    next_lesson_number,
    read_progression,
    read_source_file,
    read_template_with_fallback,
)
from content_generator.models import PedagogyStyle, TargetProject
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


@_skip_no_dsa
def test_analyze_project_config_dsa() -> None:
    config = analyze_project_config(TargetProject.DSA)
    assert config.name is not None
    assert config.mypy_strict is True
    assert config.has_doctest_modules is True


@_skip_no_asyncio
def test_analyze_project_config_asyncio() -> None:
    config = analyze_project_config(TargetProject.ASYNCIO)
    assert config.name is not None
    assert config.mypy_strict is True


@_skip_no_dsa
def test_analyze_project_config_source_dirs() -> None:
    config = analyze_project_config(TargetProject.DSA)
    assert "src" in config.source_dirs


def test_analyze_project_config_string_addopts(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    """Verify addopts as a single string is split correctly."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[project]\nname = "test"\n'
        "[tool.pytest.ini_options]\n"
        'addopts = "--doctest-modules -v"\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(analyzers_module, "get_project_path", lambda _: tmp_path)
    config = analyze_project_config(TargetProject.DSA)
    assert config.has_doctest_modules is True


def test_analyze_project_config_missing_raises(tmp_path: pathlib.Path) -> None:
    """Verify FileNotFoundError when pyproject.toml is absent."""
    # This test uses monkeypatching indirectly - the registry points
    # to real paths, so we test with the real projects.
    # If FASTAPI project doesn't exist, this will naturally raise.
    fastapi_path = get_project_path(TargetProject.FASTAPI)
    if fastapi_path.exists():
        pytest.skip("FASTAPI project exists, can't test missing")
    with pytest.raises(FileNotFoundError):
        analyze_project_config(TargetProject.FASTAPI)


@_skip_no_dsa
def test_analyze_existing_lessons_dsa() -> None:
    lessons = analyze_existing_lessons(TargetProject.DSA)
    assert len(lessons) > 0
    assert all("name" in lesson for lesson in lessons)
    assert all("path" in lesson for lesson in lessons)


@_skip_no_dsa
def test_analyze_existing_lessons_dsa_structure() -> None:
    lessons = analyze_existing_lessons(TargetProject.DSA)
    # Each lesson should have name and path keys
    for lesson in lessons:
        assert "name" in lesson
        assert "path" in lesson
        assert lesson["path"].endswith(".py")


@_skip_no_asyncio
def test_analyze_existing_lessons_asyncio() -> None:
    lessons = analyze_existing_lessons(TargetProject.ASYNCIO)
    assert len(lessons) > 0


@_skip_no_dsa
def test_analyze_existing_lessons_excludes_dunder() -> None:
    lessons = analyze_existing_lessons(TargetProject.DSA)
    for lesson in lessons:
        assert not lesson["name"].startswith("__")


def test_analyze_existing_lessons_app_based_scans_app_dir(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    """APP_BASED projects should scan the app/ directory."""
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / "main.py").write_text("# app", encoding="utf-8")
    (app_dir / "__init__.py").write_text("", encoding="utf-8")

    monkeypatch.setattr(analyzers_module, "get_project_path", lambda _: tmp_path)
    lessons = analyze_existing_lessons(TargetProject.LITESTAR)

    names = [lesson["name"] for lesson in lessons]
    assert "main" in names


def test_analyze_existing_lessons_app_based_excludes_dunder(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    """APP_BASED projects should still exclude __init__.py."""
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / "__init__.py").write_text("", encoding="utf-8")

    monkeypatch.setattr(analyzers_module, "get_project_path", lambda _: tmp_path)
    lessons = analyze_existing_lessons(TargetProject.LITESTAR)

    assert len(lessons) == 0


@_skip_no_dsa
def test_extract_template_patterns_dsa() -> None:
    template = extract_template_patterns(TargetProject.DSA)
    assert template.project == TargetProject.DSA
    assert len(template.template_content) > 0
    assert len(template.conventions) > 0


@_skip_no_asyncio
def test_extract_template_patterns_asyncio() -> None:
    template = extract_template_patterns(TargetProject.ASYNCIO)
    assert template.project == TargetProject.ASYNCIO


@_skip_no_dsa
def test_extract_template_patterns_example_lessons_limited() -> None:
    template = extract_template_patterns(TargetProject.DSA)
    assert len(template.example_lessons) <= 3


@_skip_no_dsa
def test_read_progression_dsa() -> None:
    progression = read_progression(TargetProject.DSA)
    # May or may not have progression files
    assert isinstance(progression, str)


@_skip_no_asyncio
def test_read_progression_asyncio() -> None:
    progression = read_progression(TargetProject.ASYNCIO)
    assert isinstance(progression, str)


def test_read_source_file_existing(tmp_path: pathlib.Path) -> None:
    test_file = tmp_path / "test.py"
    test_file.write_text("# test", encoding="utf-8")
    content = read_source_file(test_file)
    assert content == "# test"


def test_read_source_file_missing_raises() -> None:
    with pytest.raises(FileNotFoundError):
        read_source_file(pathlib.Path("/nonexistent/file.py"))


def test_next_lesson_number_empty_dir(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    """next_lesson_number should return 1 for an empty project."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    monkeypatch.setattr(analyzers_module, "get_project_path", lambda _: tmp_path)
    assert next_lesson_number(TargetProject.DSA) == 1


def test_next_lesson_number_with_numbered_files(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    """next_lesson_number should return max+1 from existing numbered files."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "001_intro.py").write_text("# intro", encoding="utf-8")
    (src_dir / "002_arrays.py").write_text("# arrays", encoding="utf-8")
    (src_dir / "005_trees.py").write_text("# trees", encoding="utf-8")
    monkeypatch.setattr(analyzers_module, "get_project_path", lambda _: tmp_path)
    assert next_lesson_number(TargetProject.DSA) == 6


def test_next_lesson_number_non_numbered_files(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    """next_lesson_number should return 1 when no files have numeric prefixes."""
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "helpers.py").write_text("# helpers", encoding="utf-8")
    monkeypatch.setattr(analyzers_module, "get_project_path", lambda _: tmp_path)
    assert next_lesson_number(TargetProject.DSA) == 1


@_skip_no_dsa
def test_next_lesson_number_dsa_real() -> None:
    """next_lesson_number should return > 1 for DSA with existing lessons."""
    num = next_lesson_number(TargetProject.DSA)
    assert num > 1


def test_read_template_with_fallback_project_template(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    """Should return project template when it exists."""
    notes_dir = tmp_path / "notes"
    notes_dir.mkdir()
    (notes_dir / "lesson_template.py").write_text(
        "# project template", encoding="utf-8"
    )
    monkeypatch.setattr(analyzers_module, "get_project_path", lambda _: tmp_path)
    result = read_template_with_fallback(TargetProject.DSA, PedagogyStyle.CONCEPT_FIRST)
    assert result == "# project template"


def test_read_template_with_fallback_builtin(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    """Should fall back to builtin template when project has none."""
    monkeypatch.setattr(analyzers_module, "get_project_path", lambda _: tmp_path)
    result = read_template_with_fallback(
        TargetProject.FASTAPI, PedagogyStyle.APPLICATION_FIRST
    )
    assert "create_app" in result
