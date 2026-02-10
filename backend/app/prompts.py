
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .schemas import FrozenDecisionPayload, Role


@dataclass(frozen=True)
class Prompt:
	system: str
	user: str


_COMMON_RULES = (
	"You are CAPINTEL, a controlled natural-language explanation renderer.\n"
	"You MUST only use the fields provided in the JSON payload.\n"
	"Do NOT infer any new features, do NOT access external data, do NOT browse.\n"
	"Do NOT override or reinterpret the decision; treat it as final.\n"
	"Be deterministic and concise.\n"
)


def _format_payload(payload: FrozenDecisionPayload) -> str:
	# Keep formatting stable to reduce variance.
	return (
		"{\n"
		f'  "decision": "{payload.decision.value}",\n'
		f"  \"risk_score\": {payload.risk_score:.2f},\n"
		f"  \"thin_file_flag\": {str(payload.thin_file_flag).lower()},\n"
		f"  \"top_negative\": {payload.top_negative},\n"
		f"  \"top_positive\": {payload.top_positive}\n"
		"}"
	)


def build_prompt(role: Role, payload: FrozenDecisionPayload) -> Prompt:
	payload_text = _format_payload(payload)

	if role == Role.customer:
		system = (
			_COMMON_RULES
			+ "Audience: credit card applicant (customer).\n"
			+ "Tone: friendly, plain language, non-technical.\n"
			+ "Do NOT mention ML, models, SHAP, XGBoost, algorithms, or attributions.\n"
			+ "Do NOT reveal the numeric risk_score.\n"
			+ "Include 2-4 concrete improvement suggestions based ONLY on the listed factors.\n"
			+ "Avoid guarantees; do not promise approval.\n"
			+ "Output format: a short paragraph, then a bulleted list of suggestions.\n"
		)
		user = (
			"Using ONLY this payload, explain the decision and key reasons in customer-friendly terms.\n"
			"Payload:\n"
			f"{payload_text}\n"
		)
		return Prompt(system=system, user=user)

	if role == Role.support:
		system = (
			_COMMON_RULES
			+ "Audience: support agent assisting a customer.\n"
			+ "Tone: structured and concise.\n"
			+ "You MAY include the numeric risk_score.\n"
			+ "List key drivers exactly as given (no new ones).\n"
			+ "Provide talking points and 1-3 suggestions aligned to the factors.\n"
			+ "Output format:\n"
			+ "- Decision: ...\n- Risk score: ...\n- Key factors (negative): ...\n- Key factors (positive): ...\n- Talking points: ...\n- Suggestions: ...\n"
		)
		user = f"Generate a support-agent explanation from this payload:\n{payload_text}\n"
		return Prompt(system=system, user=user)

	if role == Role.compliance:
		system = (
			_COMMON_RULES
			+ "Audience: compliance auditor.\n"
			+ "Tone: formal, factual, audit-log ready.\n"
			+ "No speculative language. No recommendations beyond what follows from the payload.\n"
			+ "You MAY include the numeric risk_score.\n"
			+ "Output format: a short formal note with labeled fields.\n"
		)
		user = (
			"Create an audit-ready explanation using ONLY the payload fields.\n"
			"Payload:\n"
			f"{payload_text}\n"
		)
		return Prompt(system=system, user=user)

	raise ValueError(f"Unsupported role: {role}")
