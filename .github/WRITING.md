# Writing

How this project writes prose, for humans and agents alike. It governs
`README.md`, commit messages, agent instructions, docstrings, and source
comments — every surface a reader (human or model) reaches.

For environment setup and the gates, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Voice

A docstring says what a caller may rely on; prose says what happens. Both are
present tense, lead with the thing being described, and stop. Why it was built
that way belongs in the commit message, which is timestamped and attached to
the diff.

The most useful editing operation is deleting the introductory sentence.

Lead with verbs and name concrete things. Put identifiers in backticks. Prefer
short declarative sentences, one operational fact each. Do not explain Python
to Python developers; do explain this project's semantics.

Type annotations describe shape. Documentation describes meaning. A sentence
that restates a signature has said nothing.

Use MUST, SHOULD, and MAY only where the normative sense is meant. Say what
actually happens rather than that something is "supported".

| Instead of                       | Prefer                             |
| --------------------------------- | ----------------------------------- |
| "We added…"                      | "`analyze_target_project` now…"    |
| "New and improved"               | "`get_domain` now…"                |
| "powerful", "seamless"           | state the capability               |
| "easily", "simply", "just"       | omit                               |
| "simple", "obvious", "intuitive" | omit                               |
| "robust"                         | name the failure that is handled   |
| "comprehensive"                  | name what is covered               |
| "production-ready"               | state the guarantee                |
| "optimized", "blazingly fast"    | give the magnitude                 |
| "various fixes"                  | name the components                |
| "under the hood"                 | omit unless observable             |
| "please note that", "note that"  | state the fact                     |
| "leverage", "utilize"            | "use"                              |
| "delve into"                     | "read", or omit                    |
| "best practices"                 | name the practice                  |
| "in order to"                    | "to"                               |

## Who you are writing for

The default reader is fluent in Python and new to this project. They can read a
signature; they cannot guess this project's semantics. Serve them first.

- **Second person, present tense, active.** "You copy `.env.example` to
  `.env`", not "The environment file is copied".
- **Concept before API surface.** Say what an agent or function *is* and what
  it does for the reader before its signature.
- **Say when they can stop.** Lead with the default and the reassurance. Let a
  skimmer leave after one paragraph.
- **Name the trade-off.** If a call costs something — an LLM round trip, a
  filesystem write, a retry loop — say so, and say what it buys.

## README

A README is the shortest path from "what is this?" to competent use, not the
project's autobiography.

The first sentence is a contract: it says what this repository is, concretely
enough to tell it apart from the target projects it generates content for.

Get to a runnable command before anything the reader can skip.

State the minimum Python version in prose, not only in a badge.
`requires-python` in `pyproject.toml` is the authority; the README must agree
with it.

State defaults and negative guarantees explicitly — "does not write outside
the configured project roots" establishes a boundary faster than a paragraph
of description.

Headings stay conventional and stable, because people deep-link them.

## Secrets

`GOOGLE_API_KEY` never appears in prose, a documentation example, a docstring,
or a committed config file. `.env` is git-ignored; only `.env.example`, which
carries a placeholder value, is committed. A quickstart snippet shows the
`cp .env.example .env` step and stops there — it never shows a real key.

## Documented examples that run

This repository's `pytest` configuration does not collect doctests.
`[tool.pytest.ini_options]` in `pyproject.toml` sets `testpaths = ["tests"]`
with no `--doctest-modules` or `--doctest-glob` in `addopts`, and
`tests/conftest.py` defines no `doctest_namespace` fixture. No `>>> ` prompt
anywhere in this repository — a docstring, this file, or anywhere else — is
executed by the test suite, and there is no `README.md` in `testpaths` to
change that.

