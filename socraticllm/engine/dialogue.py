"""The Socratic dialogue loop.

Wires `LLMClient` (the API call) and the guardrail (`check` — the hard
constraint from Core Design Decision #1) into a turn-taking loop, with a
system prompt that encodes the Pedagogy section of CLAUDE.md. There is no
Problem/session model yet (see Open Design Questions), so this engine takes
an optional plain-string `curriculum_context` hook rather than a `ConceptGraph`
dependency — a caller can inject concept-specific framing once that model
exists, without this module needing to know about `ConceptGraph` itself.
"""

from __future__ import annotations

from dataclasses import dataclass

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
