
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
	openrouter_api_key: str
	openrouter_base_url: str = "https://openrouter.ai/api/v1"
	openrouter_model: str = "mistralai/mistral-7b-instruct"

	llm_temperature: float = 0.0
	llm_top_p: float = 1.0
	llm_max_tokens: int = 350
	llm_timeout_seconds: float = 30.0

	app_env: str = "dev"
	log_level: str = "INFO"


def get_settings() -> Settings:
	api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
	if not api_key:
		raise RuntimeError(
			"OPENROUTER_API_KEY is not set. Set it in the environment or a .env file."
		)

	return Settings(
		openrouter_api_key=api_key,
		openrouter_base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").strip()
		or "https://openrouter.ai/api/v1",
		openrouter_model=os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct").strip()
		or "mistralai/mistral-7b-instruct",
		app_env=os.getenv("APP_ENV", "dev").strip() or "dev",
		log_level=os.getenv("LOG_LEVEL", "INFO").strip() or "INFO",
	)
