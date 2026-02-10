
from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class Decision(str, Enum):
	approved = "Approved"
	rejected = "Rejected"


class Role(str, Enum):
	customer = "customer"
	support = "support"
	compliance = "compliance"


class FrozenDecisionPayload(BaseModel):
	"""Frozen contract between ML/SHAP layers and the GenAI explanation layer.

	This model forbids extra fields so the API cannot accept any additional features.
	"""

	model_config = ConfigDict(extra="forbid")

	decision: Decision
	risk_score: float = Field(..., ge=0.0, le=1.0)
	thin_file_flag: bool
	top_negative: List[str] = Field(default_factory=list)
	top_positive: List[str] = Field(default_factory=list)


class ExplanationResponse(BaseModel):
	role: Role
	decision: Decision
	explanation: str

	# Echoed fields for internal roles (kept optional for customer output)
	risk_score: float | None = None
	key_drivers: list[str] = Field(default_factory=list)
	improvement_suggestions: list[str] = Field(default_factory=list)
