import os

from providers.base import RateLimitedProvider
from providers.openai_provider import OpenAIProvider
from providers.openrouter_provider import OpenRouterProvider
from providers.anthropic_provider import AnthropicProvider
from providers.gemini_provider import GeminiProvider


DEFAULT_REQUESTS_PER_MINUTE = 15.0


def _requests_per_minute() -> float:
    raw_value = os.getenv("LLM_REQUESTS_PER_MINUTE", str(DEFAULT_REQUESTS_PER_MINUTE))
    try:
        value = float(raw_value)
    except ValueError as exc:
        raise ValueError("LLM_REQUESTS_PER_MINUTE must be a number") from exc
    if value < 0:
        raise ValueError("LLM_REQUESTS_PER_MINUTE must be zero or greater")
    return value


def make_provider(name: str) -> RateLimitedProvider:
    if name == "openai":
        provider = OpenAIProvider()
    elif name == "openrouter":
        provider = OpenRouterProvider()
    elif name == "anthropic":
        provider = AnthropicProvider()
    elif name == "gemini":
        provider = GeminiProvider()
    else:
        raise ValueError(f"Unknown provider: {name}")
    return RateLimitedProvider(provider, requests_per_minute=_requests_per_minute())
