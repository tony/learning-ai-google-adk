"""Built-in lesson templates for fallback when projects lack templates.

Ships ``.py.tmpl`` reference files loaded via :mod:`importlib.resources`.
These are reference templates for the LLM (not Jinja2 templates) and
coexist with the Jinja2 rendering in :mod:`content_generator.templates`.
"""

from __future__ import annotations

import importlib.resources

from ..models import PedagogyStyle

_TEMPLATE_MAP: dict[PedagogyStyle, str] = {
    PedagogyStyle.CONCEPT_FIRST: "concept_lesson.py.tmpl",
    PedagogyStyle.INTEGRATION_FIRST: "integration_lesson.py.tmpl",
    PedagogyStyle.APPLICATION_FIRST: "app_scaffold.py.tmpl",
}


def get_builtin_template(style: PedagogyStyle) -> str:
    """Load a built-in template for the given pedagogy style.

    Parameters
    ----------
    style : PedagogyStyle
        The teaching approach to get a template for.

    Returns
    -------
    str
        Template content as a string.
    """
    filename = _TEMPLATE_MAP[style]
    ref = importlib.resources.files("content_generator.builtin_templates").joinpath(
        filename
    )
    return ref.read_text(encoding="utf-8")
