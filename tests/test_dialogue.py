import pytest

from socraticllm.engine.dialogue import FALLBACK_RESPONSE, MAX_GUARDRAIL_RETRIES, DialogueEngine
from socraticllm.engine.guardrail import check


class ScriptedLLMClient:
    def __init__(self, responses: list[str]) -> None:
        self._responses = iter(responses)
        self.calls: list[dict] = []

    def complete(self, system, messages, max_tokens=2048):
        self.calls.append({"system": system, "messages": messages, "max_tokens": max_tokens})
        return next(self._responses)


class FlakyLLMClient:
    """Raises on any queued `None`, otherwise returns the queued string."""

    def __init__(self, responses: list[str | None]) -> None:
        self._responses = iter(responses)

    def complete(self, system, messages, max_tokens=2048):
        response = next(self._responses)
        if response is None:
            raise RuntimeError("simulated API failure")
        return response


def test_passing_response_is_used_directly():
    llm = ScriptedLLMClient(["What do you think happens if x doubles?"])
    engine = DialogueEngine(llm_client=llm)

    turn = engine.ask("I don't understand why y grows.")

    assert turn.response == "What do you think happens if x doubles?"
    assert turn.guardrail_retries == 0
    assert engine.history[-1] == {"role": "assistant", "content": turn.response}
    assert len(llm.calls) == 1


def test_retries_on_guardrail_rejection_then_succeeds():
    llm = ScriptedLLMClient(
        [
            "The answer is 4.",
            "What would you get if you divided both sides by 2?",
        ]
    )
    engine = DialogueEngine(llm_client=llm)

    turn = engine.ask("What's x?")

    assert turn.response == "What would you get if you divided both sides by 2?"
    assert turn.guardrail_retries == 1
    assert len(llm.calls) == 2
    # the rejected candidate must never enter permanent history
    assert all(m["content"] != "The answer is 4." for m in engine.history)


def test_falls_back_after_exhausting_retries():
    llm = ScriptedLLMClient(["The answer is 4."] * (MAX_GUARDRAIL_RETRIES + 1))
    engine = DialogueEngine(llm_client=llm)

    turn = engine.ask("What's x?")

    assert turn.response == FALLBACK_RESPONSE
    assert turn.guardrail_retries == MAX_GUARDRAIL_RETRIES
    assert engine.history[-1] == {"role": "assistant", "content": FALLBACK_RESPONSE}
    assert len(llm.calls) == MAX_GUARDRAIL_RETRIES + 1


def test_history_accumulates_across_turns():
    llm = ScriptedLLMClient(["First question?", "Second question?"])
    engine = DialogueEngine(llm_client=llm)

    engine.ask("Hi")
    engine.ask("Ok I think x=2")

    assert [m["role"] for m in engine.history] == ["user", "assistant", "user", "assistant"]


def test_curriculum_context_is_folded_into_system_prompt():
    llm = ScriptedLLMClient(["What's the first step you'd try?"])
    engine = DialogueEngine(llm_client=llm, curriculum_context="Linear equations: isolating a variable.")

    engine.ask("How do I solve for x?")

    assert "Linear equations: isolating a variable." in llm.calls[0]["system"]


def test_history_untouched_when_llm_call_raises():
    engine = DialogueEngine(llm_client=FlakyLLMClient([None]))

    with pytest.raises(RuntimeError, match="simulated API failure"):
        engine.ask("What's x?")

    assert engine.history == []


def test_can_ask_again_after_a_failed_turn():
    # A prior failed ask() must not leave a dangling user turn that would
    # break role alternation on the next call.
    llm = FlakyLLMClient([None, "What have you tried so far?"])
    engine = DialogueEngine(llm_client=llm)

    with pytest.raises(RuntimeError):
        engine.ask("What's x?")
    turn = engine.ask("What's x?")

    assert turn.response == "What have you tried so far?"
    assert [m["role"] for m in engine.history] == ["user", "assistant"]


def test_fallback_response_itself_passes_the_guardrail():
    assert check(FALLBACK_RESPONSE).passed is True


def test_raises_if_fallback_response_would_fail_the_guardrail(monkeypatch):
    monkeypatch.setattr("socraticllm.engine.dialogue.check", lambda _response: check("The answer is 4."))
    llm = ScriptedLLMClient(["The answer is 4."] * (MAX_GUARDRAIL_RETRIES + 1))
    engine = DialogueEngine(llm_client=llm)

    with pytest.raises(RuntimeError, match="FALLBACK_RESPONSE itself fails the guardrail"):
        engine.ask("What's x?")
