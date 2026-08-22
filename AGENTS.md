# AGENTS.md

google-adk-example holds two Google Agent Development Kit (ADK) agents: a
minimal `google_search_agent`, and a `content_generator_agent` pipeline that
writes and validates Python lesson files for four other learning projects.

Follow the conventions already in the tree, and keep a change scoped to what
was asked for.

## What is here

| Path | What it is |
| ---- | ---------- |
| `google_search_agent/` | Minimal ADK agent, `google_search` tool only |
| `content_generator/` | Library (no ADK dependency): models, project registry, analyzers, templates, validators, tools — see nested `AGENTS.md` |
| `content_generator/builtin_templates/` | Fallback `.py.tmpl` lesson templates |
| `content_generator_agent/` | ADK `SequentialAgent` pipeline — see nested `AGENTS.md` |
| `tests/` | pytest suite, one module per source module |
| `justfile` | Task runner: `just start`, `just test`, `just check` |
| `.env.example` | Template for `GOOGLE_API_KEY` |

## Which policy applies

- Documentation, user-facing text, commit messages, agent instructions,
  docstrings, and source comments: [.github/WRITING.md](.github/WRITING.md)
- Environment, the gates, tests, debugging, and pull requests:
  [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md)

Each of those is the single home for its subject. Where a rule seems to be
stated twice, the file listed above is the one that governs.

## Change discipline

- Make the smallest coherent change that solves the verified problem; keep
  unrelated cleanup out of it.
- Reuse an existing file, helper, API, or test before adding a new one.
- Add a file only for a durable boundary — a distinct responsibility,
  independent reuse, or splitting an oversized module — not for a
  single-use helper or a one-line re-export.
- Add a test for every user-visible behaviour change.
- A passing gate is evidence only once it has been shown capable of
  failing.
- Keep this file lean: a multi-step procedure or a path-specific rule
  belongs in a nested `AGENTS.md`, not a growing root one.

- ADK discovers an agent by importing its package and finding `root_agent`;
  the attribute name is not configurable.
- Import standard-library modules by namespace (`import enum`, not
  `from enum import Enum`); `typing` is imported as `t`. Third-party imports
  may use `from X import Y`. Not enforced by ruff — a human convention.
  Exception: `dataclasses` may use `from dataclasses import dataclass,
  field` for cleaner decorator syntax.
- `content_generator` stays free of an ADK import by design, so it is
  importable and testable without the `google-adk` package.

## References

- [Google ADK](https://github.com/google/adk-python) — the framework these
  agents are built on.
