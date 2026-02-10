
from __future__ import annotations

from dataclasses import dataclass

import httpx


class OpenRouterError(RuntimeError):
	pass


@dataclass(frozen=True)
class OpenRouterConfig:
	api_key: str
	base_url: str
	model: str
	temperature: float = 0.0
	top_p: float = 1.0
	max_tokens: int = 350
	timeout_seconds: float = 30.0
	app_title: str = "CAPINTEL"


class OpenRouterClient:
	"""Minimal OpenRouter Chat Completions client (OpenAI-compatible schema)."""

	def __init__(self, config: OpenRouterConfig) -> None:
		self._config = config
		self._http = httpx.AsyncClient(
			base_url=self._config.base_url.rstrip("/"),
			timeout=httpx.Timeout(self._config.timeout_seconds),
			headers={
				"Authorization": f"Bearer {self._config.api_key}",
				"Content-Type": "application/json",
				# Optional OpenRouter metadata headers
				"X-Title": self._config.app_title,
			},
		)

	async def aclose(self) -> None:
		await self._http.aclose()

	async def chat(self, *, system: str, user: str) -> str:
		payload = {
			"model": self._config.model,
			"temperature": self._config.temperature,
			"top_p": self._config.top_p,
			"max_tokens": self._config.max_tokens,
			"messages": [
				{"role": "system", "content": system},
				{"role": "user", "content": user},
			],
		}

		try:
			resp = await self._http.post("/chat/completions", json=payload)
		except httpx.HTTPError as exc:
			raise OpenRouterError(f"OpenRouter request failed: {exc}") from exc

		if resp.status_code >= 400:
			raise OpenRouterError(
				f"OpenRouter error {resp.status_code}: {resp.text[:500]}"
			)

		data = resp.json()
		try:
			content = data["choices"][0]["message"]["content"]
		except Exception as exc:  # noqa: BLE001
			raise OpenRouterError("Unexpected OpenRouter response schema") from exc

		if not isinstance(content, str) or not content.strip():
			raise OpenRouterError("Empty response from OpenRouter")

		return content.strip()
