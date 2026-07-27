export function mockVerification(input: string, dsl: unknown): unknown {
  const combined = `${input} ${JSON.stringify(dsl)}`.toLowerCase();
  const unauthorized = input.toLowerCase().includes("nie wysy") && combined.includes("email.send");
  return {
    verdict: unauthorized ? "FAIL" : "PASS",
    score: unauthorized ? 0.2 : 0.95,
    intent_coverage: unauthorized ? 0.7 : 0.95,
    missing_requirements: [],
    unauthorized_actions: unauthorized ? ["email.send"] : [],
    contradictions: [],
    policy_violations: [],
    requires_confirmation: combined.includes("email.send") ? ["email.send"] : [],
    explanation: unauthorized
      ? "DSL sends email although user requested drafts only."
      : "Mock verifier accepted DSL.",
    recommended_action: unauthorized ? "REGENERATE" : "ACCEPT"
  };
}
