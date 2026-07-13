"""Guardrail: the hard constraint from Core Design Decision #1 in CLAUDE.md —
the system never gives the answer, only the next question. Every candidate
dialogue turn passes through here before it reaches the student.

This first pass is structural, not semantic: it flags phrasing shaped like a
delivered answer (declarative solution statements, "Answer:" labels,
multi-step walkthroughs) regardless of curriculum content. There is no
Problem/expected-answer model yet to check a response's content against a
specific correct answer — that would need a semantic, LLM-judge-based check,
which is a deliberate follow-up once that representation exists (see
CLAUDE.md's Open Design Questions), not part of this pass.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class GuardrailResult:
    passed: bool
    reason: str | None = None


_LEAK_PHRASE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bthe (?:correct |right )?answer is\b", re.IGNORECASE), "declares a final answer"),
    (re.compile(r"\bthe (?:correct |right )?(?:choice|solution) is\b", re.IGNORECASE), "declares a final answer"),
    (
        re.compile(r"\b(?:so|therefore|thus|hence),?\s+the answer\b", re.IGNORECASE),
        "concludes with a stated answer",
    ),
    (
        re.compile(r"\bin (?:conclusion|summary),?\s+the answer\b", re.IGNORECASE),
        "concludes with a stated answer",
    ),
    (re.compile(r"\byou should conclude that\b", re.IGNORECASE), "tells the student what to conclude"),
    (re.compile(r"\b(?:final )?answer\s*:\s*\S", re.IGNORECASE), "labels an answer directly"),
]

_STEP_MARKER_PATTERN = re.compile(r"(?:^|\n)\s*(?:step\s*\d+[:.]?|\d+[.)])\s", re.IGNORECASE)
_MIN_STEP_MARKERS_TO_FLAG = 2


def check(response: str) -> GuardrailResult:
    """Check a candidate dialogue turn for the shape of a delivered answer.

    Structural only — see the module docstring. A `passed=True` result means
    no known leak pattern matched, not that the response is pedagogically
    sound; that judgment still belongs to the dialogue engine and, ultimately,
    the reviewer of the prompts that produced it.
    """
    for pattern, reason in _LEAK_PHRASE_PATTERNS:
        if pattern.search(response):
            return GuardrailResult(passed=False, reason=reason)

    if len(_STEP_MARKER_PATTERN.findall(response)) >= _MIN_STEP_MARKERS_TO_FLAG:
        return GuardrailResult(passed=False, reason="reads as a multi-step solution walkthrough")

    return GuardrailResult(passed=True)
