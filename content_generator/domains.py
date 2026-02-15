"""Static domain registry for content generation.

Maps domain names (e.g. ``"dsa"``, ``"asyncio"``) to generation
configuration including pedagogy style, lesson directory, and
validation options.  Domain configs reference :class:`TargetProject`
and delegate path resolution to :func:`get_project_path`.
"""

from __future__ import annotations

import pathlib

from pydantic import BaseModel, Field

from .models import (
    PROJECT_CATEGORIES,
    PedagogyStyle,
    TargetProject,
    TemplateCategory,
)
from .project_registry import get_project_path

_REGISTRY: dict[str, DomainConfig] = {}


class DomainConfig(BaseModel):
    """Configuration for a content generation domain.

    Parameters
    ----------
    name : str
        Domain identifier (e.g. ``"dsa"``, ``"asyncio"``).
    project : TargetProject
        The target learning project.
    pedagogy : PedagogyStyle
        Teaching approach to use.
    lesson_dir : str
        Subdirectory within the project for lessons.
    template_path : str | None
        Relative path to a lesson template within the project.
    source_refs : dict[str, str]
        Mapping of reference names to paths for source material.
    strict_mypy : bool
        Whether to run mypy in strict mode for validation.
    doctest_strategy : str
        How to handle doctests: ``"deterministic"``, ``"ellipsis"``,
        or ``"skip"``.
    """

    name: str
    project: TargetProject
    pedagogy: PedagogyStyle
    lesson_dir: str = "src"
    template_path: str | None = None
    source_refs: dict[str, str] = Field(default_factory=dict)
    strict_mypy: bool = True
    doctest_strategy: str = "deterministic"

    @property
    def project_path(self) -> pathlib.Path:
        """Resolve the filesystem path for this domain's project."""
        return get_project_path(self.project)

    @property
    def project_type(self) -> TemplateCategory:
        """Derive the template category from the project."""
        return PROJECT_CATEGORIES[self.project]


def _register(config: DomainConfig) -> None:
    """Register a domain configuration."""
    _REGISTRY[config.name] = config


def get_domain(name: str) -> DomainConfig:
    """Look up a domain by name.

    Parameters
    ----------
    name : str
        Domain identifier.

    Returns
    -------
    DomainConfig
        The domain configuration.

    Raises
    ------
    KeyError
        If the domain is not registered.
    """
    if name not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY))
        msg = f"Unknown domain {name!r}. Available: {available}"
        raise KeyError(msg)
    return _REGISTRY[name]


def list_domains() -> list[str]:
    """Return sorted list of registered domain names.

    Returns
    -------
    list[str]
        Available domain names.
    """
    return sorted(_REGISTRY)


# ---------------------------------------------------------------------------
# Registered domains
# ---------------------------------------------------------------------------

_register(
    DomainConfig(
        name="dsa",
        project=TargetProject.DSA,
        pedagogy=PedagogyStyle.CONCEPT_FIRST,
        lesson_dir="src/algorithms",
        template_path="notes/lesson_template.py",
        source_refs={
            "cpython": str(pathlib.Path.home() / "study" / "c" / "cpython"),
        },
        strict_mypy=True,
        doctest_strategy="deterministic",
    ),
)

_register(
    DomainConfig(
        name="asyncio",
        project=TargetProject.ASYNCIO,
        pedagogy=PedagogyStyle.CONCEPT_FIRST,
        lesson_dir="src",
        template_path="notes/lesson_template.py",
        source_refs={
            "cpython": str(pathlib.Path.home() / "study" / "c" / "cpython"),
        },
        strict_mypy=True,
        doctest_strategy="ellipsis",
    ),
)

_register(
    DomainConfig(
        name="litestar",
        project=TargetProject.LITESTAR,
        pedagogy=PedagogyStyle.INTEGRATION_FIRST,
        lesson_dir="src",
        strict_mypy=True,
        doctest_strategy="skip",
    ),
)

_register(
    DomainConfig(
        name="fastapi",
        project=TargetProject.FASTAPI,
        pedagogy=PedagogyStyle.APPLICATION_FIRST,
        lesson_dir="src",
        strict_mypy=True,
        doctest_strategy="skip",
    ),
)
