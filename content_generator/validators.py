"""CI validation subprocess runners for generated content.

Runs ruff, mypy, and pytest as subprocesses against target project
directories, returning structured validation results.
"""

from __future__ import annotations

import pathlib
import subprocess

from .models import ValidationResult
from .project_registry import validate_path


def _run_tool(
    args: list[str],
    *,
    cwd: pathlib.Path,
    timeout: int = 60,
) -> tuple[bool, str]:
    """Run a validation tool as a subprocess.

    Parameters
    ----------
    args : list[str]
        Command and arguments as a list (no shell interpolation).
    cwd : pathlib.Path
        Working directory for the subprocess.
    timeout : int
        Maximum execution time in seconds.

    Returns
    -------
    tuple[bool, str]
        Tuple of (success, combined stdout+stderr output).
    """
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return False, f"Command timed out after {timeout}s: {' '.join(args)}"
    except FileNotFoundError:
        return False, f"Command not found: {args[0]}"
    else:
        output = (result.stdout + result.stderr).strip()
        return result.returncode == 0, output


def run_ruff_format(
    file_path: pathlib.Path,
    *,
    project_dir: pathlib.Path | None = None,
) -> tuple[bool, str]:
    """Run ``ruff format --check`` on a file.

    Parameters
    ----------
    file_path : pathlib.Path
        Path to the file to check.
    project_dir : pathlib.Path | None
        Working directory. Defaults to file's parent.

    Returns
    -------
    tuple[bool, str]
        Tuple of (passed, output).
    """
    cwd = project_dir or file_path.parent
    return _run_tool(
        ["uv", "run", "ruff", "format", "--check", str(file_path)],
        cwd=cwd,
    )


def run_ruff_check(
    file_path: pathlib.Path,
    *,
    project_dir: pathlib.Path | None = None,
) -> tuple[bool, str]:
    """Run ``ruff check`` on a file.

    Parameters
    ----------
    file_path : pathlib.Path
        Path to the file to check.
    project_dir : pathlib.Path | None
        Working directory. Defaults to file's parent.

    Returns
    -------
    tuple[bool, str]
        Tuple of (passed, output).
    """
    cwd = project_dir or file_path.parent
    return _run_tool(
        ["uv", "run", "ruff", "check", str(file_path)],
        cwd=cwd,
    )


def run_mypy_check(
    file_path: pathlib.Path,
    *,
    project_dir: pathlib.Path | None = None,
) -> tuple[bool, str]:
    """Run ``mypy`` on a file.

    Parameters
    ----------
    file_path : pathlib.Path
        Path to the file to check.
    project_dir : pathlib.Path | None
        Working directory. Defaults to file's parent.

    Returns
    -------
    tuple[bool, str]
        Tuple of (passed, output).
    """
    cwd = project_dir or file_path.parent
    return _run_tool(
        ["uv", "run", "mypy", str(file_path)],
        cwd=cwd,
    )


def run_pytest_doctest(
    file_path: pathlib.Path,
    *,
    project_dir: pathlib.Path | None = None,
) -> tuple[bool, str]:
    """Run ``pytest --doctest-modules`` on a file.

    Parameters
    ----------
    file_path : pathlib.Path
        Path to the file to check.
    project_dir : pathlib.Path | None
        Working directory. Defaults to file's parent.

    Returns
    -------
    tuple[bool, str]
        Tuple of (passed, output).
    """
    cwd = project_dir or file_path.parent
    return _run_tool(
        ["uv", "run", "pytest", "--doctest-modules", str(file_path)],
        cwd=cwd,
    )


def validate_file(
    file_path: pathlib.Path,
    *,
    project_dir: pathlib.Path | None = None,
) -> ValidationResult:
    """Run all validation checks on a file.

    Runs ruff format, ruff check, mypy, and pytest doctest sequentially.

    Parameters
    ----------
    file_path : pathlib.Path
        Path to the file to validate. Must be within an allowed project root.
    project_dir : pathlib.Path | None
        Working directory for tools. Defaults to file's parent.

    Returns
    -------
    ValidationResult
        Structured result with output from each tool.

    Raises
    ------
    ValueError
        If file_path is not within any allowed project root.
    """
    validate_path(file_path)
    cwd = project_dir or file_path.parent

    fmt_ok, fmt_out = run_ruff_format(file_path, project_dir=cwd)
    lint_ok, lint_out = run_ruff_check(file_path, project_dir=cwd)
    mypy_ok, mypy_out = run_mypy_check(file_path, project_dir=cwd)
    test_ok, test_out = run_pytest_doctest(file_path, project_dir=cwd)

    return ValidationResult(
        passed=all([fmt_ok, lint_ok, mypy_ok, test_ok]),
        ruff_format=fmt_out,
        ruff_lint=lint_out,
        mypy=mypy_out,
        pytest=test_out,
    )
