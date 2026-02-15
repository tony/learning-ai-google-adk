"""Jinja2 boilerplate scaffolding for generated content.

Provides templates that handle structural boilerplate (imports, guards,
docstring skeleton) while the LLM fills semantic content.
"""

from __future__ import annotations

import jinja2

#: Jinja2 environment for rendering templates.
_ENV = jinja2.Environment(
    autoescape=False,  # Generating Python source code, not HTML
    keep_trailing_newline=True,
    undefined=jinja2.StrictUndefined,
)

#: Template for lesson-based content (DSA, asyncio).
LESSON_TEMPLATE_STR = '''\
#!/usr/bin/env python
"""{{ module_docstring }}"""

from __future__ import annotations

{{ imports }}


{{ body }}


def main() -> None:
    """{{ main_docstring }}"""
    {{ main_body }}


if __name__ == "__main__":
    import doctest

    doctest.testmod()
    main()
'''

#: Template for asyncio lesson-based content.
ASYNCIO_LESSON_TEMPLATE_STR = '''\
#!/usr/bin/env python
"""{{ module_docstring }}"""

from __future__ import annotations

import asyncio
{{ imports }}


{{ body }}


async def main() -> None:
    """{{ main_docstring }}"""
    {{ main_body }}


if __name__ == "__main__":
    import doctest

    doctest.testmod()
    asyncio.run(main())
'''

#: Template for app-based content (Litestar, FastAPI).
APP_TEMPLATE_STR = '''\
"""{{ module_docstring }}"""

from __future__ import annotations

{{ imports }}


{{ body }}
'''

#: Template for app test files.
APP_TEST_TEMPLATE_STR = '''\
"""{{ module_docstring }}"""

from __future__ import annotations

{{ imports }}


{{ body }}
'''

_LESSON_TEMPLATE = _ENV.from_string(LESSON_TEMPLATE_STR)
_ASYNCIO_LESSON_TEMPLATE = _ENV.from_string(ASYNCIO_LESSON_TEMPLATE_STR)
_APP_TEMPLATE = _ENV.from_string(APP_TEMPLATE_STR)
_APP_TEST_TEMPLATE = _ENV.from_string(APP_TEST_TEMPLATE_STR)


def render_lesson_template(
    *,
    module_docstring: str,
    imports: str = "",
    body: str,
    main_docstring: str = "Run lesson demonstrations.",
    main_body: str = "pass",
) -> str:
    """Render a lesson-based boilerplate template.

    Parameters
    ----------
    module_docstring : str
        The module-level docstring content.
    imports : str
        Additional import statements beyond ``__future__``.
    body : str
        The main body of the module (function definitions, etc.).
    main_docstring : str
        Docstring for the ``main()`` function.
    main_body : str
        Body of the ``main()`` function.

    Returns
    -------
    str
        Rendered Python source code.
    """
    return _LESSON_TEMPLATE.render(
        module_docstring=module_docstring,
        imports=imports,
        body=body,
        main_docstring=main_docstring,
        main_body=main_body,
    )


def render_asyncio_lesson_template(
    *,
    module_docstring: str,
    imports: str = "",
    body: str,
    main_docstring: str = "Run async lesson demonstrations.",
    main_body: str = "pass",
) -> str:
    """Render an asyncio lesson-based boilerplate template.

    Parameters
    ----------
    module_docstring : str
        The module-level docstring content.
    imports : str
        Additional import statements beyond ``__future__`` and ``asyncio``.
    body : str
        The main body of the module (async function definitions, etc.).
    main_docstring : str
        Docstring for the ``main()`` coroutine.
    main_body : str
        Body of the ``main()`` coroutine.

    Returns
    -------
    str
        Rendered Python source code.
    """
    return _ASYNCIO_LESSON_TEMPLATE.render(
        module_docstring=module_docstring,
        imports=imports,
        body=body,
        main_docstring=main_docstring,
        main_body=main_body,
    )


def render_app_template(
    *,
    module_docstring: str,
    imports: str = "",
    body: str,
) -> str:
    """Render an app-based boilerplate template.

    Parameters
    ----------
    module_docstring : str
        The module-level docstring content.
    imports : str
        Import statements beyond ``__future__``.
    body : str
        The main body of the module (app definition, routes, etc.).

    Returns
    -------
    str
        Rendered Python source code.
    """
    return _APP_TEMPLATE.render(
        module_docstring=module_docstring,
        imports=imports,
        body=body,
    )


def render_app_test_template(
    *,
    module_docstring: str,
    imports: str = "",
    body: str,
) -> str:
    """Render an app test file boilerplate template.

    Parameters
    ----------
    module_docstring : str
        The module-level docstring content.
    imports : str
        Import statements beyond ``__future__``.
    body : str
        The test function definitions.

    Returns
    -------
    str
        Rendered Python source code.
    """
    return _APP_TEST_TEMPLATE.render(
        module_docstring=module_docstring,
        imports=imports,
        body=body,
    )
