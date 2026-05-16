import json
from typing import Any

import httpx

from app.core.config import get_settings
from app.core.errors import AppError


OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"


def resolve_api_key(header_api_key: str | None = None) -> str:
    api_key = header_api_key or get_settings().openai_api_key
    if not api_key:
        raise AppError(
            "missing_openai_api_key",
            "Add your OpenAI API key in extension settings or backend .env.",
        )
    return api_key


class LLMClient:
    def __init__(self, api_key: str | None, model: str | None = None):
        self.api_key = api_key
        self.model = model or get_settings().openai_model

    async def json_completion(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        api_key = resolve_api_key(self.api_key)
        payload = {
            "model": self.model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        content = await self._completion_content(api_key, payload)
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise AppError(
                "invalid_openai_json",
                "OpenAI returned a response that could not be parsed as JSON.",
                status_code=502,
            ) from exc

    async def text_completion(self, system_prompt: str, user_prompt: str) -> str:
        api_key = resolve_api_key(self.api_key)
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        return (await self._completion_content(api_key, payload)).strip()

    async def _completion_content(self, api_key: str, payload: dict[str, Any]) -> str:
        try:
            async with httpx.AsyncClient(timeout=45) as client:
                response = await client.post(
                    OPENAI_CHAT_URL,
                    headers={"Authorization": f"Bearer {api_key}"},
                    json=payload,
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise AppError(
                "openai_request_failed",
                "OpenAI rejected the request. Check your API key, model, and account access.",
                status_code=502,
            ) from exc
        except httpx.HTTPError as exc:
            raise AppError(
                "openai_unavailable",
                "Could not reach OpenAI. Check your network connection and try again.",
                status_code=502,
            ) from exc

        try:
            return response.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AppError(
                "invalid_openai_response",
                "OpenAI returned an unexpected response format.",
                status_code=502,
            ) from exc
