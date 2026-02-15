# AGENTS.md

This file provides guidance to AI agents (including Claude Code, Cursor, and other LLM-powered tools) when working with code in this repository.

## CRITICAL REQUIREMENTS

### Test Success
- ALL tests MUST pass for code to be considered complete and working
- Never describe code as "working as expected" if there are ANY failing tests
- Changes that break existing tests must be fixed before considering implementation complete
- A successful implementation must pass linting, type checking, AND all existing tests

## Project Overview

google-adk-example is a project for [Google's Agent Development Kit (ADK)](https://github.com/google/adk-python). It includes two agents:

1. **`google_search_agent`** — Minimal agent using `google_search` tool
2. **`content_generator_agent`** — SequentialAgent pipeline that generates validated Python learning content for DSA, asyncio, Litestar, and FastAPI projects

Key features:
- ADK agents with Google Search grounding and content generation
- SequentialAgent pipeline with 4-stage orchestration
- Reusable `content_generator` library (no ADK dependency)
- Local editable ADK source via `[tool.uv.sources]`
- Follows conventions from the libtmux family of projects

## Development Environment

This project uses:
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) for dependency management
- [ruff](https://github.com/astral-sh/ruff) for linting and formatting
- [mypy](https://github.com/python/mypy) for type checking
- [pytest](https://docs.pytest.org/) for testing
- [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio) for async test support

## Common Commands

### Setting Up Environment

```bash
uv sync
```

Copy the environment template and add your API key:

```bash
cp .env.example .env
```

### Running the Agent

```bash
uv run adk web google_search_agent
```

### Running the Content Generator Agent

```bash
uv run adk web content_generator_agent
```

Example prompt: "Generate a DSA lesson about binary search for learning-dsa project."

### Running Tests

```bash
uv run pytest
```

Run a specific test file:

```bash
uv run pytest tests/test_agent.py
```

### Linting and Type Checking

Run ruff for linting:

```bash
uv run ruff check .
```

Format code with ruff:

```bash
uv run ruff format .
```

Run ruff linting with auto-fixes:

```bash
uv run ruff check . --fix --show-fixes
```

Run mypy for type checking:

```bash
uv run mypy google_search_agent content_generator content_generator_agent
```

### Development Workflow

Follow this workflow for code changes:

1. **Format First**: `uv run ruff format .`
2. **Run Tests**: `uv run pytest`
3. **Run Linting**: `uv run ruff check . --fix --show-fixes`
4. **Check Types**: `uv run mypy .`
5. **Verify Tests Again**: `uv run pytest`

## Code Architecture

```
google_search_agent/
  __init__.py          # Re-exports root_agent
  agent.py             # Agent definition (root_agent)

content_generator/                # Library (no ADK dependency, fully testable)
  __init__.py
  models.py            # Pydantic models (TargetProject, ProjectConfig, etc.)
  project_registry.py  # Project path mappings + path traversal safety
  analyzers.py         # Read target project config, content, progression
  templates.py         # Jinja2 boilerplate scaffolding
  validators.py        # Subprocess runners for ruff/mypy/pytest
  tools.py             # ADK FunctionTool-compatible wrapper functions

content_generator_agent/          # ADK agent package
  __init__.py          # Re-exports root_agent
  agent.py             # SequentialAgent with 4 sub-agents

tests/
  conftest.py
  test_models.py
  test_project_registry.py
  test_analyzers.py
  test_templates.py
  test_validators.py
  test_tools.py
  test_agent.py        # Structural tests (no API key needed)
  test_agent_e2e.py    # Conditional E2E (requires GOOGLE_API_KEY)
```

ADK discovers agents by importing the package and finding `root_agent`.

### Content Generator Pipeline

The content generator uses ADK's `SequentialAgent` to orchestrate a 4-stage pipeline:

1. **template_analyzer** — Reads target project config, templates, existing content
2. **content_planner** — Creates a detailed lesson plan from analysis
3. **code_generator** — Produces Python source matching the template
4. **validator** — Runs ruff/mypy/pytest with up to 3 repair cycles

State flows between agents via `output_key` → `{placeholder}` in instructions.
`include_contents='none'` on agents 2-4 prevents conversation history bloat.

## Testing Strategy

This project uses pytest for testing. Tests live in `tests/` with one test module per source module.

### Testing Guidelines

1. **Use functional tests only**: Write tests as standalone functions (`test_*`), not classes. Avoid `class TestFoo:` groupings — use descriptive function names and file organization instead. This applies to pytest tests, not doctests.

2. **Use existing fixtures over mocks**
   - Use fixtures from `conftest.py` instead of `monkeypatch` and `MagicMock` when available
   - Document in test docstrings why standard fixtures weren't used for exceptional cases

3. **Preferred pytest patterns**
   - Use `tmp_path` (pathlib.Path) fixture over Python's `tempfile`
   - Use `monkeypatch` fixture over `unittest.mock`

### Parametrized Tests

Use `typing.NamedTuple` with a `test_id` field for parametrized test fixtures:

```python
import typing as t

import pytest


class ConfigFixture(t.NamedTuple):
    test_id: str
    project_name: str
    expected_strict: bool


CONFIG_FIXTURES = [
    ConfigFixture(
        test_id="dsa_strict",
        project_name="learning-dsa",
        expected_strict=True,
    ),
    ConfigFixture(
        test_id="asyncio_strict",
        project_name="learning-asyncio",
        expected_strict=True,
    ),
]


@pytest.mark.parametrize(
    list(ConfigFixture._fields),
    CONFIG_FIXTURES,
    ids=[test.test_id for test in CONFIG_FIXTURES],
)
def test_project_config(
    test_id: str,
    project_name: str,
    expected_strict: bool,
) -> None:
    config = analyze_project_config(TargetProject(project_name))
    assert config.mypy_strict is expected_strict
```

## Coding Standards

### Imports

- **Use namespace imports for standard library modules**: `import enum` instead of `from enum import Enum`
  - **Exception**: `dataclasses` module may use `from dataclasses import dataclass, field` for cleaner decorator syntax
  - This rule applies to Python standard library only; third-party packages may use `from X import Y`
- **For typing**, use `import typing as t` and access via namespace: `t.NamedTuple`, etc.
- **Use `from __future__ import annotations`** at the top of all Python files

### Docstrings

Follow NumPy docstring style for all functions and methods:

```python
"""Short description of the function or class.

Detailed description using reStructuredText format.

Parameters
----------
param1 : type
    Description of param1
param2 : type
    Description of param2

Returns
-------
type
    Description of return value
"""
```

### Git Commit Standards

Format commit messages as:
```
Scope(type[detail]): concise description

why: Explanation of necessity or impact.
what:
- Specific technical changes made
- Focused on a single topic
```

Common commit types:
- **feat**: New features or enhancements
- **fix**: Bug fixes
- **refactor**: Code restructuring without functional change
- **docs**: Documentation updates
- **chore**: Maintenance (dependencies, tooling, config)
- **test**: Test-related updates
- **style**: Code style and formatting
- **py(deps)**: Dependencies
- **py(deps[dev])**: Dev Dependencies
- **ai(rules[AGENTS])**: AI rule updates
- **ai(claude[rules])**: Claude Code rules (CLAUDE.md)

For multi-line commits, use heredoc to preserve formatting:
```bash
git commit -m "$(cat <<'EOF'
feat(Component[method]) add feature description

why: Explanation of the change.
what:
- First change
- Second change
EOF
)"
```

## Debugging Tips

When stuck in debugging loops:

1. **Pause and acknowledge the loop**
2. **Minimize to MVP**: Remove all debugging cruft and experimental code
3. **Document the issue** comprehensively for a fresh approach
4. **Format for portability** (using quadruple backticks)
