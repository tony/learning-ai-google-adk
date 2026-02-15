"""Project registry mapping target projects to filesystem paths.

Provides path resolution and traversal safety for all file operations
targeting learning project directories.
"""

from __future__ import annotations

import os
import pathlib

from .models import TargetProject

#: Base directory containing all learning projects.
_STUDY_BASE = pathlib.Path(
    os.environ.get(
        "CONTENT_GENERATOR_STUDY_BASE", str(pathlib.Path.home() / "study" / "python")
    )
)

#: Maps each target project to its root directory.
PROJECT_PATHS: dict[TargetProject, pathlib.Path] = {
    TargetProject.DSA: _STUDY_BASE / "learning-dsa",
    TargetProject.ASYNCIO: _STUDY_BASE / "learning-asyncio",
    TargetProject.LITESTAR: _STUDY_BASE / "learning-litestar",
    TargetProject.FASTAPI: _STUDY_BASE / "learning-fastapi",
}

#: Roots allowed for file write operations.
ALLOWED_ROOTS: frozenset[pathlib.Path] = frozenset(PROJECT_PATHS.values())


def get_project_path(project: TargetProject) -> pathlib.Path:
    """Return the filesystem path for a target project.

    Parameters
    ----------
    project : TargetProject
        The project to look up.

    Returns
    -------
    pathlib.Path
        Absolute path to the project root.

    Raises
    ------
    KeyError
        If the project is not registered.
    """
    return PROJECT_PATHS[project]


def validate_path(path: pathlib.Path) -> pathlib.Path:
    """Validate that a path is within an allowed project root.

    Resolves symlinks and relative components before checking containment.

    Parameters
    ----------
    path : pathlib.Path
        The path to validate.

    Returns
    -------
    pathlib.Path
        The resolved absolute path.

    Raises
    ------
    ValueError
        If the path is not within any allowed root.
    """
    resolved = path.resolve()
    if any(resolved.is_relative_to(root) for root in ALLOWED_ROOTS):
        return resolved
    msg = f"Path {resolved} is not within any allowed project root"
    raise ValueError(msg)
