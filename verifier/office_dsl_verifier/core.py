from __future__ import annotations

import json
import os
from typing import Any, Literal

from pydantic import BaseModel, Field


Verdict = Literal["PASS", "FAIL", "NEEDS_REVIEW"]
RecommendedAction = Literal["ACCEPT", "REGENERATE", "ASK_USER", "BLOCK"]
SemanticFindingSeverity = Literal["info", "warning", "error"]


class VerificationReport(BaseModel):
    verdict: Verdict
    score: float = Field(ge=0.0, le=1.0)
    intent_coverage: float = Field(ge=0.0, le=1.0)
    missing_requirements: list[str] = Field(default_factory=list)
    unauthorized_actions: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    policy_violations: list[str] = Field(default_factory=list)
    requires_confirmation: list[str] = Field(default_factory=list)
    explanation: str
    recommended_action: RecommendedAction


class SemanticFinding(BaseModel):
    kind: str
    path: str
    message: str
    severity: SemanticFindingSeverity


class SemanticVerifierInput(BaseModel):
    original_nl: str | None = None
    approved_dsl: dict[str, Any] | None = None
    rendered_document: str | None = None
    codegen_verifier_input: dict[str, Any] | None = None
    testgen_verifier_input: dict[str, Any] | None = None


class SemanticVerificationReport(BaseModel):
    version: Literal["semantic-verifier.report.v1"] = "semantic-verifier.report.v1"
    verdict: Verdict
    score: float = Field(ge=0.0, le=1.0)
    findings: list[SemanticFinding] = Field(default_factory=list)
    missing_requirements: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    unauthorized_assumptions: list[str] = Field(default_factory=list)
    document_mismatches: list[str] = Field(default_factory=list)
    code_mismatches: list[str] = Field(default_factory=list)
    uncovered_acceptance_criteria: list[str] = Field(default_factory=list)
    recommended_action: RecommendedAction
    explanation: str


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


def verify_semantic(
    semantic_input: SemanticVerifierInput | dict[str, Any], mode: str | None = None
) -> SemanticVerificationReport:
    selected = mode or os.getenv("OFFICE_DSL_VERIFIER_MODE", "mock")
    parsed = (
        semantic_input
        if isinstance(semantic_input, SemanticVerifierInput)
        else SemanticVerifierInput.model_validate(semantic_input)
    )
    if selected == "mock":
        return _mock_semantic_verify(parsed)
    _validate_openrouter_runtime()
    raise RuntimeError("Semantic OpenRouter verification is not implemented in the validated default")


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


def _mock_semantic_verify(value: SemanticVerifierInput) -> SemanticVerificationReport:
    findings: list[SemanticFinding] = []
    missing_requirements: list[str] = []
    contradictions: list[str] = []
    unauthorized_assumptions: list[str] = []
    document_mismatches: list[str] = []
    code_mismatches: list[str] = []
    uncovered_acceptance_criteria: list[str] = []

    dsl = value.approved_dsl or {}
    for path, field in _iter_formal_fields(dsl):
        status = str(field.get("status", ""))
        required = bool(field.get("requiredForCompletion"))
        field_name = str(field.get("field", path))
        if required and status in {"MISSING", "INCOMPLETE"}:
            missing_requirements.append(field_name)
            findings.append(
                _finding("missing_requirement", field_name, f"{field_name} is {status}", "error")
            )
        if status == "CONFLICTING":
            contradictions.append(field_name)
            findings.append(
                _finding("contradiction", field_name, f"{field_name} is conflicting", "error")
            )
        if status == "ASSUMED" and not field.get("approvedBy"):
            unauthorized_assumptions.append(field_name)
            findings.append(
                _finding(
                    "unauthorized_assumption",
                    field_name,
                    f"{field_name} is assumed but not approved",
                    "warning",
                )
            )
        if value.original_nl:
            _check_source_quote_against_original_nl(value.original_nl, field_name, field, findings)

    for conflict in dsl.get("conflicts", []) if isinstance(dsl, dict) else []:
        conflict_path = str(conflict.get("field", conflict.get("id", "conflict")))
        contradictions.append(conflict_path)
        findings.append(_finding("contradiction", conflict_path, "DSL contains unresolved conflict", "error"))

    if value.rendered_document and dsl:
        for field_name, rendered_value in _rendered_document_required_values(dsl):
            if rendered_value and _normalize(rendered_value) not in _normalize(value.rendered_document):
                document_mismatches.append(field_name)
                findings.append(
                    _finding(
                        "document_mismatch",
                        field_name,
                        f"Rendered document is missing DSL value: {rendered_value}",
                        "error",
                    )
                )

    if value.codegen_verifier_input:
        generated_files = value.codegen_verifier_input.get("generatedFiles", [])
        if not generated_files:
            code_mismatches.append("generatedFiles")
            findings.append(
                _finding("code_mismatch", "generatedFiles", "Codegen verifier input has no generated files", "error")
            )
        for index, result in enumerate(value.codegen_verifier_input.get("testResults", [])):
            if not result.get("passed"):
                name = str(result.get("name", f"testResults[{index}]"))
                code_mismatches.append(name)
                findings.append(_finding("code_mismatch", name, "Generated code test failed", "error"))

    if value.testgen_verifier_input:
        uncovered_acceptance_criteria = [
            str(item) for item in value.testgen_verifier_input.get("uncoveredAcceptanceCriteriaIds", [])
        ]
        for item in uncovered_acceptance_criteria:
            findings.append(
                _finding(
                    "uncovered_acceptance_criteria",
                    item,
                    "Acceptance criterion has no generated test coverage",
                    "warning",
                )
            )

    error_count = sum(1 for finding in findings if finding.severity == "error")
    warning_count = sum(1 for finding in findings if finding.severity == "warning")
    if error_count:
        verdict: Verdict = "FAIL"
        recommended_action: RecommendedAction = "BLOCK"
        score = 0.2
    elif warning_count:
        verdict = "NEEDS_REVIEW"
        recommended_action = "ASK_USER"
        score = 0.65
    else:
        verdict = "PASS"
        recommended_action = "ACCEPT"
        score = 0.95

    return SemanticVerificationReport(
        verdict=verdict,
        score=score,
        findings=findings,
        missing_requirements=sorted(set(missing_requirements)),
        contradictions=sorted(set(contradictions)),
        unauthorized_assumptions=sorted(set(unauthorized_assumptions)),
        document_mismatches=sorted(set(document_mismatches)),
        code_mismatches=sorted(set(code_mismatches)),
        uncovered_acceptance_criteria=sorted(set(uncovered_acceptance_criteria)),
        recommended_action=recommended_action,
        explanation="Mock semantic verifier checks source quotes, required DSL field states, rendered document coverage, generated code test results, and test-generation coverage.",
    )


