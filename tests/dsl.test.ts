import { describe, expect, it } from "vitest";
import { parseTaskDsl, renderHumanDsl, validateTaskDsl } from "../packages/dsl-model/src/index.js";
import { mockPlan } from "../packages/llm-planner/src/index.js";

describe("DSL model", () => {
  it("validates mock planner output", () => {
    const dsl = mockPlan("Przygotuj raport niezaplaconych faktur starszych niz 30 dni.");
    expect(validateTaskDsl(dsl).ok).toBe(true);
  });

  it("parses canonical JSON DSL", () => {
    const dsl = mockPlan("Znajdz w logach invoice failed");
    expect(parseTaskDsl(JSON.stringify(dsl)).steps[0]?.action).toBe("log.search");
  });

  it("renders human readable DSL tokens", () => {
    const rendered = renderHumanDsl(mockPlan("Przygotuj raport"));
    expect(rendered).toContain("TASK");
    expect(rendered).toContain("INPUT");
    expect(rendered).toContain("STEP");
    expect(rendered).toContain("POLICY");
  });

  it("rejects email.send without confirmation", () => {
    const dsl = mockPlan("Wyslij przygotowane przypomnienia.");
    const send = dsl.steps.find((step) => step.action === "email.send");
    if (send) delete send.confirm;
    expect(validateTaskDsl(dsl).ok).toBe(false);
  });
});
