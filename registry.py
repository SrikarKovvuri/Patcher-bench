# patchpilot/registry.py

BENCHMARKS = {
    "bugsinpy": BugsInPyAdapter,
    # "swebench": SWEBenchAdapter,
}

MODELS = {
    "fake": FakeModelAdapter,
    "claude-sonnet": AnthropicAdapter,
    "gpt-4.1-mini": OpenAIAdapter,
}

POLICIES = {
    "fake": FakePolicy,
    "react": ReActPolicy,
    "verify_driven": VerifyDrivenReActPolicy,
}