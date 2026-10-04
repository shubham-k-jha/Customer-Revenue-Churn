from __future__ import annotations

import json
import os
import re

import requests


class LLMProvider:
    def complete(self, messages: list[dict], **kwargs) -> str:
        raise NotImplementedError


class OpenAICompatibleProvider(LLMProvider):
    """Provider-neutral adapter for OpenAI-compatible chat endpoints."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout: int = 60,
    ):
        self.base_url = (
            base_url or os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        ).rstrip("/")
        self.api_key = api_key or os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("LLM_MODEL", "gpt-5.6-mini")
        self.timeout = timeout
        if timeout <= 0:
            raise ValueError("timeout must be positive")

    def complete(self, messages, **kwargs):
        if not self.api_key:
            raise RuntimeError("LLM_API_KEY/OPENAI_API_KEY is required for live agent calls")
        payload = {"model": self.model, "messages": messages, **kwargs}
        response = requests.post(
            self.base_url + "/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError("LLM response did not contain choices[0].message.content") from exc
        if not isinstance(content, str) or not content.strip():
            raise ValueError("LLM response content was empty")
        return content


def extract_json(text: str):
    """Extract one JSON object from plain or fenced model output."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("LLM response was empty")
    raw = text.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.I)
        raw = re.sub(r"\s*```$", "", raw)
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("LLM response did not contain a JSON object")
        try:
            obj = json.loads(raw[start : end + 1])
        except json.JSONDecodeError as exc:
            raise ValueError("LLM response contained invalid JSON") from exc
    if not isinstance(obj, dict):
        raise ValueError("LLM response JSON must be an object")
    return obj
