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
    dsl: dict[str, Any],
    plan: dict[str, Any],
    trace: dict[str, Any] | None = None,
    mode: str | None = None,
) -> VerificationReport:
    selected = mode or os.getenv("OFFICE_DSL_VERIFIER_MODE", "mock")
    if selected == "mock":
        return _mock_verify(nl_command, dsl, plan, trace)
    return _openrouter_verify(nl_command, dsl, plan, trace)


def _mock_verify(
    nl_command: str,
    dsl: dict[str, Any],
    plan: dict[str, Any],
    trace: dict[str, Any] | None,
) -> VerificationReport:
    text = json.dumps({"nl": nl_command, "dsl": dsl, "plan": plan, "trace": trace}, ensure_ascii=False).lower()
    action_names = _collect_action_names(dsl, plan)
    unauthorized: list[str] = []
    violations: list[str] = []
    requires_confirmation: list[str] = []

    if "nie wysy" in nl_command.lower() and "email.send" in action_names:
        unauthorized.append("email.send")
    if "email.send" in action_names:
        requires_confirmation.append("email.send")
        if '"confirm"' not in text:
            violations.append("email.send without confirmation marker")
    if "rm -rf" in text or "command" in text or "secret_key" in text:
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


def _collect_action_names(dsl: dict[str, Any], plan: dict[str, Any]) -> set[str]:
    actions: set[str] = set()
    for step in dsl.get("steps", []):
        if isinstance(step, dict) and isinstance(step.get("action"), str):
            actions.add(step["action"])
    for action in plan.get("actions", []):
        if isinstance(action, str):
            actions.add(action)
        elif isinstance(action, dict) and isinstance(action.get("action"), str):
            actions.add(action["action"])
    return actions


def _openrouter_verify(
    nl_command: str,
    dsl: dict[str, Any],
    plan: dict[str, Any],
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
                    {"nl_command": nl_command, "dsl": dsl, "plan": plan, "trace": trace},
                    ensure_ascii=False,
                ),
            },
        ],
        response_format={"type": "json_object"},
    )
    content = response["choices"][0]["message"]["content"]
    return VerificationReport.model_validate_json(content)
