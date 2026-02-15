"""Tests for content_generator.validators."""

from __future__ import annotations

import pathlib
import subprocess

import pytest

import content_generator.validators as validators_module
from content_generator.models import TargetProject
from content_generator.project_registry import get_project_path
from content_generator.validators import (
    _run_tool,
    run_mypy_check,
    run_pytest_doctest,
    run_ruff_check,
    run_ruff_format,
    validate_file,
)


def test_run_tool_success() -> None:
    ok, output = _run_tool(["echo", "hello"], cwd=pathlib.Path())
    assert ok is True
    assert "hello" in output


def test_run_tool_failure() -> None:
    ok, _output = _run_tool(
        ["python", "-c", "import sys; sys.exit(1)"],
        cwd=pathlib.Path(),
    )
    assert ok is False


def test_run_tool_timeout() -> None:
    ok, output = _run_tool(
        ["sleep", "10"],
        cwd=pathlib.Path(),
        timeout=1,
    )
    assert ok is False
    assert "timed out" in output


def test_run_tool_missing_binary() -> None:
    ok, output = _run_tool(
        ["nonexistent_binary_xyz"],
        cwd=pathlib.Path(),
    )
    assert ok is False
    assert "not found" in output.lower()


def test_run_tool_captures_stderr() -> None:
    _ok, output = _run_tool(
        ["python", "-c", "import sys; print('err', file=sys.stderr)"],
        cwd=pathlib.Path(),
    )
    assert "err" in output


def test_run_ruff_format_success(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_result = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout="All checks passed!\n",
        stderr="",
    )
    monkeypatch.setattr(
        validators_module.subprocess, "run", lambda *a, **kw: mock_result
    )
    ok, output = run_ruff_format(pathlib.Path("/fake/test.py"))
    assert ok is True
    assert "All checks passed" in output


def test_run_ruff_check_success(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_result = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout="All checks passed!\n",
        stderr="",
    )
    monkeypatch.setattr(
        validators_module.subprocess, "run", lambda *a, **kw: mock_result
    )
    ok, _output = run_ruff_check(pathlib.Path("/fake/test.py"))
    assert ok is True


def test_run_mypy_check_success(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_result = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout="Success: no issues found\n",
        stderr="",
    )
    monkeypatch.setattr(
        validators_module.subprocess, "run", lambda *a, **kw: mock_result
    )
    ok, output = run_mypy_check(pathlib.Path("/fake/test.py"))
    assert ok is True
    assert "Success" in output


def test_run_pytest_doctest_success(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_result = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout="1 passed\n",
        stderr="",
    )
    monkeypatch.setattr(
        validators_module.subprocess, "run", lambda *a, **kw: mock_result
    )
    ok, _output = run_pytest_doctest(pathlib.Path("/fake/test.py"))
    assert ok is True


def test_run_pytest_doctest_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_result = subprocess.CompletedProcess(
        args=[],
        returncode=1,
        stdout="FAILED test.py\n",
        stderr="",
    )
    monkeypatch.setattr(
        validators_module.subprocess, "run", lambda *a, **kw: mock_result
    )
    ok, output = run_pytest_doctest(pathlib.Path("/fake/test.py"))
    assert ok is False
    assert "FAILED" in output


def test_validate_file_all_pass(monkeypatch: pytest.MonkeyPatch) -> None:
    project_path = get_project_path(TargetProject.DSA)
    fake_file = project_path / "src" / "test_generated.py"

    mock_result = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout="OK\n",
        stderr="",
    )
    monkeypatch.setattr(
        validators_module.subprocess, "run", lambda *a, **kw: mock_result
    )
    result = validate_file(fake_file, project_dir=project_path)
    assert result.passed is True


def test_validate_file_skip_doctest(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify run_doctest=False skips pytest --doctest-modules."""
    project_path = get_project_path(TargetProject.DSA)
    fake_file = project_path / "src" / "test_generated.py"

    call_count = 0
    mock_result = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout="OK\n",
        stderr="",
    )

    def fake_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        nonlocal call_count
        call_count += 1
        return mock_result

    monkeypatch.setattr(validators_module.subprocess, "run", fake_run)
    result = validate_file(fake_file, project_dir=project_path, run_doctest=False)
    assert result.passed is True
    assert result.pytest == ""
    # Should have 3 calls (ruff format, ruff check, mypy) not 4
    assert call_count == 3


def test_validate_file_partial_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    project_path = get_project_path(TargetProject.DSA)
    fake_file = project_path / "src" / "test_generated.py"

    call_count = 0

    def mock_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        nonlocal call_count
        call_count += 1
        # Fail on the third call (mypy)
        if call_count == 3:
            return subprocess.CompletedProcess(
                args=[],
                returncode=1,
                stdout="error: something wrong\n",
                stderr="",
            )
        return subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="OK\n",
            stderr="",
        )

    monkeypatch.setattr(validators_module.subprocess, "run", mock_run)
    result = validate_file(fake_file, project_dir=project_path)
    assert result.passed is False
    assert "error" in result.mypy
