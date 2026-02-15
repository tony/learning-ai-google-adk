"""Tests for content_generator.tools.

Verifies all tool functions have proper type annotations and docstrings
required by ADK FunctionTool, plus basic functional behavior.
"""

from __future__ import annotations

import inspect
import typing as t

import pytest

import content_generator.tools as tools_module
from content_generator import tools
from content_generator.models import TargetProject, ValidationResult
from content_generator.project_registry import get_project_path


class ToolFixture(t.NamedTuple):
    """Parametrize fixture pairing a test ID with a tool function."""

    test_id: str
    func: t.Callable[..., t.Any]


TOOL_FIXTURES = [
    ToolFixture(test_id="analyze_target_project", func=tools.analyze_target_project),
    ToolFixture(test_id="get_existing_content", func=tools.get_existing_content),
    ToolFixture(test_id="read_template", func=tools.read_template),
    ToolFixture(test_id="read_progression_plan", func=tools.read_progression_plan),
    ToolFixture(test_id="read_source_reference", func=tools.read_source_reference),
    ToolFixture(test_id="write_generated_file", func=tools.write_generated_file),
    ToolFixture(
        test_id="validate_generated_content",
        func=tools.validate_generated_content,
    ),
    ToolFixture(test_id="run_ruff_format", func=tools.run_ruff_format),
    ToolFixture(test_id="run_ruff_check", func=tools.run_ruff_check),
    ToolFixture(test_id="run_mypy_check", func=tools.run_mypy_check),
    ToolFixture(test_id="run_pytest_doctest", func=tools.run_pytest_doctest),
]

_DSA_PATH = get_project_path(TargetProject.DSA)
_skip_no_dsa = pytest.mark.skipif(
    not _DSA_PATH.exists(),
    reason="learning-dsa project not found",
)


@pytest.mark.parametrize(
    list(ToolFixture._fields),
    TOOL_FIXTURES,
    ids=[f.test_id for f in TOOL_FIXTURES],
)
def test_tool_has_docstring(test_id: str, func: t.Callable[..., t.Any]) -> None:
    assert callable(func)
    assert func.__doc__ is not None
    assert len(func.__doc__) > 10


@pytest.mark.parametrize(
    list(ToolFixture._fields),
    TOOL_FIXTURES,
    ids=[f.test_id for f in TOOL_FIXTURES],
)
def test_tool_has_return_annotation(test_id: str, func: t.Callable[..., t.Any]) -> None:
    assert callable(func)
    sig = inspect.signature(func)
    assert sig.return_annotation != inspect.Parameter.empty


@pytest.mark.parametrize(
    list(ToolFixture._fields),
    TOOL_FIXTURES,
    ids=[f.test_id for f in TOOL_FIXTURES],
)
def test_tool_all_params_annotated(test_id: str, func: t.Callable[..., t.Any]) -> None:
    assert callable(func)
    sig = inspect.signature(func)
    for name, param in sig.parameters.items():
        assert param.annotation != inspect.Parameter.empty, (
            f"Parameter {name!r} in {func.__name__} has no annotation"
        )


@pytest.mark.parametrize(
    list(ToolFixture._fields),
    TOOL_FIXTURES,
    ids=[f.test_id for f in TOOL_FIXTURES],
)
def test_tool_returns_str(test_id: str, func: t.Callable[..., t.Any]) -> None:
    assert callable(func)
    sig = inspect.signature(func)
    assert sig.return_annotation == "str"


@_skip_no_dsa
def test_analyze_target_project_dsa() -> None:
    result = tools.analyze_target_project("learning-dsa")
    assert "learning-dsa" in result
    assert "Mypy strict: True" in result


def test_analyze_target_project_invalid() -> None:
    with pytest.raises(ValueError):
        tools.analyze_target_project("nonexistent")


@_skip_no_dsa
def test_get_existing_content_dsa() -> None:
    result = tools.get_existing_content("learning-dsa")
    assert "Found" in result


