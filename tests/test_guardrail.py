import pytest

from socraticllm.engine.guardrail import check


@pytest.mark.parametrize(
    "response",
    [
        "The answer is 42.",
        "The correct answer is that mitochondria produce ATP.",
        "The solution is to multiply both sides by 3.",
        "So, the answer is that gravity causes tides.",
        "Therefore the answer is x = 4.",
        "In conclusion, the answer is supply exceeds demand.",
        "You should conclude that the derivative is zero here.",
        "Answer: 4",
        "Final answer: photosynthesis converts light into chemical energy.",
        "Step 1: Isolate x.\nStep 2: Divide both sides by 2.\nx equals 4.",
        "1. Add 3 to both sides.\n2. Divide by 2.\nThat gives you the value of x.",
    ],
)
def test_rejects_leaked_answers(response):
    result = check(response)
    assert result.passed is False
    assert result.reason


@pytest.mark.parametrize(
    "response",
    [
        "What happens if you substitute x = 2 into the equation?",
        "You've got it — that's exactly why constants have a derivative of zero.",
        "Let's slow down — what does 'isolate the variable' actually mean here?",
        "If doubling the input doubles the output, what does that suggest about how they're related?",
        "1. What's the first term in the sequence?",
        "Yes, that's the right instinct — but what happens at the boundary case?",
    ],
)
def test_passes_socratic_responses(response):
    result = check(response)
    assert result.passed is True
    assert result.reason is None
