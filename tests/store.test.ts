import { mkdtemp, rm, stat } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { mockPlan } from "../packages/llm-planner/src/index.js";
import { Runtime } from "../packages/dsl-runtime/src/index.js";
import { FileTaskStore } from "../packages/dsl-runtime/src/store.js";

describe("FileTaskStore", () => {
  let tmpDir: string;

  beforeEach(async () => {
    tmpDir = await mkdtemp(path.join(os.tmpdir(), "office-dsl-store-"));
    process.env.OFFICE_DSL_TASK_DIR = tmpDir;
  });

  afterEach(async () => {
    delete process.env.OFFICE_DSL_TASK_DIR;
    await rm(tmpDir, { recursive: true, force: true });
  });

  it("saves a session and its audit record to disk", async () => {
    const store = new FileTaskStore();
    const session = new Runtime().create(mockPlan("Przygotuj raport"));
    await store.save(session);

    const taskFile = path.join(tmpDir, "mock-llm", "tasks", `${session.id}.json`);
    const auditFile = path.join(tmpDir, "mock-llm", "audit", `${session.id}.json`);
    expect((await stat(taskFile)).isFile()).toBe(true);
    expect((await stat(auditFile)).isFile()).toBe(true);
  });

  it("loads a previously saved session", async () => {
    const store = new FileTaskStore();
    const session = new Runtime().create(mockPlan("Przygotuj raport"));
    await store.save(session);

    const loaded = await store.load(session.id);
    expect(loaded.id).toBe(session.id);
    expect(loaded.state).toBe("READY");
    expect(loaded.audit.task_id).toBe(session.dsl.task.id);
  });

  it("lists saved sessions", async () => {
    const store = new FileTaskStore();
    const first = new Runtime().create(mockPlan("Przygotuj raport"));
    const second = new Runtime().create(mockPlan("Wyslij przygotowane przypomnienia."));
    await store.save(first);
    await store.save(second);

    const listed = await store.list();
    const ids = listed.map((s) => s.id);
    expect(ids).toContain(first.id);
    expect(ids).toContain(second.id);
  });
});
