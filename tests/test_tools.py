"""Tests for content_generator.tools.

Verifies all tool functions have proper type annotations and docstrings
required by ADK FunctionTool, plus basic functional behavior.
"""

from __future__ import annotations

import inspect
import typing as t
from unittest.mock import MagicMock, patch

import pytest

from content_generator import tools
from content_generator.models import TargetProject, ValidationResult
from content_generator.project_registry import get_project_path

#: All tool functions that will be wrapped by FunctionTool.
TOOL_FUNCTIONS = [
    tools.analyze_target_project,
    tools.get_existing_content,
    tools.read_template,
    tools.read_progression_plan,
    tools.read_source_reference,
    tools.write_generated_file,
    tools.validate_generated_content,
    tools.run_ruff_format,
    tools.run_ruff_check,
    tools.run_mypy_check,
    tools.run_pytest_doctest,
]

_DSA_PATH = get_project_path(TargetProject.DSA)
_skip_no_dsa = pytest.mark.skipif(
    not _DSA_PATH.exists(),
    reason="learning-dsa project not found",
)


class TestToolAnnotations:
    """Tests that all tool functions meet FunctionTool requirements."""

    @pytest.mark.parametrize("func", TOOL_FUNCTIONS, ids=lambda f: f.__name__)
    def test_has_docstring(self, func: t.Callable[..., t.Any]) -> None:
        assert callable(func)
        assert func.__doc__ is not None
        assert len(func.__doc__) > 10

    @pytest.mark.parametrize("func", TOOL_FUNCTIONS, ids=lambda f: f.__name__)
    def test_has_return_annotation(self, func: t.Callable[..., t.Any]) -> None:
        assert callable(func)
        sig = inspect.signature(func)
        assert sig.return_annotation != inspect.Parameter.empty

    @pytest.mark.parametrize("func", TOOL_FUNCTIONS, ids=lambda f: f.__name__)
    def test_all_params_annotated(self, func: t.Callable[..., t.Any]) -> None:
        assert callable(func)
        sig = inspect.signature(func)
        for name, param in sig.parameters.items():
            assert param.annotation != inspect.Parameter.empty, (
                f"Parameter {name!r} in {func.__name__} has no annotation"
            )

    @pytest.mark.parametrize("func", TOOL_FUNCTIONS, ids=lambda f: f.__name__)
    def test_returns_str(self, func: t.Callable[..., t.Any]) -> None:
        assert callable(func)
        sig = inspect.signature(func)
        assert sig.return_annotation == "str"


class TestAnalyzeTargetProject:
    """Tests for analyze_target_project."""

    @_skip_no_dsa
    def test_dsa_analysis(self) -> None:
        result = tools.analyze_target_project("learning-dsa")
        assert "learning-dsa" in result
        assert "Mypy strict: True" in result

    def test_invalid_project(self) -> None:
        with pytest.raises(ValueError):
            tools.analyze_target_project("nonexistent")


class TestGetExistingContent:
    """Tests for get_existing_content."""

    @_skip_no_dsa
    def test_dsa_content(self) -> None:
        result = tools.get_existing_content("learning-dsa")
        assert "Found" in result


class TestReadTemplate:
    """Tests for read_template."""

    @_skip_no_dsa
    def test_dsa_template(self) -> None:
        result = tools.read_template("learning-dsa")
        assert "TEMPLATE" in result or "CONVENTIONS" in result


class TestReadProgressionPlan:
    """Tests for read_progression_plan."""

    @_skip_no_dsa
    def test_returns_string(self) -> None:
        result = tools.read_progression_plan("learning-dsa")
        assert isinstance(result, str)


class TestReadSourceReference:
    """Tests for read_source_reference."""

    def test_invalid_path_raises(self) -> None:
        with pytest.raises(ValueError, match="not within any allowed"):
            tools.read_source_reference("learning-dsa", "../../etc/passwd")


class TestValidateGeneratedContent:
    """Tests for validate_generated_content."""

    def test_rejects_invalid_path(self) -> None:
        with pytest.raises(ValueError, match="not within any allowed"):
            tools.validate_generated_content("learning-dsa", "../../etc/passwd")

    def test_returns_fail_on_validation_errors(self) -> None:
        """Verify FAIL output includes all non-empty tool outputs."""
        fail_result = ValidationResult(
            passed=False,
            ruff_format="1 file would be reformatted",
            ruff_lint="",
            mypy="error: Name 'x' is not defined",
            pytest="",
        )
        with patch(
            "content_generator.tools.validators.validate_file",
            return_value=fail_result,
        ):
            result = tools.validate_generated_content("learning-dsa", "src/test.py")
        assert result.startswith("FAIL:")
        assert "RUFF FORMAT" in result
        assert "MYPY" in result
        # Empty sections should not appear
        assert "RUFF LINT" not in result
        assert "PYTEST" not in result


class TestWriteGeneratedFile:
    """Tests for write_generated_file."""

    def test_writes_file_and_updates_state(self, tmp_path: t.Any) -> None:
        """Verify file write, directory creation, and state update."""
        mock_context = MagicMock()
        mock_context.state = {}

        project_path = tmp_path / "learning-dsa"
        project_path.mkdir()

        with (
            patch(
                "content_generator.tools.get_project_path",
                return_value=project_path,
            ),
            patch(
                "content_generator.tools.validate_path",
                side_effect=lambda p: p.resolve(),
            ),
        ):
            result = tools.write_generated_file(
                "learning-dsa",
                "src/lesson_01.py",
                "# hello world\n",
                mock_context,
            )

        assert "Successfully wrote" in result
        assert "14 bytes" in result
        written_file = project_path / "src" / "lesson_01.py"
        assert written_file.exists()
        assert written_file.read_text(encoding="utf-8") == "# hello world\n"
        assert "last_written_file" in mock_context.state
        assert "last_written_project" in mock_context.state
        assert mock_context.state["last_written_project"] == "learning-dsa"

    def test_creates_parent_directories(self, tmp_path: t.Any) -> None:
        """Verify nested directory creation."""
        mock_context = MagicMock()
        mock_context.state = {}

        project_path = tmp_path / "learning-dsa"
        project_path.mkdir()

        with (
            patch(
                "content_generator.tools.get_project_path",
                return_value=project_path,
            ),
            patch(
                "content_generator.tools.validate_path",
                side_effect=lambda p: p.resolve(),
            ),
        ):
            tools.write_generated_file(
                "learning-dsa",
                "src/deep/nested/file.py",
                "content",
                mock_context,
            )

        assert (project_path / "src" / "deep" / "nested" / "file.py").exists()


class TestValidationTools:
    """Tests for individual validation tool wrappers."""

    def test_ruff_format_rejects_invalid_path(self) -> None:
        with pytest.raises(ValueError, match="not within any allowed"):
            tools.run_ruff_format("learning-dsa", "../../etc/passwd")

    def test_ruff_check_rejects_invalid_path(self) -> None:
        with pytest.raises(ValueError, match="not within any allowed"):
            tools.run_ruff_check("learning-dsa", "../../etc/passwd")

    def test_mypy_check_rejects_invalid_path(self) -> None:
        with pytest.raises(ValueError, match="not within any allowed"):
            tools.run_mypy_check("learning-dsa", "../../etc/passwd")

    def test_pytest_doctest_rejects_invalid_path(self) -> None:
        with pytest.raises(ValueError, match="not within any allowed"):
            tools.run_pytest_doctest("learning-dsa", "../../etc/passwd")