A `>>> ` prompt here is prose, not a test. Do not add one implying it is
verified; write an illustrative snippet as a plain ```` ```python ```` fence
instead.

The `>>> ` blocks that do exist in this repository live in
`content_generator/builtin_templates/*.py.tmpl`. Those are Jinja2 templates
rendered into lesson files for the target learning projects (`learning-dsa`,
`learning-asyncio`, `learning-litestar`, `learning-fastapi`); the rendered
doctests are checked by the target project's own pytest configuration, through
the `run_pytest_doctest` validator tool — not by this repository's test suite.
Keep that distinction when editing a template: the prompts are real doctests,
but only once rendered into someone else's project.

## Agent instructions

The instruction strings in `content_generator_agent/prompts.py` and the
`instruction=` argument in `google_search_agent/agent.py` are prose read by
the model, not by a human, but they follow the same voice: imperative,
concrete, present tense. Keep the existing shape:

- Numbered steps naming the exact tool to call, in call order.
- A `{placeholder}` for each piece of upstream state the agent consumes via
  `output_key`, named after that key.
- A closing paragraph stating what the agent's final response must contain,
  so the next stage in the pipeline can consume it.

## Docstrings

The prime directive: never restate the type. The annotation is the source of
truth; the docstring carries what the annotation cannot.

This is documentation debt wearing a docstring:

```python
def get_id(pane: Pane) -> str:
    """Get the pane's identifier.

    Parameters
    ----------
    pane : Pane
        The pane.

    Returns
    -------
    str
        The identifier.
    """
```

Document instead the dimensions the type system cannot encode: mutation,
ownership, ordering, timing, failure, idempotence, concurrency, units and
ranges, boundary behaviour, platform differences, and the security boundary —
what is executed versus what is only read.

The first sentence stands alone; tooling truncates there. PEP 257 applies:
triple double quotes, an imperative one-line summary ending in a period, a
blank line before any extended description.

This repository's docstring dialect is NumPy, enforced by
`[tool.ruff.lint.pydocstyle]` rather than relitigated in review:

```python
def get_project_path(project: TargetProject) -> pathlib.Path:
    """Return the filesystem path for a target project.

    Parameters
    ----------
    project : TargetProject
        The project to look up.

    Returns
    -------
    pathlib.Path
        Absolute path to the project root.

    Raises
    ------
    KeyError
        If the project is not registered.
    """
```

## Source comments

A comment ships only if it passes all three gates. Fail any: delete or
rewrite. Borderline: delete — borderline means the information is
reconstructible, which is what makes deletion cheap.

**Loss.** Three years from now, would losing this cost a maintainer real time
rediscovering intent, an invariant, a constraint, or a failure mode the code
and tests do not already make obvious?

**Elite.** Would SQLite, Redis, the Go standard library, or CPython write this
comment, at this length? Those projects state the constraint and stop. They do
not argue with an imagined objector.

**Upkeep.** Will it stay true without maintenance? A comment that hand-syncs a
value the code owns — a count, an offset, a line reference, a duplicated
constant — is false the first time that value moves.

### Ceiling

One or two lines. A comment reaching four is either carrying several facts, in
which case split it, or arguing, in which case cut it to the fact.

Rationale, alternatives weighed, and the story of how the code got here belong
in the commit message: timestamped, attached to the exact diff, and free to
maintain.

### Keep

- Why over how: upstream quirks, protocol and compatibility constraints,
  performance tradeoffs still part of the contract.
- Invariants, preconditions, ordering, lifetime, and concurrency requirements
  that types and tests cannot express.
- Code that looks wrong but is not, so a later cleanup does not reintroduce
  the bug.
- A high-level sketch of an algorithm whose local operations do not reveal
  the whole.

### Delete

- Narration of the next lines; code translated into English.
- Restated names, types, defaults, or control flow.
- Values duplicated from the code and hand-synced.
- Justification, hedging, or apology for a choice.
- Speculation about future requirements.
- History version control already holds, including commented-out code.
- Ticket and issue numbers.
- Transient observations — "currently", "for now", "the latest release" —
  that go stale with no nearby edit.

### The upkeep gate in practice

It reaches values that track our own code. It does not reach frozen external
facts.

Bad (Delete):

```python
# There are 321 tests to complete for servers.
```

Good (Keep):

```python
# ADK discovers an agent by importing the package and finding
# `root_agent`; the name is not configurable per package.
```

### Documentation exception

Minimal usage examples, and parameter, return, and raises entries on public
API, are exempt from the loss gate — they serve the caller, not the
maintainer. They are exempt from nothing else. Ceiling: a good man page entry.

## Terminology and capitalization

Pick the domain noun and keep it. This project calls a generation target a
"target project", not a "learning repo" in one paragraph and a "destination"
in the next. Python and PyPI keep their own capitalisation.

Do not write counts into prose — how many tests exist, how many domains are
registered. They go stale silently and no reader needs them.

## Durable source links

Link to a pinned revision, never to trunk. A `blob/master/…` link rots
silently — the file moves, lines shift, and the anchor lands on unrelated
code while still resolving.

- Prefer a release tag. This repository has none yet; until it does, use a
  7-character commit SHA reachable from `master` instead.
- Never link to a pull-request-head SHA — it can be rebased or garbage
  collected.
- A line anchor (`#L120-L145`) is only safe on a pinned ref.

## Markdown

Prose wraps at 80 columns. Table rows, badge lines, and long links are
exempt, because breaking them harms rendering.

GitHub alert blocks — `> [!NOTE]`, `> [!WARNING]` — render as literal text
outside GitHub, so reserve them for at most one load-bearing warning per
document.

Do not use a local absolute path or an email address in anything published.

## Code blocks

Code blocks are paste-and-run units: pasting one block runs exactly one
intended action.

- **One command per block.** Multiple steps may share a block only when
  explicitly chained with `&&`, `;`, or `\` continuations, or piped with `|`
  — the chain is then one logical command.
- **Explanations go in prose above the block**, never as `#` comments inside
  it.
- **Shell commands use the `console` tag with a `$ ` prefix.**
- **Split long commands with `\`** — one flag or flag+value pair per indented
  continuation line, positional arguments last.

Good:

```console
$ curl -s http://localhost:8000/list-apps | jq .
```

Bad:

```console
# List the agents the dev server has discovered
$ curl -s http://localhost:8000/list-apps | jq .
```

## Commits

```
Scope(type[detail]): Concise description

why: Explanation of necessity or impact.

what:
- Specific technical changes made
- Focused on a single topic
```

Keep the subject to 50 characters or fewer, excluding any trailing `(#NN)`
pull request reference, and wrap body lines at 72. Separate the `why:` and
`what:` blocks with a blank line.

Routine maintenance commits drop the colon and take a capitalised
description, which is what distinguishes them at a glance in
`git log --oneline`:

```
py(deps[dev]) Bump dev packages
ai(rules[AGENTS]) Judge comments by three gates
```

Everything that changes behaviour keeps the colon.

Common types: **feat**, **fix**, **refactor**, **docs**, **chore**, **test**,
**style**, **py(deps)**, **py(deps[dev])**, **ai(rules[AGENTS])**.

Example:

```
Agent(feat[content_generator]): Add a fifth domain

why: Support generating lessons for a Rust learning project.

what:
- Add TargetProject.RUST and its DomainConfig
- Register the domain's pedagogy and doctest strategy
```

For a multi-line message, use a heredoc so the formatting survives:

```console
$ git commit -m "$(cat <<'EOF'
Scope(feat[detail]): Concise description

why: Explanation of the change.

what:
- First change
- Second change
EOF
)"
```

## Slop prevention

Treat AI slop as review-hostile noise, not as proof that text or code is
wrong. The goal is to maximise information density.

- **AI signatures.** No "Generated by", no conversational filler, no
  unexplained emoji, no tool metadata.
- **Brittle references.** No hard-coded line numbers, fragile file counts,
  dated "as of" claims, bare SHAs, or local absolute paths — unless they are
  strict evidentiary artefacts, such as a benchmark log or a stack trace.
- **Evidence is immune.** The brittle-references rule above does not apply
  to exact counts, dates, and SHAs that serve as evidence — benchmark
  results, release notes, stack traces, lockfiles. Preserve those exactly.
- **Diff narration.** Do not restate what moved, was renamed, or was removed
  in anything the reader holds alongside the diff: code, docstrings, README,
  or a pull request description.
- **Branch-internal narrative.** Do not mention intermediate states,
  abandoned approaches, or "no longer" behaviour unless a change actually
  shipped in a release users experienced. Apply the Published-Release Test:
  did users of the most recently published release ever experience this old
  name, old behaviour, or bug? If not, it belongs in the commit message, not
  the artefact.
- **Low-value scaffolding.** No ownerless TODOs, unused future-proofing,
  debug artefacts, or defensive wrappers around failure modes nothing can
  reach.
- **Prose inflation.** The diction table under [Voice](#voice) governs;
  replace an inflated word with a concrete description of behaviour,
  constraints, or trade-offs.
- **Coded labels.** Write rules and findings as plain imperatives. No `[R1]`,
  `Option B`, or any index a reader has to decode.

Preserve the "why". Never delete a comment documenting an invariant, a
protocol constraint, a platform quirk, or an upstream workaround — those are
the facts [Source comments](#source-comments) keeps, and every other comment
is judged by it.
