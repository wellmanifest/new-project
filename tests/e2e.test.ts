import { describe, expect, it } from "vitest";
import { Runtime } from "../packages/dsl-runtime/src/index.js";
import { mockPlan } from "../packages/llm-planner/src/index.js";

describe("E2E NL to DSL to verification to runtime", () => {
  it("runs read-only scenario end to end", async () => {
    const nl = "Przygotuj raport niezaplaconych faktur starszych niz 30 dni.";
    const dsl = mockPlan(nl);
    const runtime = new Runtime();
    const session = runtime.create(dsl, { verdict: "PASS", score: 0.95, recommended_action: "ACCEPT" });
    expect(session.audit.validation.ok).toBe(true);
    expect(session.state).toBe("READY");
    await runtime.execute(session);
    expect(session.audit.final_status).toBe("SUCCEEDED");
    expect(session.audit.plan_hash).toHaveLength(64);
  });

  it("runs confirmation workflow without real email send", async () => {
    const runtime = new Runtime();
    const session = runtime.create(mockPlan("Wyslij przygotowane przypomnienia."));
    runtime.confirm(session, "send-reminders", session.planHash);
    await runtime.execute(session);
    const send = session.audit.executed_actions.find((action) => action.action === "email.send");
    expect(send?.dryRun).toBe(true);
    expect(send?.output).toMatchObject({ wouldSend: 2 });
  });
});
