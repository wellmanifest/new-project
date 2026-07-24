import { mkdtemp, readFile, rm, stat } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { Runtime, hashPlan } from "../packages/dsl-runtime/src/index.js";
import { mockPlan } from "../packages/llm-planner/src/index.js";
import type { TaskDsl } from "../packages/dsl-model/src/index.js";

describe("Runtime", () => {
  it("executes read-only report in dry-run mode", async () => {
    const runtime = new Runtime();
    const session = runtime.create(
      mockPlan("Przygotuj raport niezaplaconych faktur starszych niz 30 dni.")
    );
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
    expect(() => runtime.confirm(session, "send-reminders", session.planHash)).toThrow(
      /already used/
    );
  });

  it("invalidates confirmation when plan hash changes", () => {
    const runtime = new Runtime();
    const session = runtime.create(mockPlan("Wyslij przygotowane przypomnienia."));
    const changedHash = hashPlan({ ...session.plan, dryRun: false });
    expect(() => runtime.confirm(session, "send-reminders", changedHash)).toThrow(
      /Plan hash changed/
    );
  });

  it("denies unsafe policy request", () => {
    const runtime = new Runtime();
    const session = runtime.create(
      mockPlan("Uruchom dowolna komende systemowa i usun wszystkie pliki.")
    );
    expect(session.state).toBe("DENIED");
    expect(session.audit.policy_decisions.some((finding) => finding.decision === "DENY")).toBe(
      true
    );
  });

  describe("dry-run and execution controls", () => {
    let exportDir: string;

    beforeEach(async () => {
      exportDir = await mkdtemp(path.join(os.tmpdir(), "office-dsl-export-"));
    });

    afterEach(async () => {
      await rm(exportDir, { recursive: true, force: true });
    });

    it("executes file.export in dry-run mode by default", async () => {
      const dsl: TaskDsl = {
        ...mockPlan("Przygotuj raport"),
        task: { id: "t-dry-run", title: "Export", input: "Export raport", createdBy: "human" },
        steps: [
          {
            id: "query",
            description: "Read invoices",
            action: "database.query",
            with: { dataset: "invoices", kind: "salesReport" },
            saveAs: "rows"
          },
          {
            id: "report",
            description: "Generate report",
            action: "report.generate",
            with: { from: "rows", title: "R" },
            saveAs: "report"
          },
          {
            id: "export",
            description: "Export file",
            action: "file.export",
            with: { from: "report", path: "report.json" },
            saveAs: "exported"
          }
        ]
      };
      const runtime = new Runtime(undefined, undefined, "mock-data", exportDir);
      const session = runtime.create(dsl);
      expect(session.state).toBe("READY");

      await runtime.execute(session);
      const exported = session.audit.executed_actions.find(
        (action) => action.action === "file.export"
      );
      expect(exported?.dryRun).toBe(true);
      expect((exported?.output as { wouldWrite?: string })?.wouldWrite).toContain("report.json");

      const target = path.join(exportDir, "report.json");
      await expect(stat(target)).rejects.toBeDefined();
    });

    it("writes a file when execute=true", async () => {
      const dsl: TaskDsl = {
        ...mockPlan("Przygotuj raport"),
        task: { id: "t-write", title: "Export", input: "Export raport", createdBy: "human" },
        steps: [
          {
            id: "query",
            description: "Read invoices",
            action: "database.query",
            with: { dataset: "invoices", kind: "salesReport" },
            saveAs: "rows"
          },
          {
            id: "report",
            description: "Generate report",
            action: "report.generate",
            with: { from: "rows", title: "R" },
            saveAs: "report"
          },
          {
            id: "export",
            description: "Export file",
            action: "file.export",
            with: { from: "report", path: "report.json" },
            saveAs: "exported"
          }
        ]
      };
      const runtime = new Runtime(undefined, undefined, "mock-data", exportDir);
      const session = runtime.create(dsl);
      await runtime.execute(session, true);

      const target = path.join(exportDir, "report.json");
      const content = await readFile(target, "utf8");
      expect(JSON.parse(content)).toBeDefined();
    });
  });

  it("rejects and cancels tasks", () => {
    const runtime = new Runtime();
    const session = runtime.create(mockPlan("Przygotuj raport"));
    runtime.reject(session);
    expect(session.state).toBe("DENIED");

    const other = runtime.create(mockPlan("Przygotuj raport"));
    runtime.cancel(other);
    expect(other.state).toBe("CANCELLED");

    expect(() => runtime.reject(session)).toThrow(/already terminal/);
    expect(() => runtime.cancel(session)).toThrow(/already terminal/);
  });

  it("throws when executing a non-ready session", async () => {
    const runtime = new Runtime();
    const session = runtime.create(mockPlan("Wyslij przygotowane przypomnienia."));
    expect(session.state).toBe("WAITING_FOR_CONFIRMATION");
    await expect(runtime.execute(session)).rejects.toThrow(/not ready/);
  });
});