@_skip_no_dsa
def test_read_template_dsa() -> None:
    result = tools.read_template("learning-dsa")
    assert "TEMPLATE" in result or "CONVENTIONS" in result


@_skip_no_dsa
def test_read_progression_plan_returns_string() -> None:
    result = tools.read_progression_plan("learning-dsa")
    assert isinstance(result, str)


def test_read_source_reference_invalid_path_raises() -> None:
    with pytest.raises(ValueError, match="not within any allowed"):
        tools.read_source_reference("learning-dsa", "../../etc/passwd")


def test_validate_generated_content_rejects_invalid_path() -> None:
    with pytest.raises(ValueError, match="not within any allowed"):
        tools.validate_generated_content("learning-dsa", "../../etc/passwd")


def test_validate_generated_content_returns_fail(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify FAIL output includes all non-empty tool outputs."""
    fail_result = ValidationResult(
        passed=False,
        ruff_format="1 file would be reformatted",
        ruff_lint="",
        mypy="error: Name 'x' is not defined",
        pytest="",
    )
    monkeypatch.setattr(
        tools_module.validators,
        "validate_file",
        lambda *a, **kw: fail_result,  # type: ignore[attr-defined]
    )
    result = tools.validate_generated_content("learning-dsa", "src/test.py")
    assert result.startswith("FAIL:")
    assert "RUFF FORMAT" in result
    assert "MYPY" in result
    # Empty sections should not appear
    assert "RUFF LINT" not in result
    assert "PYTEST" not in result


def test_write_generated_file_writes_and_updates_state(
    monkeypatch: pytest.MonkeyPatch,
    fake_tool_context: t.Any,
    tmp_path: t.Any,
) -> None:
    """Verify file write, directory creation, and state update."""
    project_path = tmp_path / "learning-dsa"
    project_path.mkdir()

    monkeypatch.setattr(tools_module, "get_project_path", lambda _: project_path)
    monkeypatch.setattr(tools_module, "validate_path", lambda p: p.resolve())

    result = tools.write_generated_file(
        "learning-dsa",
        "src/lesson_01.py",
        "# hello world\n",
        fake_tool_context,
    )

    assert "Successfully wrote" in result
    assert "14 bytes" in result
    written_file = project_path / "src" / "lesson_01.py"
    assert written_file.exists()
    assert written_file.read_text(encoding="utf-8") == "# hello world\n"
    assert "last_written_file" in fake_tool_context.state
    assert "last_written_project" in fake_tool_context.state
    assert fake_tool_context.state["last_written_project"] == "learning-dsa"


def test_write_generated_file_creates_parent_directories(
    monkeypatch: pytest.MonkeyPatch,
    fake_tool_context: t.Any,
    tmp_path: t.Any,
) -> None:
    """Verify nested directory creation."""
    project_path = tmp_path / "learning-dsa"
    project_path.mkdir()

    monkeypatch.setattr(tools_module, "get_project_path", lambda _: project_path)
    monkeypatch.setattr(tools_module, "validate_path", lambda p: p.resolve())

    tools.write_generated_file(
        "learning-dsa",
        "src/deep/nested/file.py",
        "content",
        fake_tool_context,
    )

    assert (project_path / "src" / "deep" / "nested" / "file.py").exists()


def test_validation_ruff_format_rejects_invalid_path() -> None:
    with pytest.raises(ValueError, match="not within any allowed"):
        tools.run_ruff_format("learning-dsa", "../../etc/passwd")


def test_validation_ruff_check_rejects_invalid_path() -> None:
    with pytest.raises(ValueError, match="not within any allowed"):
        tools.run_ruff_check("learning-dsa", "../../etc/passwd")


def test_validation_mypy_check_rejects_invalid_path() -> None:
    with pytest.raises(ValueError, match="not within any allowed"):
        tools.run_mypy_check("learning-dsa", "../../etc/passwd")


def test_validation_pytest_doctest_rejects_invalid_path() -> None:
    with pytest.raises(ValueError, match="not within any allowed"):
        tools.run_pytest_doctest("learning-dsa", "../../etc/passwd")
