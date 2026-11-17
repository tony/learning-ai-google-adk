# Contributing

Thanks for looking. This is a personal project for learning Google's Agent
Development Kit (ADK); a bug report with a reproduction, or a note on where
this documentation is wrong, is the most useful thing to open.

How this project writes prose — README, commit messages, agent instructions,
docstrings, and source comments — is set out separately in
[WRITING.md](WRITING.md). Read that before changing any of it. The map of
what is where is in [AGENTS.md](../AGENTS.md).

## Getting set up

```console
$ uv sync
```

`google-adk` resolves through `[tool.uv.sources]` in `pyproject.toml` to a
local editable checkout at `../../../study/ai-agents/google-adk-python`
(relative to the repository root). That checkout must exist before
`uv sync` succeeds.

Copy the environment template and add a real key:

```console
$ cp .env.example .env
```

`content_generator_agent` and `google_search_agent` need `GOOGLE_API_KEY` in
`.env` to make live calls; the structural tests do not.

## The gates

Format:

```console
$ uv run ruff format .
```

Lint:

```console
$ uv run ruff check . --fix --show-fixes
```

Type-check:

```console
$ uv run mypy google_search_agent content_generator content_generator_agent
```

Test:

```console
$ uv run pytest
```

There is no continuous integration in this repository; `just check` runs
format, test, lint, and type-check in that order and is the order of record.

All four gates must pass before a change counts as complete. A failing
test blocks completion, not review only — do not describe a change as
done, or as working as expected, while any gate is red.

This repository does not run documentation examples as tests — see
[Documented examples that run](WRITING.md#documented-examples-that-run).

Before claiming a test or a gate works, show it failing. A gate that has
never been red is an assumption.

## Tests

Tests live in `tests/`, one module per source module.

- **Functional tests only.** Write tests as standalone `test_*` functions,
  not `class TestFoo:` groupings.
- **Prefer fixtures over mocks.** Use `tests/conftest.py`'s
  `fake_tool_context` fixture — a minimal stand-in for ADK's `Context` —
  instead of `monkeypatch` or `MagicMock` where it covers the case.
- **Use `tmp_path` over `tempfile`, `monkeypatch` over `unittest.mock`.**
- **Async tests need no marker.** `asyncio_mode = "auto"` in
  `pyproject.toml` runs any `async def test_*` directly.
- **`test_agent.py` is structural**: it asserts pipeline shape (sub-agent
  order, `output_key`, `include_contents`, tool wiring) without an API key
  or a model call.
- **`test_agent_e2e.py` is conditional**: it calls the live model and is
  skipped without `GOOGLE_API_KEY`:

  ```python
  _skip_no_api_key = pytest.mark.skipif(
      not os.environ.get("GOOGLE_API_KEY"),
      reason="GOOGLE_API_KEY not set",
  )
  ```

Parametrize with a `typing.NamedTuple` carrying a `test_id` field, not bare
tuples:

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

## Debugging

When stuck in a debugging loop: pause and name the loop, strip the change
back to a minimal reproduction, write down what was tried, and share it in
quadruple backticks so any fenced code inside stays intact.

With the dev server running (`just start`, serving `http://localhost:8000`),
query it directly. The API accepts both camelCase and snake_case field names.

List available agents:

```console
$ curl -s http://localhost:8000/list-apps | jq .
```

List sessions for an agent:

```console
$ curl -s \
    http://localhost:8000/apps/content_generator_agent/users/user/sessions \
    | jq '.[].id'
```

Create a session:

```console
$ curl -s -X POST \
    http://localhost:8000/apps/content_generator_agent/users/user/sessions \
    -H 'Content-Type: application/json' \
    -d '{}' \
    | jq .id
```

Send a message and read the reply:

```console
$ curl -s -X POST http://localhost:8000/run \
    -H 'Content-Type: application/json' \
    -d '{
      "app_name": "content_generator_agent",
      "user_id": "user",
      "session_id": "SESSION_ID",
      "new_message": {"parts": [{"text": "Generate a DSA lesson about binary search"}]}
    }' \
    | jq '.[-1].content.parts[0].text'
```

Send a message over SSE, streaming the response:

```console
$ curl -s -N -X POST http://localhost:8000/run_sse \
    -H 'Content-Type: application/json' \
    -d '{
      "app_name": "content_generator_agent",
      "user_id": "user",
      "session_id": "SESSION_ID",
      "new_message": {"parts": [{"text": "Generate a DSA lesson about binary search"}]},
      "streaming": true
    }'
```

Inspect a session's event history:

```console
$ curl -s \
    http://localhost:8000/apps/content_generator_agent/users/user/sessions/SESSION_ID \
    | jq '.events[] | {author, id, parts: .content.parts[0].text[:120]}'
```

Check server health:

```console
$ curl -s http://localhost:8000/health | jq .
```

## Pull requests

One subject per pull request. Unrelated cleanup found along the way belongs
in its own commit, and usually in its own pull request.

Discuss a substantial change via an issue before making it.

Commit format is in [WRITING.md](WRITING.md#commits).

## Decorum

- Participants will be tolerant of opposing views.
- Participants must ensure that their language and actions are free of
  personal attacks and disparaging personal remarks.
- When interpreting the words and actions of others, participants should
  always assume good intentions.
- Behaviour which can be reasonably considered harassment will not be
  tolerated.

Based on
[Ruby's Community Conduct Guideline](https://www.ruby-lang.org/en/conduct/).

## Security

Please do not open a public issue for a vulnerability. This repository has no
dedicated security contact; open a private security advisory through
GitHub's repository Security tab instead.
