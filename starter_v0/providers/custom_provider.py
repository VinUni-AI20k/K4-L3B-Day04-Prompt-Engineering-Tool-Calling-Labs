from __future__ import annotations

import os

from providers.openai_provider import OpenAIProvider


class CustomProvider(OpenAIProvider):
    """Custom OpenAI-compatible provider for Qwen/Moonshot/DashScope/etc."""

    def __init__(
        self,
        *,
        api_key_env: str = "OPENAI_API_KEY",
        base_url_env: str = "OPENAI_BASE_URL",
        model_env: str = "MODEL",
        default_model: str = "qwen3.7-flash",
    ) -> None:
        base_url = os.getenv(base_url_env)
        if not base_url:
            base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # default DashScope URL
        model = os.getenv(model_env) or default_model
        super().__init__(
            api_key_env=api_key_env,
            base_url=base_url,
            default_model=model,
        )
