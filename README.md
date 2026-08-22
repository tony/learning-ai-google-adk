# google-adk-example

A personal project for learning [Google's Agent Development Kit
(ADK)](https://github.com/google/adk-python): a minimal search-grounded
agent, and a `SequentialAgent` pipeline that writes and validates Python
lesson files for four other learning repositories.

Requires Python 3.13 or later and [uv](https://github.com/astral-sh/uv).

## Setup

```console
$ uv sync
```

`google-adk` resolves to a local editable checkout, declared in
`[tool.uv.sources]` in `pyproject.toml`; that checkout must exist on disk
before `uv sync` succeeds.

Copy the environment template and add a Gemini API key:

```console
$ cp .env.example .env
```

## Running an agent

Launch the ADK dev server, which serves every agent in this repository:

```console
$ just start
```

Or run a single agent directly:

```console
$ uv run adk web google_search_agent
```

## What is here

- **`google_search_agent`** — a minimal `Agent` with the `google_search`
  tool and nothing else.
- **`content_generator_agent`** — a four-stage `SequentialAgent` pipeline
  (analyze, plan, generate, validate-and-repair) that produces a lesson file
  for a target project: `learning-dsa`, `learning-asyncio`,
  `learning-litestar`, or `learning-fastapi`.
- **`content_generator`** — the library behind that pipeline. It has no ADK
  dependency, so it is importable and testable on its own. Every file it
  writes is resolved and checked against a registered project root first; it
  never writes outside one.

See [AGENTS.md](AGENTS.md) for the full project map, and the nested
`AGENTS.md` under `content_generator/` and `content_generator_agent/` for
how the pipeline and the domain registry work.

## Testing

```console
$ uv run pytest
```

Most tests are structural and need no API key. Tests that call the live
model are skipped unless `GOOGLE_API_KEY` is set.

See [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md) for the full set of
gates and the development workflow.

## License

MIT, as declared in `pyproject.toml`.
