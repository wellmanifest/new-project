import { existsSync } from "node:fs";
import { cp, mkdtemp, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import {
  discoverScenarios,
  loadScenarioManifest,
  runScenario,
  validateScenarioManifest
} from "../packages/example-runner/src/index.js";

const repoRoot = process.cwd();

describe("example runner", () => {
  it("loads canonical scenario manifests", async () => {
    const scenarios = await discoverScenarios(repoRoot);
    expect(scenarios.map((scenario) => path.basename(scenario))).toContain("01-read-only-report");
    const manifest = await loadScenarioManifest(
      path.join(repoRoot, "examples", "01-read-only-report")
    );
    expect(manifest.version).toBe("example.scenario.v1");
    expect(manifest.pipeline.planner.kind).toBe("fixture");
    expect(manifest.pipeline.verifier.kind).toBe("python");
  });

  it("runs one scenario and compares expected artifacts", async () => {
    const generatedRoot = await mkdtemp(path.join(os.tmpdir(), "office-dsl-example-runner-"));
    const result = await runScenario({
      repoRoot,
      scenarioDir: path.join(repoRoot, "examples", "01-read-only-report"),
      generatedRoot
    });
    expect(result.ok).toBe(true);
    expect(result.artifacts.plan.actions).toEqual(["database.query", "report.generate"]);
    expect(result.artifacts.verification).toMatchObject({
      verdict: "PASS",
      recommended_action: "ACCEPT"
    });
  });

  it("writes default generated outputs beside the example scenario as .dsl.hcl", async () => {
    const scenarioDir = path.join(repoRoot, "examples", "01-read-only-report");
    const generatedRoot = path.join(scenarioDir, "generated");
    await rm(generatedRoot, { recursive: true, force: true });

    const result = await runScenario({ repoRoot, scenarioDir });

    expect(result.generatedDir).toBe(generatedRoot);
    expect(existsSync(path.join(generatedRoot, "actual.dsl.hcl"))).toBe(true);
    expect(existsSync(path.join(generatedRoot, "actual.plan.dsl.hcl"))).toBe(true);
    expect(existsSync(path.join(generatedRoot, "verifier-input.dsl.hcl"))).toBe(true);
    expect(existsSync(path.join(generatedRoot, "actual.dsl.md"))).toBe(false);
    await rm(generatedRoot, { recursive: true, force: true });
  });
  it("discovers all six example scenarios", async () => {
    const scenarios = await discoverScenarios(repoRoot);
    const ids = scenarios.map((scenario) => path.basename(scenario));
    expect(ids).toHaveLength(6);
    expect(ids).toEqual(ids.slice().sort());
  });

  it("runs all examples without regressions", async () => {
    const generatedRoot = await mkdtemp(path.join(os.tmpdir(), "office-dsl-examples-all-"));
    const scenarios = await discoverScenarios(repoRoot);
    const results = await Promise.all(
      scenarios.map((scenarioDir) =>
        runScenario({
          repoRoot,
          scenarioDir,
          generatedRoot: path.join(generatedRoot, path.basename(scenarioDir))
        })
      )
    );
    for (const result of results) {
      expect(result.ok).toBe(true);
      expect(result.failures).toEqual([]);
    }
    await rm(generatedRoot, { recursive: true, force: true });
  });

  it("produces readable diffs for mismatched artifacts", async () => {
    const baseDir = path.join(repoRoot, "examples", "01-read-only-report");
    const generatedRoot = await mkdtemp(path.join(os.tmpdir(), "office-dsl-diff-"));
    const scenarioDir = path.join(generatedRoot, "bad-plan");
    await cp(baseDir, scenarioDir, { recursive: true });
    await writeFile(
      path.join(scenarioDir, "out", "expected.plan.json"),
      JSON.stringify(
        {
          actions: ["email.send"],
          requiresInput: false,
          requiresConfirmation: true,
          dryRun: true,
          expectedState: "READY"
        },
        null,
        2
      )
    );

    const result = await runScenario({
      repoRoot,
      scenarioDir,
      generatedRoot: path.join(generatedRoot, "generated")
    });
    expect(result.ok).toBe(false);
    const failure = result.failures.find((f) => f.includes("plan.actions"));
    expect(failure).toBeDefined();
    expect(failure).toContain("expected:");
    expect(failure).toContain("actual:");
    await rm(generatedRoot, { recursive: true, force: true });
  });

  it("rejects invalid scenario manifests", () => {
    const invalid = {
      version: "wrong",
      id: "",
      title: "Invalid",
      kind: "office-command",
      input: {},
      pipeline: { planner: { kind: "fixture" }, runtime: {}, verifier: { kind: "python" } },
      expected: {}
    } as unknown as import("../packages/example-runner/src/scenario.js").ScenarioManifest;
    expect(() => validateScenarioManifest(invalid, ".")).toThrow(/version must be/);
  });
});
