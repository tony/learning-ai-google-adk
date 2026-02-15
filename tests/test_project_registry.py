"""Tests for content_generator.project_registry."""

from __future__ import annotations

import importlib
import pathlib

import pytest

import content_generator.project_registry as project_registry_module
from content_generator.models import TargetProject
from content_generator.project_registry import (
    ALLOWED_ROOTS,
    PROJECT_PATHS,
    get_project_path,
    validate_path,
)


def test_project_paths_all_have_paths() -> None:
    for project in TargetProject:
        assert project in PROJECT_PATHS


def test_project_paths_are_absolute() -> None:
    for path in PROJECT_PATHS.values():
        assert path.is_absolute()


def test_project_paths_under_study() -> None:
    for path in PROJECT_PATHS.values():
        assert "study" in str(path) or "python" in str(path)


def test_get_project_path_returns_path() -> None:
    path = get_project_path(TargetProject.DSA)
    assert isinstance(path, pathlib.Path)
    assert "learning-dsa" in str(path)


def test_get_project_path_all_resolvable() -> None:
    for project in TargetProject:
        path = get_project_path(project)
        assert isinstance(path, pathlib.Path)


def test_allowed_roots_is_frozenset() -> None:
    assert isinstance(ALLOWED_ROOTS, frozenset)


def test_allowed_roots_contains_all_project_paths() -> None:
    for path in PROJECT_PATHS.values():
        assert path in ALLOWED_ROOTS


def test_validate_path_within_project() -> None:
    project_path = get_project_path(TargetProject.DSA)
    test_path = project_path / "src" / "test.py"
    result = validate_path(test_path)
    assert result.is_absolute()


def test_validate_path_rejects_outside_roots() -> None:
    with pytest.raises(ValueError, match="not within any allowed"):
        validate_path(pathlib.Path("/tmp/evil/script.py"))


def test_validate_path_rejects_traversal() -> None:
    project_path = get_project_path(TargetProject.DSA)
    traversal_path = project_path / ".." / ".." / "etc" / "passwd"
    with pytest.raises(ValueError, match="not within any allowed"):
        validate_path(traversal_path)


def test_validate_path_resolves_symlinks() -> None:
    project_path = get_project_path(TargetProject.ASYNCIO)
    dotdot_path = project_path / "src" / ".." / "src" / "test.py"
    result = validate_path(dotdot_path)
    assert ".." not in str(result)


def test_study_base_env_override(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    monkeypatch.setenv("CONTENT_GENERATOR_STUDY_BASE", str(tmp_path))
    importlib.reload(project_registry_module)
    try:
        reloaded_base = project_registry_module._STUDY_BASE
        assert reloaded_base == tmp_path
        dsa_path = project_registry_module.PROJECT_PATHS[TargetProject.DSA]
        assert str(dsa_path).startswith(str(tmp_path))
    finally:
        monkeypatch.delenv("CONTENT_GENERATOR_STUDY_BASE")
        importlib.reload(project_registry_module)
