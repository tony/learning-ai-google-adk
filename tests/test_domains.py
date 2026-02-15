"""Tests for content_generator.domains — registry and domain lookup."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from content_generator.domains import (
    _REGISTRY,
    DomainConfig,
    _register,
    get_domain,
    list_domains,
)
from content_generator.models import (
    PROJECT_CATEGORIES,
    PedagogyStyle,
    TargetProject,
    TemplateCategory,
)


@pytest.fixture()
def _clean_registry() -> Iterator[None]:
    """Snapshot and restore the registry around each test."""
    original = dict(_REGISTRY)
    yield
    _REGISTRY.clear()
    _REGISTRY.update(original)


@pytest.mark.usefixtures("_clean_registry")
def test_get_domain_returns_registered() -> None:
    """get_domain should return a previously registered config."""
    config = DomainConfig(
        name="_test_reg",
        project=TargetProject.DSA,
        pedagogy=PedagogyStyle.CONCEPT_FIRST,
    )
    _register(config)
    assert get_domain("_test_reg") is config


@pytest.mark.usefixtures("_clean_registry")
def test_get_domain_raises_for_unknown() -> None:
    """get_domain should raise KeyError for unregistered domains."""
    with pytest.raises(KeyError, match="Unknown domain"):
        get_domain("nonexistent_domain_xyz")


@pytest.mark.usefixtures("_clean_registry")
def test_list_domains_returns_sorted() -> None:
    """list_domains should return domain names in sorted order."""
    for name in ("zzz", "aaa", "mmm"):
        _register(
            DomainConfig(
                name=name,
                project=TargetProject.DSA,
                pedagogy=PedagogyStyle.CONCEPT_FIRST,
            ),
        )
    names = list_domains()
    assert "aaa" in names
    assert names == sorted(names)


def test_all_domains_reference_valid_project() -> None:
    """Every registered domain must reference a valid TargetProject."""
    for name in list_domains():
        config = get_domain(name)
        assert config.project in TargetProject


def test_domain_project_path_delegates_to_registry() -> None:
    """DomainConfig.project_path should resolve via get_project_path."""
    config = get_domain("dsa")
    assert config.project_path.is_absolute()
    assert "learning-dsa" in str(config.project_path)


def test_domain_project_type_derived_from_categories() -> None:
    """DomainConfig.project_type should match PROJECT_CATEGORIES."""
    config = get_domain("dsa")
    assert config.project_type == PROJECT_CATEGORIES[config.project]
    assert config.project_type == TemplateCategory.LESSON_BASED


def test_builtin_domains_exist() -> None:
    """The four standard domains should be registered at import time."""
    names = list_domains()
    assert "dsa" in names
    assert "asyncio" in names
    assert "litestar" in names
    assert "fastapi" in names


def test_dsa_domain_config() -> None:
    config = get_domain("dsa")
    assert config.pedagogy == PedagogyStyle.CONCEPT_FIRST
    assert config.lesson_dir == "src/algorithms"
    assert config.doctest_strategy == "deterministic"


def test_asyncio_domain_config() -> None:
    config = get_domain("asyncio")
    assert config.pedagogy == PedagogyStyle.CONCEPT_FIRST
    assert config.doctest_strategy == "ellipsis"


def test_litestar_domain_config() -> None:
    config = get_domain("litestar")
    assert config.pedagogy == PedagogyStyle.INTEGRATION_FIRST


def test_fastapi_domain_config() -> None:
    config = get_domain("fastapi")
    assert config.pedagogy == PedagogyStyle.APPLICATION_FIRST
