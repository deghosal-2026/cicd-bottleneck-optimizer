import sys
from typing import Any

from openai import OpenAI
from anthropic import Anthropic


class LLMClient:
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.token_usage: dict[str, int] = {}
        self._local_client: OpenAI | None = None
        self._openai_client: OpenAI | None = None
        self._anthropic_client: Anthropic | None = None

    @property
    def local_client(self) -> OpenAI | None:
        if self._local_client is not None:
            return self._local_client

        local_cfg = self.config.get("llm", {}).get("local", {})
        if not local_cfg:
            return None

        try:
            self._local_client = OpenAI(
                base_url=local_cfg.get("base_url", "http://127.0.0.1:8000/v1"),
                api_key=local_cfg.get("api_key", "omlx-test"),
            )
            # Quick connectivity check
            self._local_client.models.list()
            return self._local_client
        except Exception:
            self._local_client = None
            return None

    @property
    def openai_client(self) -> OpenAI | None:
        if self._openai_client is not None:
            return self._openai_client

        api_key = self.config.get("llm", {}).get("cloud", {}).get("openai_api_key", "")
        if not api_key:
            return None

        self._openai_client = OpenAI(api_key=api_key)
        return self._openai_client

    @property
    def anthropic_client(self) -> Anthropic | None:
        if self._anthropic_client is not None:
            return self._anthropic_client

        api_key = self.config.get("llm", {}).get("cloud", {}).get("anthropic_api_key", "")
        if not api_key:
            return None

        self._anthropic_client = Anthropic(api_key=api_key)
        return self._anthropic_client

    def call_local(self, prompt: str, system: str | None = None, **kwargs) -> str:
        client = self.local_client
        if not client:
            raise ConnectionError("OMLX local LLM not available. Check if OMLX is running.")

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        model = (
            self.config.get("llm", {}).get("local", {}).get("model", "Qwen3.5-9B-MLX-4bit")
        )

        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs,
        )

        content = resp.choices[0].message.content or ""
        tokens = {
            "prompt": resp.usage.prompt_tokens if resp.usage else 0,
            "completion": resp.usage.completion_tokens if resp.usage else 0,
        }
        self._track_usage(f"omlx:{model}", tokens)
        return content

    def call_openai(self, prompt: str, system: str | None = None, **kwargs) -> str:
        client = self.openai_client
        if not client:
            raise ConnectionError("OpenAI client not configured. Set openai_api_key in config.")

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        model = self.config.get("llm", {}).get("cloud", {}).get("openai_model", "gpt-4o-mini")

        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs,
        )

        content = resp.choices[0].message.content or ""
        tokens = {
            "prompt": resp.usage.prompt_tokens if resp.usage else 0,
            "completion": resp.usage.completion_tokens if resp.usage else 0,
        }
        self._track_usage(f"openai:{model}", tokens)
        return content

    def call_anthropic(self, prompt: str, system: str | None = None, **kwargs) -> str:
        client = self.anthropic_client
        if not client:
            raise ConnectionError("Anthropic client not configured. Set anthropic_api_key in config.")

        model = (
            self.config.get("llm", {}).get("cloud", {}).get("anthropic_model", "claude-sonnet-4-20250514")
        )

        message = client.messages.create(
            model=model,
            max_tokens=kwargs.get("max_tokens", 4096),
            system=system or "",
            messages=[{"role": "user", "content": prompt}],
        )

        from anthropic.types import TextBlock

        content = ""
        for block in message.content:
            if isinstance(block, TextBlock):
                content += block.text
        tokens = {
            "prompt": message.usage.input_tokens if message.usage else 0,
            "completion": message.usage.output_tokens if message.usage else 0,
        }
        self._track_usage(f"anthropic:{model}", tokens)
        return content

    def _track_usage(self, model_key: str, tokens: dict[str, int]) -> None:
        if model_key not in self.token_usage:
            self.token_usage[model_key] = 0
        self.token_usage[model_key] += tokens.get("prompt", 0) + tokens.get("completion", 0)

    def get_token_summary(self) -> str:
        if not self.token_usage:
            return "No tokens used."
        parts = [f"{k}: {v} tokens" for k, v in self.token_usage.items()]
        return ", ".join(parts)
