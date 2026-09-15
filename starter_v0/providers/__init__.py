import os

from providers.openai_provider import OpenAIProvider
from providers.openrouter_provider import OpenRouterProvider
from providers.anthropic_provider import AnthropicProvider
from providers.gemini_provider import GeminiProvider


def make_provider(name: str):
    if name == "colab":
        return OpenAIProvider(
            api_key_env=None,
            base_url=os.environ["LLM_BASE_URL"].rstrip("/"),
            default_model=os.getenv("LLM_MODEL", "qwen2.5-7b"),
            default_headers={"ngrok-skip-browser-warning": "true"},
            max_tokens=512,
        )
    if name == "openai":
        return OpenAIProvider()
    if name == "openrouter":
        return OpenRouterProvider()
    if name == "anthropic":
        return AnthropicProvider()
    if name == "gemini":
        return GeminiProvider()
    raise ValueError(f"Unknown provider: {name}")
