from providers.openai_provider import OpenAIProvider
from providers.openrouter_provider import OpenRouterProvider
from providers.anthropic_provider import AnthropicProvider
from providers.gemini_provider import GeminiProvider
from providers.ollama_provider import OllamaProvider
from providers.local_provider import LocalProvider


def make_provider(name: str):
    if name == "openai":
        return OpenAIProvider()
    if name == "local":
        return LocalProvider()
    if name == "openrouter":
        return OpenRouterProvider()
    if name == "ollama":
        return OllamaProvider()
    if name == "anthropic":
        return AnthropicProvider()
    if name == "gemini":
        return GeminiProvider()
    raise ValueError(f"Unknown provider: {name}")
