import { describe, expect, it } from "vitest";
import { Runtime, hashPlan } from "../packages/dsl-runtime/src/index.js";
import { mockPlan } from "../packages/llm-planner/src/index.js";

describe("Runtime", () => {
  it("executes read-only report in dry-run mode", async () => {
    const runtime = new Runtime();
    const session = runtime.create(mockPlan("Przygotuj raport niezaplaconych faktur starszych niz 30 dni."));
    expect(session.state).toBe("READY");
    const results = await runtime.execute(session);
    expect(session.state).toBe("SUCCEEDED");
    expect(results.map((result) => result.action)).toEqual(["database.query", "report.generate"]);
  });

  it("waits for clarification and resumes after answer", () => {
    const runtime = new Runtime();
    const session = runtime.create(mockPlan("Przygotuj raport sprzedazy."));
    expect(session.state).toBe("WAITING_FOR_INPUT");
    runtime.answer(session, "period", "ostatnie 30 dni");
    expect(session.state).toBe("READY");
  });

  it("requires confirmation for email.send", () => {
    const runtime = new Runtime();
    const session = runtime.create(mockPlan("Wyslij przygotowane przypomnienia."));
    expect(session.state).toBe("WAITING_FOR_CONFIRMATION");
    runtime.confirm(session, "send-reminders", session.planHash);
    expect(session.state).toBe("READY");
  });

  it("rejects reused confirmation", () => {
    const runtime = new Runtime();
    const session = runtime.create(mockPlan("Wyslij przygotowane przypomnienia."));
    runtime.confirm(session, "send-reminders", session.planHash);
    expect(() => runtime.confirm(session, "send-reminders", session.planHash)).toThrow(/already used/);
  });

  it("invalidates confirmation when plan hash changes", () => {
    const runtime = new Runtime();
    const session = runtime.create(mockPlan("Wyslij przygotowane przypomnienia."));
    const changedHash = hashPlan({ ...session.plan, dryRun: false });
    expect(() => runtime.confirm(session, "send-reminders", changedHash)).toThrow(/Plan hash changed/);
  });

  it("denies unsafe policy request", () => {
    const runtime = new Runtime();
    const session = runtime.create(mockPlan("Uruchom dowolna komende systemowa i usun wszystkie pliki."));
    expect(session.state).toBe("DENIED");
    expect(session.audit.policy_decisions.some((finding) => finding.decision === "DENY")).toBe(true);
  });
});
