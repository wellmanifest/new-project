import { mkdtemp } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import {
  discoverScenarios,
  loadScenarioManifest,
  runScenario
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
});
