"""Thin wrapper around the Claude API call the dialogue engine runs on.

Core Design Decision #4 (CLAUDE.md): the dialogue engine calls an existing LLM
API rather than running a self-hosted model. This module is the one place
that API call happens — the dialogue loop and guardrail build on top of it,
they don't talk to the API directly.
"""

from __future__ import annotations

import anthropic

DEFAULT_MODEL = "claude-opus-4-8"
DEFAULT_MAX_TOKENS = 2048


class NoTextResponseError(Exception):
    """Raised when an API response has no text content block to return.

    Can happen if the model spends its whole token budget on thinking and
    never emits text — a plain StopIteration here would be a confusing crash.
    """


class LLMClient:
    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        client: anthropic.Anthropic | None = None,
    ) -> None:
        self.model = model
        self._client = client or anthropic.Anthropic()

    def complete(
        self,
        system: str,
        messages: list[dict[str, str]],
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> str:
        response = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            thinking={"type": "adaptive"},
            messages=messages,
        )
        for block in response.content:
            if block.type == "text":
                return block.text
        raise NoTextResponseError(
            f"no text block in response (stop_reason={response.stop_reason!r}); "
            f"block types present: {[block.type for block in response.content]}"
        )
