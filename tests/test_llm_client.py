from socraticllm.engine import LLMClient


class FakeBlock:
    def __init__(self, type_: str, text: str = "") -> None:
        self.type = type_
        self.text = text


class FakeResponse:
    def __init__(self, content: list[FakeBlock]) -> None:
        self.content = content


class FakeMessages:
    def __init__(self, response: FakeResponse) -> None:
        self._response = response
        self.last_call: dict | None = None

    def create(self, **kwargs):
        self.last_call = kwargs
        return self._response


class FakeAnthropicClient:
    def __init__(self, response: FakeResponse) -> None:
        self.messages = FakeMessages(response)


def test_complete_extracts_text_block():
    response = FakeResponse([FakeBlock("thinking", ""), FakeBlock("text", "What comes before that step?")])
    fake_client = FakeAnthropicClient(response)
    llm = LLMClient(client=fake_client)

    result = llm.complete(system="Ask questions only.", messages=[{"role": "user", "content": "I'm stuck."}])

    assert result == "What comes before that step?"


def test_complete_passes_model_and_messages_through():
    fake_client = FakeAnthropicClient(FakeResponse([FakeBlock("text", "ok")]))
    llm = LLMClient(model="claude-opus-4-8", client=fake_client)

    llm.complete(system="sys", messages=[{"role": "user", "content": "hi"}], max_tokens=512)

    call = fake_client.messages.last_call
    assert call["model"] == "claude-opus-4-8"
    assert call["system"] == "sys"
    assert call["messages"] == [{"role": "user", "content": "hi"}]
    assert call["max_tokens"] == 512
