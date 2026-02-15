"""Utility functions for content processing.

Provides text manipulation helpers that clean LLM output before
validation or file writing.
"""

from __future__ import annotations

import re

# Compiled regexes for stripping markdown code fences from LLM output.
# Both must match for stripping to occur — prevents false positives from
# backticks inside docstrings or inline code.
_OPENING_FENCE_RE = re.compile(r"^`{3,}[^\S\n]*\w*[^\S\n]*\n", re.ASCII)
_CLOSING_FENCE_RE = re.compile(r"\n[^\S\n]*`{3,}[^\S\n]*$", re.ASCII)


def strip_code_fences(text: str) -> str:
    """Remove wrapping markdown code fences from LLM output.

    Only strips when both an opening fence (e.g. `` ```python ``) at the start
    and a closing fence (`` ``` ``) at the end are present.  Backticks embedded
    inside the code body (docstrings, inline reST) are left untouched.

    Parameters
    ----------
    text : str
        Raw LLM output, possibly wrapped in fences.

    Returns
    -------
    str
        Code with outer fences removed (if matched) and whitespace trimmed.
    """
    stripped = text.strip()
    if _OPENING_FENCE_RE.search(stripped) and _CLOSING_FENCE_RE.search(stripped):
        stripped = _OPENING_FENCE_RE.sub("", stripped, count=1)
        stripped = _CLOSING_FENCE_RE.sub("", stripped, count=1)
    return stripped.strip()
