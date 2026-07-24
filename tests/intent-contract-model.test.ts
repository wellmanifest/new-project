import { readFile } from "node:fs/promises";
import path from "node:path";
import { describe, expect, it } from "vitest";
import {
  canonicalizeIntentContractDsl,
  hashIntentContractDsl,
  parseIntentContractDsl,
  validateIntentContractDsl
} from "../packages/intent-contract-model/src/index.js";

const fixturePath = path.join(
  process.cwd(),
  "packages",
  "intent-contract-model",
  "fixtures",
  "service-agreement.intent-contract.json"
);

describe("Intent/Contract DSL model", () => {
  it("parses and validates the canonical fixture", async () => {
    const dsl = parseIntentContractDsl(await readFile(fixturePath, "utf8"));
    const result = validateIntentContractDsl(dsl);
    expect(result.ok).toBe(true);
    expect(dsl.version).toBe("intent-contract.dsl.v1");
    expect(dsl.document.type.status).toBe("CONFIRMED");
    expect(dsl.deadlines[0]?.dueAt.status).toBe("MISSING");
    expect(dsl.payments[0]?.total.requiredForCompletion).toBe(true);
  });

  it("rejects confirmed fields without values", async () => {
    const dsl = parseIntentContractDsl(await readFile(fixturePath, "utf8"));
    dsl.document.title.status = "CONFIRMED";
    dsl.document.title.value = null;
    const result = validateIntentContractDsl(dsl);
    expect(result.ok).toBe(false);
    expect(result.issues.map((issue) => issue.path)).toContain("document.title.value");
  });

  it("rejects unresolved required fields that are not completion-blocking", async () => {
    const dsl = parseIntentContractDsl(await readFile(fixturePath, "utf8"));
    dsl.deadlines[0]!.dueAt.requiredForCompletion = false;
    const result = validateIntentContractDsl(dsl);
    expect(result.ok).toBe(false);
    expect(result.issues.map((issue) => issue.path)).toContain(
      "deadlines[0].dueAt.requiredForCompletion"
    );
  });

  it("requires an explicit contract object or null boundary", async () => {
    const dsl = parseIntentContractDsl(await readFile(fixturePath, "utf8"));
    const withoutContract = { ...dsl } as Record<string, unknown>;
    delete withoutContract.contract;
    const result = validateIntentContractDsl(withoutContract);
    expect(result.ok).toBe(false);
    expect(result.issues.map((issue) => issue.path)).toContain("contract");
  });

  it("canonicalizes and hashes equivalent objects deterministically", async () => {
    const dsl = parseIntentContractDsl(await readFile(fixturePath, "utf8"));
    const reordered = JSON.parse(
      JSON.stringify({
        execution: dsl.execution,
        render: dsl.render,
        sourceReferences: dsl.sourceReferences,
        approvals: dsl.approvals,
        questions: dsl.questions,
        conflicts: dsl.conflicts,
        risks: dsl.risks,
        assumptions: dsl.assumptions,
        exclusions: dsl.exclusions,
        acceptanceCriteria: dsl.acceptanceCriteria,
        dependencies: dsl.dependencies,
        conditions: dsl.conditions,
        payments: dsl.payments,
        deadlines: dsl.deadlines,
        deliverables: dsl.deliverables,
        obligations: dsl.obligations,
        subjects: dsl.subjects,
        intents: dsl.intents,
        roles: dsl.roles,
        parties: dsl.parties,
        contract: dsl.contract,
        document: dsl.document,
        version: dsl.version
      })
    );
    expect(canonicalizeIntentContractDsl(reordered)).toBe(canonicalizeIntentContractDsl(dsl));
    expect(hashIntentContractDsl(reordered)).toBe(hashIntentContractDsl(dsl));
    expect(hashIntentContractDsl(dsl)).toHaveLength(64);
  });
});
