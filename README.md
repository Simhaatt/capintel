

# CAPINTEL
**Context-Aware Explainability for ML-Based Loan Decisions**

---

## Repository Structure

capintel/
│
├── backend/
│ ├── app/
│ │ ├── main.py # FastAPI application entrypoint
│ │ ├── config.py # OpenRouter model & generation config
│ │ ├── schemas.py # API request/response schemas
│ │ ├── prompts.py # 🔒 Frozen system + role prompts
│ │ ├── llm_client.py # OpenRouter API client
│ │ └── explain_service.py # Core explanation logic
│ │
│ ├── requirements.txt
│ └── README.md
│
├── contracts/
│ └── explanation_contract.json # 🔒 Frozen ML → GenAI interface
│
├── demo/
│ ├── sample_inputs/ # Fixed demo payloads
│ │ ├── rejected_high_risk.json
│ │ ├── approved_borderline.json
│ │ └── approved_low_risk.json
│ │
│ └── screenshots/
│
├── docs/
│ ├── architecture.md
│ ├── prompt_design.md
│ └── demo_flow.md
│
├── .env.example
├── .gitignore
├── README.md
└── LICENSE


---

## Overview

CAPINTEL is a **GenAI-based explanation layer** designed to sit on top of
traditional machine learning loan decision systems.

The system follows a strict separation of responsibilities:
- **ML models** make approval/rejection decisions
- **SHAP** identifies key contributing factors
- **GenAI** explains those factors to different stakeholders

GenAI is **never used for decision-making**.

---

## Motivation

Loan decisions often lack:
- Clear customer communication
- Actionable support explanations
- Audit-ready compliance documentation

While explainability tools like SHAP exist, they are technical and not
audience-specific. CAPINTEL converts model outputs into **role-aware,
controlled explanations** without compromising compliance.

---

## System Architecture



[ ML Model (XGBoost) ]
↓
[ SHAP Feature Attributions ]
↓
[ Frozen Explanation Contract ]
↓
[ GenAI Explanation Engine ]
↓
Role-Based Natural Language Output


---

## Frozen Explanation Contract

The interface between ML/SHAP and GenAI is **explicitly frozen** to ensure
stability, safety, and auditability.

```json
{
  "decision": "Approved | Rejected",
  "risk_score": 0,
  "top_negative": ["High DTI", "High Utilization"],
  "top_positive": ["Stable Income"]
}

Contract Rules

GenAI consumes this structure exactly as provided

No additional features are inferred or invented

GenAI cannot override or reinterpret the decision

ML and SHAP implementations may evolve independently

Role-Based Explanations

CAPINTEL generates explanations for three distinct roles:

Customer

Friendly, non-technical language

No risk scores or model references

Includes improvement suggestions

Support Agent

Structured and concise

Includes risk score and key drivers

Actionable talking points

Compliance Auditor

Formal and factual tone

Complete decision context

Suitable for audit logs

All explanations originate from the same decision payload.

GenAI Design Constraints

LLM access via OpenRouter

Models: Mistral / LLaMA (7B–8B class)

Low temperature, capped token generation

No fine-tuning

No RAG

No LangChain or agent frameworks

GenAI is used strictly as a controlled explanation generator.

Tech Stack

Backend API: FastAPI

ML Model: XGBoost (external)

Explainability: SHAP (external)

GenAI: OpenRouter

UI: Lovable (API-driven, no frontend logic)

Demo

The demo uses fixed, reproducible decision payloads located in:

demo/sample_inputs/


The same payload can be explained from multiple perspectives by switching
roles, demonstrating explainability without decision variance.

Design Principles

Decision logic and explanation logic are isolated

Interfaces are frozen early

Compliance takes precedence over creativity

Minimal infrastructure, maximum clarity

License

MIT License



