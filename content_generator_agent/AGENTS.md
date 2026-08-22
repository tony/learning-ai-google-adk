# content_generator_agent

`agent.py` builds a `SequentialAgent` of four stages, each an ADK `Agent`
except the last:

1. **`template_analyzer`** — reads the target project's config, existing
   lessons, and template via `content_generator.tools`.
2. **`content_planner`** — turns the analysis into a lesson plan.
3. **`code_generator`** — writes the lesson file from the plan.
4. **`validation_loop`** (`LoopAgent`, `max_iterations=3`) — wraps a single
   **`validator`** sub-agent, which runs ruff/mypy/pytest against the
   generated file, repairs it, and calls `exit_loop` on success.

State flows forward only, through `output_key` on one stage matching a
`{placeholder}` in the next stage's instruction (see
`content_generator_agent/prompts.py`). Stages 2–4 set
`include_contents="none"`, so each starts from its instruction and the
placeholder state rather than the full conversation history.

`exit_loop` sets `actions.escalate=True`, which is what stops the
`LoopAgent` early; without a passing validation run it stops after
`max_iterations` regardless.

`google_search_agent/agent.py` is a single `Agent` with no pipeline —
`google_search` is its only tool.
