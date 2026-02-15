"""Tests for content_generator.builtin_templates."""

from __future__ import annotations

import typing as t

import pytest

from content_generator.builtin_templates import get_builtin_template
from content_generator.models import PedagogyStyle


class TemplateFixture(t.NamedTuple):
    """Parametrized fixture for builtin template loading."""

    test_id: str
    style: PedagogyStyle
    expected_marker: str


TEMPLATE_FIXTURES: list[TemplateFixture] = [
    TemplateFixture(
        test_id="concept_first",
        style=PedagogyStyle.CONCEPT_FIRST,
        expected_marker="demonstrate_concept",
    ),
    TemplateFixture(
        test_id="integration_first",
        style=PedagogyStyle.INTEGRATION_FIRST,
        expected_marker="build_pipeline",
    ),
    TemplateFixture(
        test_id="application_first",
        style=PedagogyStyle.APPLICATION_FIRST,
        expected_marker="create_app",
    ),
]


@pytest.mark.parametrize(
    list(TemplateFixture._fields),
    TEMPLATE_FIXTURES,
    ids=[f.test_id for f in TEMPLATE_FIXTURES],
)
def test_builtin_template_loads(
    test_id: str,
    style: PedagogyStyle,
    expected_marker: str,
) -> None:
    """Each pedagogy style should load a non-empty template."""
    content = get_builtin_template(style)
    assert len(content) > 0
    assert expected_marker in content


@pytest.mark.parametrize(
    list(TemplateFixture._fields),
    TEMPLATE_FIXTURES,
    ids=[f.test_id for f in TEMPLATE_FIXTURES],
)
def test_builtin_template_has_future_annotations(
    test_id: str,
    style: PedagogyStyle,
    expected_marker: str,
) -> None:
    """All templates should use from __future__ import annotations."""
    content = get_builtin_template(style)
    assert "from __future__ import annotations" in content


def test_all_pedagogy_styles_have_templates() -> None:
    """Every PedagogyStyle should have a corresponding builtin template."""
    for style in PedagogyStyle:
        content = get_builtin_template(style)
        assert len(content) > 0
