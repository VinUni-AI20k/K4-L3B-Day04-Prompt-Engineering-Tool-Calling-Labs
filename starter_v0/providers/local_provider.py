from __future__ import annotations

import json
from typing import Any

from providers.base import ModelResponse, ToolCall


class LocalProvider:
    """Local Hugging Face Transformers provider."""

    def __init__(self) -> None:
        self.default_model = None

    def complete(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:

        if not model:
            raise RuntimeError("Local provider requires --model path")

        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
        except ImportError as exc:
            raise RuntimeError(
                "Install local model dependencies: "
                "pip install transformers torch"
            ) from exc

        tokenizer = AutoTokenizer.from_pretrained(model)
        model_obj = AutoModelForCausalLM.from_pretrained(
            model,
            torch_dtype="auto",
            device_map="auto",
        )

        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = tokenizer(
            prompt,
            return_tensors="pt",
        ).to(model_obj.device)

        with torch.no_grad():
            output = model_obj.generate(
                **inputs,
                max_new_tokens=512,
                temperature=temperature,
                do_sample=False,
            )

        generated = output[0][inputs["input_ids"].shape[1]:]

        text = tokenizer.decode(
            generated,
            skip_special_tokens=True,
        ).strip()

        return ModelResponse(
            text=text,
            tool_calls=[],
            raw=text,
        )