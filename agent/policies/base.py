# patchpilot/agent/policies/base.py

@dataclass
class AgentResult:
    messages: list[Message]      # full conversation
    turns: int
    cost_usd: float
    stop_reason: str             # "budget" | "done" | "max_iterations"

class AgentPolicy(Protocol):
    name: str  # "react", "verify_driven_react", later "plan_execute"

    def run(
        self,
        *,
        model: ModelAdapter,
        tools: ToolRegistry,
        workspace: Path,
        issue: str,
        initial_context: dict,     # before_test log, etc.
        limits: RunLimits,
        tracer: Tracer,
    ) -> AgentResult: ...