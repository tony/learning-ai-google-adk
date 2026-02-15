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


class TestProjectPaths:
    """Tests for the PROJECT_PATHS mapping."""

    def test_all_projects_have_paths(self) -> None:
        for project in TargetProject:
            assert project in PROJECT_PATHS

    def test_paths_are_absolute(self) -> None:
        for path in PROJECT_PATHS.values():
            assert path.is_absolute()

    def test_paths_are_under_study(self) -> None:
        for path in PROJECT_PATHS.values():
            assert "study" in str(path) or "python" in str(path)


class TestGetProjectPath:
    """Tests for get_project_path."""

    def test_returns_path(self) -> None:
        path = get_project_path(TargetProject.DSA)
        assert isinstance(path, pathlib.Path)
        assert "learning-dsa" in str(path)

    def test_all_projects_resolvable(self) -> None:
        for project in TargetProject:
            path = get_project_path(project)
            assert isinstance(path, pathlib.Path)


class TestAllowedRoots:
    """Tests for ALLOWED_ROOTS."""

    def test_is_frozenset(self) -> None:
        assert isinstance(ALLOWED_ROOTS, frozenset)

    def test_contains_all_project_paths(self) -> None:
        for path in PROJECT_PATHS.values():
            assert path in ALLOWED_ROOTS


class TestValidatePath:
    """Tests for validate_path."""

    def test_valid_path_within_project(self) -> None:
        project_path = get_project_path(TargetProject.DSA)
        test_path = project_path / "src" / "test.py"
        result = validate_path(test_path)
        assert result.is_absolute()

    def test_rejects_path_outside_roots(self) -> None:
        with pytest.raises(ValueError, match="not within any allowed"):
            validate_path(pathlib.Path("/tmp/evil/script.py"))

    def test_rejects_path_traversal(self) -> None:
        project_path = get_project_path(TargetProject.DSA)
        traversal_path = project_path / ".." / ".." / "etc" / "passwd"
        with pytest.raises(ValueError, match="not within any allowed"):
            validate_path(traversal_path)

    def test_resolves_symlinks(self) -> None:
        project_path = get_project_path(TargetProject.ASYNCIO)
        dotdot_path = project_path / "src" / ".." / "src" / "test.py"
        result = validate_path(dotdot_path)
        assert ".." not in str(result)


class TestStudyBaseEnvOverride:
    """Tests for CONTENT_GENERATOR_STUDY_BASE env var override."""

    def test_env_var_overrides_study_base(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
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