def _check_source_quote_against_original_nl(
    original_nl: str, field_name: str, field: dict[str, Any], findings: list[SemanticFinding]
) -> None:
    source = field.get("source")
    if not isinstance(source, dict):
        return
    quote = source.get("quote")
    if not quote:
        return
    if _normalize(str(quote)) not in _normalize(original_nl):
        findings.append(
            _finding(
                "source_mismatch",
                field_name,
                f"Source quote for {field_name} is absent from original NL",
                "error",
            )
        )


def _rendered_document_required_values(dsl: dict[str, Any]) -> list[tuple[str, str]]:
    wanted_prefixes = (
        "document.title",
        "parties.",
        "deliverables.",
        "obligations.",
        "acceptanceCriteria.",
        "payments.",
        "deadlines.",
        "conditions.",
        "exclusions.",
    )
    values: list[tuple[str, str]] = []
    for path, field in _iter_formal_fields(dsl):
        field_name = str(field.get("field", path))
        if not field_name.startswith(wanted_prefixes):
            continue
        if field.get("status") not in {"CONFIRMED", "INCOMPLETE", "ASSUMED"}:
            continue
        raw = field.get("value")
        if raw is None:
            continue
        values.append((field_name, _value_to_text(raw)))
    return values


def _iter_formal_fields(value: Any, path: str = "$"):
    if isinstance(value, dict):
        if {"field", "status", "value"}.issubset(value.keys()):
            yield path, value
        for key, child in value.items():
            yield from _iter_formal_fields(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _iter_formal_fields(child, f"{path}[{index}]")


def _value_to_text(value: Any) -> str:
    if isinstance(value, dict):
        if "amount" in value and "currency" in value:
            return f"{value['amount']} {value['currency']}"
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def _normalize(value: str) -> str:
    return " ".join(value.lower().split())


def _finding(kind: str, path: str, message: str, severity: SemanticFindingSeverity) -> SemanticFinding:
    return SemanticFinding(kind=kind, path=path, message=message, severity=severity)


def _validate_openrouter_runtime() -> None:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is required outside mock mode")
    try:
        import litellm  # noqa: F401
    except ImportError as exc:
        raise RuntimeError("Install verifier[openrouter] to use LiteLLM/OpenRouter") from exc


def _openrouter_verify(
    nl_command: str,
    dsl_text: str,
    plan_text: str,
    dsl_actions: list[str],
    plan_actions: list[str],
    trace: dict[str, Any] | None,
) -> VerificationReport:
    _validate_openrouter_runtime()
    import litellm

    response = litellm.completion(
        model=os.getenv("OPENROUTER_MODEL", "openrouter/openai/gpt-4.1-mini"),
        api_key=os.getenv("OPENROUTER_API_KEY"),
        messages=[
            {"role": "system", "content": "Return only verifier JSON matching the requested schema."},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "nl_command": nl_command,
                        "dsl_actions": dsl_actions,
                        "plan_actions": plan_actions,
                        "trace": trace,
                    },
                    ensure_ascii=False,
                ),
            },
        ],
        response_format={"type": "json_object"},
    )
    content = response["choices"][0]["message"]["content"]
    return VerificationReport.model_validate_json(content)
