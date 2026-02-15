"""Tests for content_generator.validators."""

from __future__ import annotations

import pathlib
import subprocess
from unittest.mock import patch

import pytest

from content_generator.validators import (
    _run_tool,
    run_mypy_check,
    run_pytest_doctest,
    run_ruff_check,
    run_ruff_format,
    validate_file,
)


class TestRunTool:
    """Tests for the _run_tool helper."""

    def test_successful_command(self) -> None:
        ok, output = _run_tool(["echo", "hello"], cwd=pathlib.Path())
        assert ok is True
        assert "hello" in output

    def test_failing_command(self) -> None:
        ok, _output = _run_tool(
            ["python", "-c", "import sys; sys.exit(1)"],
            cwd=pathlib.Path(),
        )
        assert ok is False

    def test_timeout_handling(self) -> None:
        ok, output = _run_tool(
            ["sleep", "10"],
            cwd=pathlib.Path(),
            timeout=1,
        )
        assert ok is False
        assert "timed out" in output

    def test_missing_binary(self) -> None:
        ok, output = _run_tool(
            ["nonexistent_binary_xyz"],
            cwd=pathlib.Path(),
        )
        assert ok is False
        assert "not found" in output.lower()

    def test_captures_stderr(self) -> None:
        _ok, output = _run_tool(
            ["python", "-c", "import sys; print('err', file=sys.stderr)"],
            cwd=pathlib.Path(),
        )
        assert "err" in output


class TestRunRuffFormat:
    """Tests for run_ruff_format."""

    def test_with_mock(self) -> None:
        mock_result = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="All checks passed!\n",
            stderr="",
        )
        with patch(
            "content_generator.validators.subprocess.run", return_value=mock_result
        ):
            ok, output = run_ruff_format(pathlib.Path("/fake/test.py"))
            assert ok is True
            assert "All checks passed" in output


class TestRunRuffCheck:
    """Tests for run_ruff_check."""

    def test_with_mock(self) -> None:
        mock_result = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="All checks passed!\n",
            stderr="",
        )
        with patch(
            "content_generator.validators.subprocess.run", return_value=mock_result
        ):
            ok, _output = run_ruff_check(pathlib.Path("/fake/test.py"))
            assert ok is True


class TestRunMypyCheck:
    """Tests for run_mypy_check."""

    def test_with_mock(self) -> None:
        mock_result = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="Success: no issues found\n",
            stderr="",
        )
        with patch(
            "content_generator.validators.subprocess.run", return_value=mock_result
        ):
            ok, output = run_mypy_check(pathlib.Path("/fake/test.py"))
            assert ok is True
            assert "Success" in output


class TestRunPytestDoctest:
    """Tests for run_pytest_doctest."""

    def test_with_mock(self) -> None:
        mock_result = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="1 passed\n",
            stderr="",
        )
        with patch(
            "content_generator.validators.subprocess.run", return_value=mock_result
        ):
            ok, _output = run_pytest_doctest(pathlib.Path("/fake/test.py"))
            assert ok is True

    def test_failure_with_mock(self) -> None:
        mock_result = subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout="FAILED test.py\n",
            stderr="",
        )
        with patch(
            "content_generator.validators.subprocess.run", return_value=mock_result
        ):
            ok, output = run_pytest_doctest(pathlib.Path("/fake/test.py"))
            assert ok is False
            assert "FAILED" in output


class TestValidateFile:
    """Tests for validate_file."""

    def test_rejects_path_outside_roots(self) -> None:
        with pytest.raises(ValueError, match="not within any allowed"):
            validate_file(pathlib.Path("/tmp/evil.py"))

    def test_all_pass(self) -> None:
        from content_generator.models import TargetProject
        from content_generator.project_registry import get_project_path

        project_path = get_project_path(TargetProject.DSA)
        fake_file = project_path / "src" / "test_generated.py"

        mock_result = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="OK\n",
            stderr="",
        )
        with patch(
            "content_generator.validators.subprocess.run", return_value=mock_result
        ):
            result = validate_file(fake_file, project_dir=project_path)
            assert result.passed is True

    def test_partial_failure(self) -> None:
        from content_generator.models import TargetProject
        from content_generator.project_registry import get_project_path

        project_path = get_project_path(TargetProject.DSA)
        fake_file = project_path / "src" / "test_generated.py"

        call_count = 0

        def mock_run(
            *args: object, **kwargs: object
        ) -> subprocess.CompletedProcess[str]:
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

        with patch("content_generator.validators.subprocess.run", side_effect=mock_run):
            result = validate_file(fake_file, project_dir=project_path)
            assert result.passed is False
            assert "error" in result.mypy
