import { execFile } from "node:child_process";
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { promisify } from "node:util";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { mockPlan } from "../packages/llm-planner/src/index.js";

const execFileAsync = promisify(execFile);
const repoRoot = process.cwd();
const node = process.execPath;
const tsxArgs = ["--import", "tsx", "packages/cli/src/index.ts"];

interface CliEnv {
  OFFICE_DSL_TASK_DIR: string;
  OFFICE_DSL_AUDIT_DIR: string;
  OFFICE_DSL_EXPORT_DIR: string;
  OFFICE_DSL_DATA_DIR: string;
}

async function runCli(
  args: string[],
  env: CliEnv
): Promise<{ code: number; stdout: string; stderr: string; json: unknown }> {
  const { stdout, stderr } = await execFileAsync(node, [...tsxArgs, ...args], {
    cwd: repoRoot,
    env: { ...process.env, ...env }
  });
  let json: unknown;
  try {
    json = JSON.parse(stdout);
  } catch {
    json = null;
  }
  return { code: 0, stdout, stderr, json };
}

describe("CLI", () => {
  let tmpDir: string;
  let env: CliEnv;

  beforeEach(async () => {
    tmpDir = await mkdtemp(path.join(os.tmpdir(), "office-dsl-cli-"));
    env = {
      OFFICE_DSL_TASK_DIR: path.join(tmpDir, "tasks"),
      OFFICE_DSL_AUDIT_DIR: path.join(tmpDir, "audit"),
      OFFICE_DSL_EXPORT_DIR: path.join(tmpDir, "exports"),
      OFFICE_DSL_DATA_DIR: "mock-data"
    };
  });

  afterEach(async () => {
    await rm(tmpDir, { recursive: true, force: true });
  });

  it("plans a task and returns JSON with state READY", async () => {
    const result = await runCli(["plan", "Przygotuj raport", "--json"], env);
    expect(result.json).toMatchObject({
      state: "READY",
      dsl: { version: "office.dsl.v1" }
    });
    expect(result.json).toHaveProperty("taskId");
    expect(result.json).toHaveProperty("planHash");
    expect(result.json).toHaveProperty("humanDsl");
  });

  it("validates a DSL file", async () => {
    const dslFile = path.join(tmpDir, "dsl.json");
    await writeFile(dslFile, JSON.stringify(mockPlan("Przygotuj raport"), null, 2));
    const result = await runCli(["validate", dslFile, "--json"], env);
    expect(result.json).toMatchObject({ ok: true });
    expect(result.json).toHaveProperty("humanDsl");
  });

  it("inspects a saved task", async () => {
    const planResult = await runCli(["plan", "Przygotuj raport", "--json"], env);
    const taskId = (planResult.json as { taskId: string }).taskId;
    const result = await runCli(["inspect", taskId, "--json"], env);
    expect(result.json).toMatchObject({ id: taskId, state: "READY" });
  });

  it("answers a clarification and executes dry-run", async () => {
    const planResult = await runCli(["plan", "Przygotuj raport sprzedazy.", "--json"], env);
    const taskId = (planResult.json as { taskId: string }).taskId;
    const answerResult = await runCli(
      ["answer", taskId, "period", "ostatnie 30 dni", "--json"],
      env
    );
    expect(answerResult.json).toMatchObject({ state: "READY" });

    const executeResult = await runCli(["execute", taskId, "--json"], env);
    expect(executeResult.json).toMatchObject({ state: "SUCCEEDED", dryRun: true });
  });

  it("confirms a sensitive action and executes dry-run", async () => {
    const planResult = await runCli(["plan", "Wyslij przygotowane przypomnienia.", "--json"], env);
    const taskId = (planResult.json as { taskId: string }).taskId;
    const planHash = (planResult.json as { planHash: string }).planHash;
    const confirmResult = await runCli(
      ["confirm", taskId, "send-reminders", planHash, "--json"],
      env
    );
    expect(confirmResult.json).toMatchObject({ state: "READY" });

    const executeResult = await runCli(["execute", taskId, "--json"], env);
    expect(executeResult.json).toMatchObject({ state: "SUCCEEDED", dryRun: true });
    const results =
      (
        executeResult.json as {
          results?: Array<{ action: string; dryRun: boolean; output: unknown }>;
        }
      ).results ?? [];
    const sent = results.find((action) => action.action === "email.send");
    expect(sent?.dryRun).toBe(true);
  });

  it("rejects a task and lists history", async () => {
    const planResult = await runCli(["plan", "Przygotuj raport", "--json"], env);
    const taskId = (planResult.json as { taskId: string }).taskId;
    const rejectResult = await runCli(["reject", taskId, "--json"], env);
    expect(rejectResult.json).toMatchObject({ state: "DENIED" });

    const historyResult = await runCli(["history", "--json"], env);
    const items = historyResult.json as Array<{ taskId: string; state: string }>;
    expect(items.some((item) => item.taskId === taskId && item.state === "DENIED")).toBe(true);
  });
});
