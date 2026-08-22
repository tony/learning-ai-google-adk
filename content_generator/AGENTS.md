# content_generator

Library that analyzes a target project and produces a validated lesson file
for it. No ADK dependency — every function here is testable without the
`google-adk` package, and `content_generator_agent` wraps these as
`FunctionTool`-compatible callables.

| Module | What it does |
| ------ | ------------- |
| `models.py` | Pydantic models and enums: `TargetProject`, `PedagogyStyle`, `LessonPlan`, `ValidationResult`, etc. |
| `project_registry.py` | Maps `TargetProject` to a filesystem path; enforces path-traversal safety |
| `analyzers.py` | Reads a target project's `pyproject.toml`, `AGENTS.md`, and existing lessons |
| `templates.py` | Jinja2 scaffolding from `builtin_templates/` |
| `validators.py` | Subprocess runners for `ruff`, `mypy`, `pytest` against generated code |
| `tools.py` | `FunctionTool`-compatible wrappers around the above, called by `content_generator_agent` |
| `utils.py` | Code-fence stripping and text utilities |
| `domains.py` | Domain registry — see below |

## Path traversal safety

Every write goes through `project_registry.validate_path`, which resolves
symlinks and rejects a path outside `ALLOWED_ROOTS`. `ALLOWED_ROOTS` is
derived from `PROJECT_PATHS`, which is rooted at
`CONTENT_GENERATOR_STUDY_BASE` (default `~/study/python`). Generated content
never lands outside a registered target project.

## Domain registry

`domains.py` maps a domain name to a `DomainConfig`: which `TargetProject`
and `PedagogyStyle` it uses, its lesson directory, and its
`doctest_strategy` (`"deterministic"`, `"ellipsis"`, or `"skip"`).

| Domain | Pedagogy | Doctest strategy |
| ------ | -------- | ----------------- |
| `dsa` | `CONCEPT_FIRST` | deterministic |
| `asyncio` | `CONCEPT_FIRST` | ellipsis |
| `litestar` | `INTEGRATION_FIRST` | skip |
| `fastapi` | `APPLICATION_FIRST` | skip |

Look up a domain with `get_domain(name)`; list them with `list_domains()`.
