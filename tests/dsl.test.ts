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

  it("rejects unsupported actions", () => {
    const dsl = mockPlan("Przygotuj raport");
    dsl.steps[0].action = "database.delete" as unknown as (typeof dsl.steps)[0]["action"];
    const result = validateTaskDsl(dsl);
    expect(result.ok).toBe(false);
    expect(result.issues.map((issue) => issue.path)).toContain("steps[0].action");
  });

  it("returns issues for structural errors", () => {
    const result = validateTaskDsl({
      version: "wrong.version",
      task: { id: "t1", input: "x" },
      sources: [{ id: "s1", connector: "mock", name: "mock.unknown" as never }],
      steps: [],
      output: {},
      policies: [],
      expectedResults: [],
      errorHandling: {}
    });
    expect(result.ok).toBe(false);
    expect(result.issues.map((issue) => issue.path)).toEqual(
      expect.arrayContaining(["version", "sources[0].name", "steps", "output", "errorHandling"])
    );
  });

  it("throws when parsing invalid DSL", () => {
    expect(() => parseTaskDsl("not json")).toThrow();
    expect(() => parseTaskDsl('{"version": "office.dsl.v1"}')).toThrow();
  });

  it("renders all human-readable DSL tokens", () => {
    const dsl = mockPlan("Przygotuj raport");
    dsl.steps[0].when = { var: "overdue", op: "exists" };
    dsl.steps.push({
      id: "ask-period",
      description: "Ask for reporting period",
      action: "user.ask",
      with: {},
      ask: { id: "period", prompt: "Jaki okres?", saveAs: "period" }
    });
    dsl.steps.push({
      id: "send",
      description: "Send report",
      action: "email.send",
      with: { from: "report" },
      saveAs: "sendResult",
      confirm: { id: "send-confirm", prompt: "Send report?", required: true }
    });
    const rendered = renderHumanDsl(dsl);
    expect(rendered).toContain("WHEN overdue exists true");
    expect(rendered).toContain("ASK period");
    expect(rendered).toContain("SAVE period");
    expect(rendered).toContain("CONFIRM send-confirm");
  });
});
