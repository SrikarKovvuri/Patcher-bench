

@dataclass
class ModelResponse:
    content: str | None
    tool_calls: list[ToolCall]
    usage: Usage  # tokens, cost

class ModelAdapter(Protocol):
    name: str

    def complete(self, messages: list[Message], tools: list[ToolSpec]) -> ModelResponse: ...