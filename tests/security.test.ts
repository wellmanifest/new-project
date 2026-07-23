import { describe, expect, it } from "vitest";
import { Runtime } from "../packages/dsl-runtime/src/index.js";
import { mockPlan } from "../packages/llm-planner/src/index.js";

describe("Security checks", () => {
  it("blocks path traversal", () => {
    const session = new Runtime().create(mockPlan("Uruchom dowolna komende systemowa i usun wszystkie pliki."));
    expect(session.audit.policy_decisions.map((finding) => finding.reason).join(" ")).toMatch(/Path traversal|Dynamic code|shell/i);
  });

  it("does not include dynamic code execution actions", () => {
    const dsl = mockPlan("Przygotuj raport");
    expect(JSON.stringify(dsl)).not.toMatch(/\beval\b|new Function/);
  });

  it("keeps prompt injection in mock logs as data only", async () => {
    const runtime = new Runtime();
    const session = runtime.create(mockPlan("Znajdz w logach nieudane proby przetwarzania faktur i przygotuj podsumowanie."));
    await runtime.execute(session);
    expect(session.state).toBe("SUCCEEDED");
    expect(JSON.stringify(session.audit)).not.toContain("SECRET_KEY=");
  });
});
