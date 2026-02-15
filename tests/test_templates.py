"""Tests for content_generator.templates."""

from __future__ import annotations

import ast

import jinja2
import pytest

from content_generator.templates import (
    render_app_template,
    render_app_test_template,
    render_asyncio_lesson_template,
    render_lesson_template,
)


def test_render_lesson_template_basic() -> None:
    result = render_lesson_template(
        module_docstring="Test lesson.",
        body="def foo() -> int:\n    return 1",
    )
    assert "from __future__ import annotations" in result
    assert "Test lesson." in result
    assert "def foo() -> int:" in result
    assert "doctest.testmod()" in result
    assert "main()" in result


def test_render_lesson_template_includes_shebang() -> None:
    result = render_lesson_template(
        module_docstring="Test.",
        body="pass",
    )
    assert result.startswith("#!/usr/bin/env python")


def test_render_lesson_template_custom_imports() -> None:
    result = render_lesson_template(
        module_docstring="Test.",
        imports="import timeit",
        body="pass",
    )
    assert "import timeit" in result


def test_render_lesson_template_custom_main() -> None:
    result = render_lesson_template(
        module_docstring="Test.",
        body="pass",
        main_docstring="Run the demo.",
        main_body="print('hello')",
    )
    assert "Run the demo." in result
    assert "print('hello')" in result


def test_render_lesson_template_valid_python() -> None:
    result = render_lesson_template(
        module_docstring="Valid Python test.",
        imports="import os",
        body='def greet() -> str:\n    """Greet."""\n    return "hi"',
        main_body="print(greet())",
    )
    # Must parse without errors
    ast.parse(result)


def test_render_lesson_template_future_annotations() -> None:
    result = render_lesson_template(
        module_docstring="Test.",
        body="pass",
    )
    lines = result.split("\n")
    future_line = next(
        (i for i, line in enumerate(lines) if "__future__" in line),
        None,
    )
    assert future_line is not None


def test_render_asyncio_lesson_template_basic() -> None:
    result = render_asyncio_lesson_template(
        module_docstring="Async lesson.",
        body="async def demo() -> None:\n    await asyncio.sleep(0.001)",
    )
    assert "import asyncio" in result
    assert "async def main()" in result
    assert "asyncio.run(main())" in result


def test_render_asyncio_lesson_template_valid_python() -> None:
    result = render_asyncio_lesson_template(
        module_docstring="Async test.",
        body=('async def demo() -> None:\n    """Demo."""\n    await asyncio.sleep(0)'),
        main_body="await demo()",
    )
    ast.parse(result)


def test_render_asyncio_lesson_template_includes_doctest() -> None:
    result = render_asyncio_lesson_template(
        module_docstring="Test.",
        body="pass",
    )
    assert "doctest.testmod()" in result


def test_render_app_template_basic() -> None:
    result = render_app_template(
        module_docstring="App module.",
        body="app = None",
    )
    assert "from __future__ import annotations" in result
    assert "App module." in result
    assert "app = None" in result


def test_render_app_template_no_shebang() -> None:
    result = render_app_template(
        module_docstring="Test.",
        body="pass",
    )
    assert not result.startswith("#!")


def test_render_app_template_valid_python() -> None:
    result = render_app_template(
        module_docstring="App test.",
        imports="import typing",
        body="x: typing.Any = None",
    )
    ast.parse(result)


def test_render_app_test_template_basic() -> None:
    result = render_app_test_template(
        module_docstring="Test module.",
        body="def test_example() -> None:\n    assert True",
    )
    assert "from __future__ import annotations" in result
    assert "def test_example()" in result


def test_render_app_test_template_valid_python() -> None:
    result = render_app_test_template(
        module_docstring="Tests.",
        imports="import pytest",
        body="def test_it() -> None:\n    assert 1 == 1",
    )
    ast.parse(result)


def test_strict_undefined_missing_variable_raises() -> None:
    from content_generator.templates import _ENV

    template = _ENV.from_string("{{ missing_var }}")
    with pytest.raises(jinja2.UndefinedError):
        template.render()
