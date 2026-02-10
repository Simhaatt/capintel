
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

try:
	from dotenv import load_dotenv

	load_dotenv()
except Exception:
	# python-dotenv is optional at runtime; environment variables can be set directly.
	pass

from .config import get_settings
from .explain_service import ExplainService
from .llm_client import OpenRouterClient, OpenRouterConfig, OpenRouterError
from .schemas import ExplanationResponse, FrozenDecisionPayload, Role


@asynccontextmanager
async def lifespan(app: FastAPI):
	settings = get_settings()
	llm = OpenRouterClient(
		OpenRouterConfig(
			api_key=settings.openrouter_api_key,
			base_url=settings.openrouter_base_url,
			model=settings.openrouter_model,
			temperature=settings.llm_temperature,
			top_p=settings.llm_top_p,
			max_tokens=settings.llm_max_tokens,
			timeout_seconds=settings.llm_timeout_seconds,
		)
	)
	app.state.explain_service = ExplainService(llm=llm)
	try:
		yield
	finally:
		await llm.aclose()


app = FastAPI(title="CAPINTEL", version="0.1.0", lifespan=lifespan)


@app.post("/explain/{role}", response_model=ExplanationResponse)
async def explain(role: Role, payload: FrozenDecisionPayload) -> ExplanationResponse:
	"""Generate a role-based explanation from a frozen decision payload."""
	service: ExplainService = app.state.explain_service
	try:
		return await service.explain(role=role, payload=payload)
	except OpenRouterError as exc:
		raise HTTPException(status_code=502, detail=str(exc)) from exc
	except ValueError as exc:
		raise HTTPException(status_code=400, detail=str(exc)) from exc
