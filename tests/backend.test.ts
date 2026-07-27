import { mkdtemp, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { afterAll, beforeAll, describe, expect, it } from "vitest";

describe("Backend API", () => {
  let tmpDir: string;
  let server: import("http").Server;
  let port: number;
  let baseUrl: string;

  beforeAll(async () => {
    tmpDir = await mkdtemp(path.join(os.tmpdir(), "office-dsl-backend-"));
    process.env.NODE_ENV = "test";
    process.env.OFFICE_DSL_TASK_DIR = path.join(tmpDir, "tasks");
    process.env.OFFICE_DSL_AUDIT_DIR = path.join(tmpDir, "audit");
    process.env.OFFICE_DSL_EXPORT_DIR = path.join(tmpDir, "exports");
    process.env.OFFICE_DSL_DATA_DIR = "mock-data";
    const mod = await import("../apps/backend/src/server.js");
    server = mod.server;
    await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
    const address = server.address();
    if (address === null || typeof address === "string") {
      throw new Error("Server did not bind to a port");
    }
    port = address.port;
    baseUrl = `http://127.0.0.1:${port}`;
  });

  afterAll(async () => {
    await new Promise<void>((resolve) => server.close(() => resolve()));
    await rm(tmpDir, { recursive: true, force: true });
    delete process.env.NODE_ENV;
    delete process.env.OFFICE_DSL_TASK_DIR;
    delete process.env.OFFICE_DSL_AUDIT_DIR;
    delete process.env.OFFICE_DSL_EXPORT_DIR;
    delete process.env.OFFICE_DSL_DATA_DIR;
  });

  async function postJson(url: string, body: unknown): Promise<unknown> {
    const response = await fetch(`${baseUrl}${url}`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body)
    });
    return response.json();
  }

  async function getJson(url: string): Promise<unknown> {
    const response = await fetch(`${baseUrl}${url}`);
    return response.json();
  }

  it("serves the static web demo", async () => {
    const response = await fetch(`${baseUrl}/`);
    const html = await response.text();
    expect(html).toContain("Office DSL MVP");
    expect(html).toContain("mock mode, dry-run default");
  });

  it("serves an OpenAPI descriptor", async () => {
    const spec = (await getJson("/openapi.json")) as { openapi: string };
    expect(spec.openapi).toBe("3.1.0");
    expect(spec).toHaveProperty("paths");
  });

  it("lists actions and connectors", async () => {
    const actions = (await getJson("/api/actions")) as Array<{ name: string }>;
    const names = actions.map((a) => a.name);
    expect(names).toContain("database.query");
    expect(names).toContain("email.send");

    const connectors = (await getJson("/api/connectors")) as Array<{ id: string }>;
    expect(connectors[0].id).toBe("mock");
  });

  it("creates and inspects a task", async () => {
    const created = (await postJson("/api/tasks", {
      input: "Przygotuj raport"
    })) as { id: string; state: string };
    expect(created.state).toBe("READY");

    const loaded = (await getJson(`/api/tasks/${created.id}`)) as { id: string; state: string };
    expect(loaded.id).toBe(created.id);
    expect(loaded.state).toBe("READY");
  });

  it("exposes CQRS-style approvals, questions, and event stream endpoints", async () => {
    const created = (await postJson("/api/tasks", {
      input: "Przygotuj raport"
    })) as { id: string; intentContractHash: string };

    const questions = (await getJson(`/api/tasks/${created.id}/questions?party=Human1`)) as {
      finalizationReady: boolean;
      questions: unknown[];
    };
    expect(questions).toHaveProperty("finalizationReady");
    expect(Array.isArray(questions.questions)).toBe(true);

    const human1 = (await postJson(`/api/tasks/${created.id}/approve`, {
      party: "Human1",
      hash: created.intentContractHash
    })) as { approvals: unknown[] };
    expect(human1.approvals).toHaveLength(1);

    const human2 = (await postJson(`/api/tasks/${created.id}/approve`, {
      party: "Human2",
      hash: created.intentContractHash
    })) as { approvals: unknown[] };
    expect(human2.approvals).toHaveLength(2);

    const approvals = (await getJson(`/api/tasks/${created.id}/approvals`)) as unknown[];
    expect(approvals).toHaveLength(2);

    const events = (await getJson(`/api/tasks/${created.id}/events`)) as Array<{
      from: string;
      to: string;
      reason: string;
    }>;
    expect(events.map((event) => event.to)).toEqual(
      expect.arrayContaining(["DSL_GENERATED", "VALIDATING", "READY"])
    );
  });
  it("answers clarification, executes dry-run, and returns audit", async () => {
    const created = (await postJson("/api/tasks", {
      input: "Przygotuj raport sprzedazy."
    })) as { id: string; state: string };
    expect(created.state).toBe("WAITING_FOR_INPUT");

    const answered = (await postJson(`/api/tasks/${created.id}/answers`, {
      questionId: "period",
      answer: "ostatnie 30 dni"
    })) as { state: string };
    expect(answered.state).toBe("READY");

    const executed = (await postJson(`/api/tasks/${created.id}/execute`, {
      execute: false
    })) as { state: string; audit: { final_status: string } };
    expect(executed.state).toBe("SUCCEEDED");
    expect(executed.audit.final_status).toBe("SUCCEEDED");

    const audit = (await getJson(`/api/tasks/${created.id}/audit`)) as { final_status: string };
    expect(audit.final_status).toBe("SUCCEEDED");
  });

  it("confirms a sensitive action and rejects or cancels tasks", async () => {
    const created = (await postJson("/api/tasks", {
      input: "Wyslij przygotowane przypomnienia."
    })) as { id: string; state: string; planHash: string };
    expect(created.state).toBe("WAITING_FOR_CONFIRMATION");

    const confirmed = (await postJson(`/api/tasks/${created.id}/confirm`, {
      confirmationId: "send-reminders",
      planHash: created.planHash
    })) as { state: string };
    expect(confirmed.state).toBe("READY");

    const executed = (await postJson(`/api/tasks/${created.id}/execute`, {
      execute: false
    })) as { state: string };
    expect(executed.state).toBe("SUCCEEDED");

    const createdForReject = (await postJson("/api/tasks", {
      input: "Przygotuj raport"
    })) as { id: string };
    const rejected = (await postJson(`/api/tasks/${createdForReject.id}/reject`, {})) as {
      state: string;
    };
    expect(rejected.state).toBe("DENIED");

    const createdForCancel = (await postJson("/api/tasks", {
      input: "Przygotuj raport"
    })) as { id: string };
    const cancelled = (await postJson(`/api/tasks/${createdForCancel.id}/cancel`, {})) as {
      state: string;
    };
    expect(cancelled.state).toBe("CANCELLED");
  });
});
