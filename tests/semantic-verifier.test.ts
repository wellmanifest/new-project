import { describe, expect, it } from "vitest";
import { Runtime, runPythonSemanticVerifier } from "../packages/dsl-runtime/src/index.js";
import { mockPlan } from "../packages/llm-planner/src/index.js";

describe("Phase 10 Python semantic verifier integration", () => {
  it("runs the Python semantic verifier through the TypeScript runtime bridge", async () => {
    const report = await runPythonSemanticVerifier({
      original_nl: "Website agreement for Landing page.",
      approved_dsl: {
        version: "intent-contract.dsl.v1",
        document: {
          id: "doc-1",
          title: {
            field: "document.title",
            status: "CONFIRMED",
            value: "Website agreement",
            requiredForCompletion: true,
            approvedBy: [],
            source: { id: "m1", quote: "Website agreement" }
          }
        },
        deliverables: [
          {
            id: "del-1",
            description: {
              field: "deliverables.del-1.description",
              status: "CONFIRMED",
              value: "Landing page",
              requiredForCompletion: true,
              approvedBy: [],
              source: { id: "m1", quote: "Landing page" }
            }
          }
        ],
        acceptanceCriteria: [],
        conflicts: []
      },
      rendered_document: "# Website agreement\nLanding page\n",
      codegen_verifier_input: {
        generatedFiles: [{ path: "src/contract-spec.mjs", sha256: "a".repeat(64) }],
        testResults: [{ name: "generated tests", passed: true }]
      },
      testgen_verifier_input: { uncoveredAcceptanceCriteriaIds: [] }
    });

    expect(report).toMatchObject({ verdict: "PASS", recommended_action: "ACCEPT" });
  });

  it("captures Python verifier output in runtime audit and gates failed sessions", async () => {
    const runtime = new Runtime();
    const session = await runtime.createWithPythonSemanticVerifier(mockPlan("Przygotuj raport"), {
      original_nl: "Website agreement for Landing page.",
      approved_dsl: {
        version: "intent-contract.dsl.v1",
        document: {
          id: "doc-1",
          title: {
            field: "document.title",
            status: "CONFIRMED",
            value: "Website agreement",
            requiredForCompletion: true,
            approvedBy: [],
            source: { id: "m1", quote: "Website agreement" }
          }
        },
        deliverables: [
          {
            id: "del-1",
            description: {
              field: "deliverables.del-1.description",
              status: "CONFIRMED",
              value: "Landing page",
              requiredForCompletion: true,
              approvedBy: [],
              source: { id: "m1", quote: "Landing page" }
            }
          }
        ],
        acceptanceCriteria: [
          {
            id: "acc-1",
            description: {
              field: "acceptanceCriteria.acc-1.description",
              status: "CONFIRMED",
              value: "Loads in under two seconds",
              requiredForCompletion: true,
              approvedBy: [],
              source: { id: "m1", quote: "Loads in under two seconds" }
            }
          }
        ],
        conflicts: []
      },
      rendered_document: "# Website agreement\nLanding page\n",
      codegen_verifier_input: {
        generatedFiles: [{ path: "src/contract-spec.mjs", sha256: "a".repeat(64) }],
        testResults: [{ name: "generated tests", passed: false }]
      }
    });

    expect(session.state).toBe("VERIFICATION_FAILED");
    expect(session.audit.verifier).toMatchObject({
      verdict: "FAIL",
      code_mismatches: ["generated tests"]
    });
    await expect(runtime.execute(session)).rejects.toThrow(/not ready/);
  });
});
