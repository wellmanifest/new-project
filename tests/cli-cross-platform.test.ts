import { execFile } from "node:child_process";
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { promisify } from "node:util";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

const execFileAsync = promisify(execFile);
const repoRoot = process.cwd();
const node = process.execPath;
const cliEntry = "packages/cli/src/intent.ts";

async function runIntent(
  args: string[],
  env: Record<string, string> = {}
): Promise<{ code: number; stdout: string; json: unknown }> {
  const { stdout, stderr } = await execFileAsync(node, ["--import", "tsx", cliEntry, ...args], {
    cwd: repoRoot,
    env: { ...process.env, ...env }
  });
  let json: unknown;
  try {
    json = JSON.parse(stdout);
  } catch {
    json = null;
  }
  return { code: stderr ? 1 : 0, stdout, json };
}

describe("cross-platform CLI path handling", () => {
  let tmpDir: string;

  beforeEach(async () => {
    tmpDir = await mkdtemp(path.join(os.tmpdir(), "well-manifest-cli-"));
  });

  afterEach(async () => {
    await rm(tmpDir, { recursive: true, force: true });
  });

  it("accepts POSIX-style paths on Windows and resolves them", async () => {
    const dsl = {
      version: "intent-contract.dsl.v1",
      document: {
        id: "doc-1",
        type: {
          field: "document.type",
          value: "TASK_DELEGATION",
          status: "CONFIRMED",
          requiredForCompletion: true,
          source: { type: "system", id: "cli" },
          approvedBy: []
        },
        title: {
          field: "document.title",
          value: "Test",
          status: "CONFIRMED",
          requiredForCompletion: false,
          source: { type: "system", id: "cli" },
          approvedBy: []
        },
        language: {
          field: "document.language",
          value: "en",
          status: "CONFIRMED",
          requiredForCompletion: true,
          source: { type: "system", id: "cli" },
          approvedBy: []
        }
      },
      contract: null,
      parties: [],
      roles: [],
      intents: [],
      subjects: [],
      obligations: [],
      deliverables: [],
      deadlines: [],
      payments: [],
      conditions: [],
      dependencies: [],
      acceptanceCriteria: [],
      exclusions: [],
      assumptions: [],
      risks: [],
      conflicts: [],
      questions: [],
      approvals: [],
      sourceReferences: [],
      render: [],
      execution: []
    };
    const dslFile = path.join(tmpDir, "contract.dsl.json");
    await writeFile(dslFile, JSON.stringify(dsl, null, 2));
    const posixPath = dslFile.replace(/\\/g, "/");
    const { code, json } = await runIntent(["verify", posixPath, "--json"]);
    expect(code).toBe(0);
    expect(json).toMatchObject({ ok: true, command: "verify" });
  });

  it("accepts file:// URLs", async () => {
    const dsl = {
      version: "intent-contract.dsl.v1",
      document: {
        id: "doc-1",
        type: {
          field: "document.type",
          value: "TASK_DELEGATION",
          status: "CONFIRMED",
          requiredForCompletion: true,
          source: { type: "system", id: "cli" },
          approvedBy: []
        },
        title: {
          field: "document.title",
          value: "Test",
          status: "CONFIRMED",
          requiredForCompletion: false,
          source: { type: "system", id: "cli" },
          approvedBy: []
        },
        language: {
          field: "document.language",
          value: "en",
          status: "CONFIRMED",
          requiredForCompletion: true,
          source: { type: "system", id: "cli" },
          approvedBy: []
        }
      },
      contract: null,
      parties: [],
      roles: [],
      intents: [],
      subjects: [],
      obligations: [],
      deliverables: [],
      deadlines: [],
      payments: [],
      conditions: [],
      dependencies: [],
      acceptanceCriteria: [],
      exclusions: [],
      assumptions: [],
      risks: [],
      conflicts: [],
      questions: [],
      approvals: [],
      sourceReferences: [],
      render: [],
      execution: []
    };
    const dslFile = path.join(tmpDir, "contract.dsl.json");
    await writeFile(dslFile, JSON.stringify(dsl, null, 2));
    const fileUrl = `file://${dslFile.replace(/\\/g, "/")}`;
    const { code, json } = await runIntent(["verify", fileUrl, "--json"]);
    expect(code).toBe(0);
    expect(json).toMatchObject({ ok: true, command: "verify" });
  });

  it("renders a document and outputs JSON", async () => {
    const dslFile = path.join(tmpDir, "contract.dsl.json");
    await writeFile(
      dslFile,
      JSON.stringify(
        {
          version: "intent-contract.dsl.v1",
          document: {
            id: "doc-1",
            type: {
              field: "document.type",
              value: "TASK_DELEGATION",
              status: "CONFIRMED",
              requiredForCompletion: true,
              source: { type: "system", id: "cli" },
              approvedBy: []
            },
            title: {
              field: "document.title",
              value: "CLI task delegation",
              status: "CONFIRMED",
              requiredForCompletion: false,
              source: { type: "system", id: "cli" },
              approvedBy: []
            },
            language: {
              field: "document.language",
              value: "en",
              status: "CONFIRMED",
              requiredForCompletion: true,
              source: { type: "system", id: "cli" },
              approvedBy: []
            }
          },
          contract: null,
          parties: [
            {
              id: "p1",
              name: {
                field: "parties.p1.name",
                value: "Human1",
                status: "CONFIRMED",
                requiredForCompletion: true,
                source: { type: "system", id: "cli" },
                approvedBy: []
              },
              role: {
                field: "parties.p1.role",
                value: "Human1",
                status: "CONFIRMED",
                requiredForCompletion: true,
                source: { type: "system", id: "cli" },
                approvedBy: []
              }
            }
          ],
          roles: [],
          intents: [],
          subjects: [],
          obligations: [],
          deliverables: [],
          deadlines: [],
          payments: [],
          conditions: [],
          dependencies: [],
          acceptanceCriteria: [],
          exclusions: [],
          assumptions: [],
          risks: [],
          conflicts: [],
          questions: [],
          approvals: [],
          sourceReferences: [],
          render: [],
          execution: []
        },
        null,
        2
      )
    );
    const { code, json } = await runIntent(["render", dslFile, "--json"]);
    expect(code).toBe(0);
    expect(json).toMatchObject({ command: "render", ok: true });
    expect(JSON.stringify(json)).toContain("CLI task delegation");
    expect(JSON.stringify(json)).toContain("Traceability Map");
  });

  it("produces human-readable output with --human", async () => {
    const { code, stdout } = await runIntent(["version", "--human"]);
    expect(code).toBe(0);
    expect(stdout).toContain("well-manifest-intent.cli.v1");
    expect(stdout).toContain("version:");
  });

  it("plans a message into an Intent/Contract DSL", async () => {
    const { code, json } = await runIntent([
      "plan",
      "Hire a backend developer for 12000 PLN per month",
      "--json"
    ]);
    expect(code).toBe(0);
    expect(json).toMatchObject({ command: "plan", ok: true });
    expect((json as { output: { dslHash: string } }).output.dslHash).toHaveLength(64);
  });
});

describe("CLI command help and version", () => {
  it("reports the intent CLI version", async () => {
    const { code, json } = await runIntent(["version", "--json"]);
    expect(code).toBe(0);
    expect(json).toMatchObject({
      command: "version",
      ok: true,
      output: { version: "well-manifest-intent.cli.v1" }
    });
  });

  it("returns a help message without errors", async () => {
    const { code, stdout } = await runIntent(["help"]);
    expect(code).toBe(0);
    expect(stdout).toContain("well-manifest-intent");
    expect(stdout).toContain("plan");
    expect(stdout).toContain("render");
    expect(stdout).toContain("verify");
  });
});
