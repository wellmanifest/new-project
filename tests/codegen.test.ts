import { readFile } from "node:fs/promises";
import path from "node:path";
import { describe, expect, it } from "vitest";
import {
  ALLOWED_CODE_GENERATION_TARGETS,
  assertDslApprovedForCodeGeneration,
  createImplementationPlanFromApprovedDsl,
  generateNodeCodeFromApprovedDsl,
  hashCodeGenerationDslSnapshot,
  runGeneratedNodeTests
} from "../packages/codegen/src/index.js";
import {
  parseIntentContractDsl,
  type IntentContractDsl
} from "../packages/intent-contract-model/src/index.js";

const fixturePath = path.join(
  process.cwd(),
  "packages",
  "intent-contract-model",
  "fixtures",
  "service-agreement.intent-contract.json"
);

describe("Phase 9 JS/Node.js code generation", () => {
  it("defines a bounded dependency-free Node.js generation target", () => {
    expect(ALLOWED_CODE_GENERATION_TARGETS).toEqual([
      expect.objectContaining({
        id: "node-esm-contract-module",
        runtime: "node",
        moduleFormat: "esm",
        dependencyPolicy: "none",
        networkPolicy: "disabled",
        processPolicy: "no-child-process"
      })
    ]);
    expect(ALLOWED_CODE_GENERATION_TARGETS[0]?.outputFiles).toEqual([
      "package.json",
      "src/contract-spec.mjs",
      "test/contract-spec.test.mjs"
    ]);
  });

  it("refuses to generate code from DSL that is not approved for the current snapshot", async () => {
    const dsl = await loadFixtureDsl();

    expect(() => assertDslApprovedForCodeGeneration(dsl)).toThrow(/requires APPROVED records/);
    expect(() => generateNodeCodeFromApprovedDsl(dsl)).toThrow(/requires APPROVED records/);
  });

  it("creates a deterministic and auditable implementation plan from approved DSL", async () => {
    const dsl = await loadApprovedFixtureDsl();
    const first = createImplementationPlanFromApprovedDsl(dsl);
    const second = createImplementationPlanFromApprovedDsl(
      JSON.parse(JSON.stringify(dsl)) as IntentContractDsl
    );

    expect(first).toEqual(second);
    expect(first.dslHash).toBe(hashCodeGenerationDslSnapshot(dsl));
    expect(first.approvedBy).toEqual(["party-adam", "party-human1"]);
    expect(first.steps.map((step) => step.id)).toEqual([
      "extract-approved-contract-spec",
      "emit-generated-tests",
      "emit-package-manifest"
    ]);
    expect(first.steps[0]?.inputDslPaths).toContain("document.title");
    expect(first.steps[1]?.inputDslPaths).toContain("approvals");
  });

  it("generates JS/Node.js artifacts only from approved DSL fields", async () => {
    const dsl = await loadApprovedFixtureDsl();
    const result = generateNodeCodeFromApprovedDsl(dsl);

    expect(result.version).toBe("codegen.node.v1");
    expect(result.files.map((file) => file.path)).toEqual([
      "package.json",
      "src/contract-spec.mjs",
      "test/contract-spec.test.mjs"
    ]);
    const module =
      result.files.find((file) => file.path === "src/contract-spec.mjs")?.content ?? "";
    expect(module).toContain("Website service agreement draft");
    expect(module).toContain(hashCodeGenerationDslSnapshot(dsl));
    expect(module).not.toMatch(/eval|Function|child_process|fetch|XMLHttpRequest/);
    expect(result.files.every((file) => file.sha256.length === 64)).toBe(true);
    expect(result.verifierInput.generatedFiles).toHaveLength(3);
    expect(result.verifierInput.testResults).toEqual([]);
  });

  it("runs generated tests and includes the results in verifier input", async () => {
    const dsl = await loadApprovedFixtureDsl();
    const result = generateNodeCodeFromApprovedDsl(dsl);
    const run = await runGeneratedNodeTests(result);

    expect(run.passed).toBe(true);
    expect(run.tests.map((test) => test.passed)).toEqual([true, true, true]);
    expect(run.verifierInput.version).toBe("codegen.verifier-input.v1");
    expect(run.verifierInput.dslHash).toBe(result.plan.dslHash);
    expect(run.verifierInput.testResults).toEqual(run.tests);
    expect(run.verifierInput.approvedBy).toEqual(["party-adam", "party-human1"]);
  });
});

async function loadFixtureDsl(): Promise<IntentContractDsl> {
  return parseIntentContractDsl(await readFile(fixturePath, "utf8"));
}

async function loadApprovedFixtureDsl(): Promise<IntentContractDsl> {
  const dsl = await loadFixtureDsl();
  const dslHash = hashCodeGenerationDslSnapshot(dsl);
  dsl.approvals = [
    {
      id: "approval-human1-codegen",
      partyId: "party-human1",
      dslHash,
      decision: "APPROVED",
      approvedAt: "2026-07-27T00:00:00.000Z"
    },
    {
      id: "approval-human2-codegen",
      partyId: "party-adam",
      dslHash,
      decision: "APPROVED",
      approvedAt: "2026-07-27T00:01:00.000Z"
    }
  ];
  return dsl;
}
