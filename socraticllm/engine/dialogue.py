"""The Socratic dialogue loop.

Wires `LLMClient` (the API call) and the guardrail (`check` — the hard
constraint from Core Design Decision #1) into a turn-taking loop, with a
system prompt that encodes the Pedagogy section of CLAUDE.md. There is no
Problem/session model yet (see Open Design Questions), so this engine takes
an optional plain-string `curriculum_context` hook rather than a `ConceptGraph`
dependency — a caller can inject concept-specific framing once that model
exists, without this module needing to know about `ConceptGraph` itself.

`SYSTEM_PROMPT` below is deliberately the generic, public version of the
Socratic-tutor instructions — safe to ship in this Apache-2.0 repo. The
specific questioning methodology (the "attention loop" and named question-move
patterns — see CLAUDE.md) is proprietary and is never checked in here: it's
loaded at runtime from a gitignored local path, or wherever
`SOCRATICLLM_METHODOLOGY_PATH` points, via `_load_methodology_overlay()`. If
that file doesn't exist (e.g. a clone of the public repo with no private
overlay), the engine still works — just with the generic prompt only.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .guardrail import check
from .llm_client import LLMClient

SYSTEM_PROMPT = """You are a Socratic tutor. Follow these rules without exception:

1. Never give the answer. Only ask the next question, offer a reframe, or give
   a partial answer that creates productive tension — never a full resolution
   the student hasn't earned. A complete, direct answer is only appropriate
   once the student has demonstrated they've done the conceptual work, or when
   they explicitly ask for the direct answer outright.
2. If the student accepts a claim too easily, resist gently: surface the
   assumption underneath it and ask whether it holds. Don't just move on.
3. When the student reaches a correct understanding on their own, say so
   explicitly — name what they figured out. The reward for productive
   struggle has to come from you, not just from the answer appearing.
"""

_METHODOLOGY_PATH_ENV_VAR = "SOCRATICLLM_METHODOLOGY_PATH"
_DEFAULT_METHODOLOGY_PATH = Path("private/methodology_prompt.txt")


def _load_methodology_overlay() -> str:
    """Read the proprietary methodology prompt overlay, if one exists locally.

    Returns "" (no overlay) when the file is absent — this must never raise,
    since the public repo has to work standalone with no private content.
    """
    path = Path(os.environ.get(_METHODOLOGY_PATH_ENV_VAR, _DEFAULT_METHODOLOGY_PATH))
    if not path.exists():
        return ""
    return path.read_text().strip()

MAX_GUARDRAIL_RETRIES = 2

FALLBACK_RESPONSE = (
    "Let's back up — what's the one thing you're already sure of here, and what does it rule out?"
)

_GUARDRAIL_RETRY_TEMPLATE = (
    "That response {reason}, which breaks the rule against giving the answer. "
    "Try again: ask a question instead."
)


@dataclass
class DialogueTurn:
    response: str
    guardrail_retries: int = 0


class DialogueEngine:
    def __init__(
        self,
        llm_client: LLMClient | None = None,
        curriculum_context: str = "",
    ) -> None:
        self._llm = llm_client or LLMClient()
        self._system_prompt = SYSTEM_PROMPT
        overlay = _load_methodology_overlay()
        if overlay:
            self._system_prompt += f"\n\n{overlay}"
        if curriculum_context:
            self._system_prompt += f"\n\nCurrent context: {curriculum_context}"
        self.history: list[dict[str, str]] = []

    def ask(self, student_message: str) -> DialogueTurn:
        # `self.history` is only mutated once a final outcome exists (below) —
        # never before the LLM call — so an exception from `complete()` (a
        # network error, or NoTextResponseError) leaves history untouched
        # instead of a dangling user turn with no reply, which would break
        # role alternation on the next call.
        user_turn = {"role": "user", "content": student_message}
        messages = [*self.history, user_turn]
        retries = 0
        while True:
            candidate = self._llm.complete(system=self._system_prompt, messages=messages)
            result = check(candidate)
            if result.passed:
                self.history.append(user_turn)
                self.history.append({"role": "assistant", "content": candidate})
                return DialogueTurn(response=candidate, guardrail_retries=retries)

            if retries >= MAX_GUARDRAIL_RETRIES:
                # FALLBACK_RESPONSE still passes through the guardrail, same as
                # any other candidate — this is a hardcoded constant that should
                # always pass (see tests/test_dialogue.py), but a future edit to
                # it must not be able to silently bypass the hard constraint.
                if not check(FALLBACK_RESPONSE).passed:
                    raise RuntimeError("FALLBACK_RESPONSE itself fails the guardrail — fix the constant")
                self.history.append(user_turn)
                self.history.append({"role": "assistant", "content": FALLBACK_RESPONSE})
                return DialogueTurn(response=FALLBACK_RESPONSE, guardrail_retries=retries)

            retries += 1
            messages = [
                *messages,
                {"role": "assistant", "content": candidate},
                {"role": "user", "content": _GUARDRAIL_RETRY_TEMPLATE.format(reason=result.reason)},
            ]
