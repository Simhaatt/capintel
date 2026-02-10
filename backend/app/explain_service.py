
from __future__ import annotations

from dataclasses import dataclass

from .llm_client import OpenRouterClient
from .prompts import build_prompt
from .schemas import ExplanationResponse, FrozenDecisionPayload, Role


_FORBIDDEN_TOKENS_CUSTOMER = (
	"shap",
	"xgboost",
	"model",
	"machine learning",
	"ml ",
	"algorithm",
	"feature attribution",
)


def _contains_forbidden_customer_terms(text: str) -> bool:
	lowered = text.lower()
	return any(token in lowered for token in _FORBIDDEN_TOKENS_CUSTOMER)


@dataclass(frozen=True)
class ExplainService:
	llm: OpenRouterClient

	async def explain(self, *, role: Role, payload: FrozenDecisionPayload) -> ExplanationResponse:
		# Contract is enforced by Pydantic model (extra fields forbidden),
		# plus runtime role routing here.
		prompt = build_prompt(role, payload)
		explanation_text = await self.llm.chat(system=prompt.system, user=prompt.user)

		if role == Role.customer and _contains_forbidden_customer_terms(explanation_text):
			# Fail closed rather than leaking prohibited content.
			raise ValueError("Generated customer explanation contained prohibited terms")

		key_drivers = [*payload.top_negative, *payload.top_positive]
		response = ExplanationResponse(
			role=role,
			decision=payload.decision,
			explanation=explanation_text,
			key_drivers=key_drivers,
		)

		if role in (Role.support, Role.compliance):
			response.risk_score = payload.risk_score

		if role == Role.customer:
			# Suggestions are included in the free-text output, but also provide a
			# lightweight structured list derived strictly from known factors.
			suggestions: list[str] = []
			for factor in payload.top_negative[:3]:
				if "util" in factor.lower():
					suggestions.append("Try to keep credit utilization lower over time.")
				elif "dti" in factor.lower() or "debt" in factor.lower():
					suggestions.append("Reduce outstanding debt where possible.")
				elif "history" in factor.lower() or "credit" in factor.lower():
					suggestions.append("Build credit history with on-time payments.")
			response.improvement_suggestions = suggestions[:4]

		return response
