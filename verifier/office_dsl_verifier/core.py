from __future__ import annotations

import json
import os
from typing import Any, Literal

from pydantic import BaseModel, Field


Verdict = Literal["PASS", "FAIL", "NEEDS_REVIEW"]
RecommendedAction = Literal["ACCEPT", "REGENERATE", "ASK_USER", "BLOCK"]


class VerificationReport(BaseModel):
    verdict: Verdict
    score: float = Field(ge=0.0, le=1.0)
    intent_coverage: float = Field(ge=0.0, le=1.0)
    missing_requirements: list[str] = []
    unauthorized_actions: list[str] = []
    contradictions: list[str] = []
    policy_violations: list[str] = []
    requires_confirmation: list[str] = []
    explanation: str
    recommended_action: RecommendedAction


def verify(
    nl_command: str,
    dsl_text: str,
    plan_text: str,
    dsl_actions: list[str],
    plan_actions: list[str],
    trace: dict[str, Any] | None = None,
    mode: str | None = None,
) -> VerificationReport:
    selected = mode or os.getenv("OFFICE_DSL_VERIFIER_MODE", "mock")
    if selected == "mock":
        return _mock_verify(nl_command, dsl_text, plan_text, dsl_actions, plan_actions, trace)
    return _openrouter_verify(nl_command, dsl_text, plan_text, dsl_actions, plan_actions, trace)


def _mock_verify(
    nl_command: str,
    dsl_text: str,
    plan_text: str,
    dsl_actions: list[str],
    plan_actions: list[str],
    trace: dict[str, Any] | None,
) -> VerificationReport:
    text = f"{nl_command} {dsl_text} {plan_text}".lower()
    action_names = set(dsl_actions) | set(plan_actions)
    unauthorized: list[str] = []
    violations: list[str] = []
    requires_confirmation: list[str] = []

    if "nie wysy" in nl_command.lower() and "email.send" in action_names:
        unauthorized.append("email.send")
    if "email.send" in action_names:
        requires_confirmation.append("email.send")
        if "confirm" not in text:
            violations.append("email.send without confirmation marker")
    if "rm -rf" in text or "secret_key" in text:
        violations.append("unsafe command or secret access attempt")

    verdict: Verdict = "PASS"
    action: RecommendedAction = "ACCEPT"
    score = 0.95
    if unauthorized or violations:
        verdict = "FAIL"
        action = "BLOCK" if violations else "REGENERATE"
        score = 0.2
    return VerificationReport(
        verdict=verdict,
        score=score,
        intent_coverage=0.9 if verdict == "PASS" else 0.5,
        missing_requirements=[],
        unauthorized_actions=unauthorized,
        contradictions=[],
        policy_violations=violations,
        requires_confirmation=requires_confirmation,
        explanation="Mock verifier checks actual actions, confirmations, command attempts and secret reads.",
        recommended_action=action,
    )


def _openrouter_verify(
    nl_command: str,
    dsl_text: str,
    plan_text: str,
    dsl_actions: list[str],
    plan_actions: list[str],
    trace: dict[str, Any] | None,
) -> VerificationReport:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is required outside mock mode")
    try:
        import litellm
    except ImportError as exc:
        raise RuntimeError("Install verifier[openrouter] to use LiteLLM/OpenRouter") from exc
    response = litellm.completion(
        model=os.getenv("OPENROUTER_MODEL", "openrouter/openai/gpt-4.1-mini"),
        api_key=api_key,
        messages=[
            {"role": "system", "content": "Return only verifier JSON matching the requested schema."},
            {
                "role": "user",
                "content": json.dumps(
                    {"nl_command": nl_command, "dsl_actions": dsl_actions, "plan_actions": plan_actions, "trace": trace},
                    ensure_ascii=False,
                ),
            },
        ],
        response_format={"type": "json_object"},
    )
    content = response["choices"][0]["message"]["content"]
    return VerificationReport.model_validate_json(content)
