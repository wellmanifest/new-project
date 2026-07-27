import { readFile } from "node:fs/promises";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { parseTaskDsl } from "../packages/dsl-model/src/index.js";
import { mockPlan } from "../packages/llm-planner/src/index.js";
import {
  canonicalizeIntentContractDsl,
  createField,
  hashIntentContractDsl,
  officeDslToIntentContractDsl,
  parseIntentContractDsl,
  validateIntentContractDsl,
  type IntentContractDsl
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

  it("migrates Office DSL into a valid Intent/Contract snapshot", async () => {
    const officeDsl = parseTaskDsl(
      await readFile("examples/01-read-only-report/expected/dsl.json", "utf8")
    );
    const migrated = officeDslToIntentContractDsl(officeDsl);
    expect(validateIntentContractDsl(migrated.dsl).ok).toBe(true);
    expect(migrated.dsl.document.type.value).toBe("OFFICE_COMMAND");
    expect(migrated.dsl.contract).toBeNull();
    expect(migrated.dsl.intents[0]?.description.value).toBe(officeDsl.task.input);
    expect(migrated.dsl.obligations).toHaveLength(officeDsl.steps.length);
    expect(migrated.dsl.acceptanceCriteria).toHaveLength(officeDsl.expectedResults.length);
    expect(migrated.notes.some((note) => note.decision === "assumed")).toBe(true);
  });

  it("migrates Office DSL clarification steps into missing canonical questions", async () => {
    const officeDsl = parseTaskDsl(
      await readFile("examples/02-clarification/expected/dsl.json", "utf8")
    );
    const migrated = officeDslToIntentContractDsl(officeDsl);
    expect(migrated.dsl.questions).toHaveLength(1);
    expect(migrated.dsl.questions[0]?.prompt.status).toBe("MISSING");
    expect(migrated.dsl.questions[0]?.targetPartyId.value).toBe("human1");
    expect(migrated.notes.map((note) => note.toPath)).toContain("questions[0].prompt");
  });

  it("hashes migrated Office DSL snapshots deterministically", async () => {
    const officeDsl = parseTaskDsl(
      await readFile("examples/03-email-drafts/expected/dsl.json", "utf8")
    );
    const first = officeDslToIntentContractDsl(officeDsl).dsl;
    const second = officeDslToIntentContractDsl(JSON.parse(JSON.stringify(officeDsl))).dsl;
    expect(canonicalizeIntentContractDsl(first)).toBe(canonicalizeIntentContractDsl(second));
    expect(hashIntentContractDsl(first)).toBe(hashIntentContractDsl(second));
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

  describe("field status semantics", () => {
    function minimalDsl(): IntentContractDsl {
      return {
        version: "intent-contract.dsl.v1",
        document: {
          id: "doc-1",
          type: createField("document.type", "OFFICE_COMMAND", "CONFIRMED", true),
          title: createField("document.title", "T", "CONFIRMED", true),
          language: createField("document.language", "en", "CONFIRMED", false)
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
    }

    it("rejects confirmed fields without a value", () => {
      const dsl = minimalDsl();
      dsl.document.title.value = null;
      const result = validateIntentContractDsl(dsl);
      expect(result.ok).toBe(false);
      expect(result.issues.map((issue) => issue.path)).toContain("document.title.value");
    });

    it("requires missing, ambiguous, and conflicting fields to block completion", () => {
      const dsl = minimalDsl();
      for (const status of ["MISSING", "AMBIGUOUS", "CONFLICTING"] as const) {
        dsl.document.title.status = status;
        dsl.document.title.value = null;
        dsl.document.title.requiredForCompletion = false;
        const result = validateIntentContractDsl(dsl);
        expect(result.ok).toBe(false);
        expect(result.issues.map((issue) => issue.path)).toContain(
          "document.title.requiredForCompletion"
        );
      }
    });

    it("accepts incomplete, assumed, rejected, and not-applicable fields", () => {
      const dsl = minimalDsl();
      for (const status of ["INCOMPLETE", "ASSUMED", "REJECTED", "NOT_APPLICABLE"] as const) {
        dsl.document.title.status = status;
        dsl.document.title.value = null;
        dsl.document.title.requiredForCompletion = false;
        expect(validateIntentContractDsl(dsl).ok).toBe(true);
      }
    });

    it("rejects unknown field statuses and malformed formal fields", () => {
      const dsl = minimalDsl();
      dsl.document.title.status = "UNKNOWN" as never;
      const badStatus = validateIntentContractDsl(dsl);
      expect(badStatus.ok).toBe(false);
      expect(badStatus.issues.map((issue) => issue.path)).toContain("document.title.status");

      const missingField = minimalDsl();
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (missingField.document.title as any).field = undefined;
      const noField = validateIntentContractDsl(missingField);
      expect(noField.ok).toBe(false);
      expect(noField.issues.map((issue) => issue.path)).toContain("document.title.field");
    });
  });

  it("parses and throws on invalid intent/contract DSL", () => {
    expect(() => parseIntentContractDsl("not json")).toThrow();
    expect(() => parseIntentContractDsl("{}")).toThrow();
  });

  it("migrates an office.dsl.v1 plan into a valid intent-contract DSL", () => {
    const office = mockPlan("Przygotuj raport");
    const migrated = officeDslToIntentContractDsl(office);
    expect(migrated.dsl.version).toBe("intent-contract.dsl.v1");
    expect(migrated.dsl.document.type.value).toBe("OFFICE_COMMAND");
    expect(migrated.notes.length).toBeGreaterThan(0);
    expect(validateIntentContractDsl(migrated.dsl).ok).toBe(true);
  });

  it("canonicalizes nested key order deterministically", () => {
    const dsl = minimalDslFromIntentContractFixture();
    const reorderedField = JSON.parse(
      JSON.stringify({
        value: dsl.document.title.value,
        status: dsl.document.title.status,
        source: dsl.document.title.source,
        approvedBy: dsl.document.title.approvedBy,
        field: dsl.document.title.field,
        requiredForCompletion: dsl.document.title.requiredForCompletion
      })
    );
    const reordered = JSON.parse(JSON.stringify(dsl));
    reordered.document.title = reorderedField;
    expect(canonicalizeIntentContractDsl(reordered)).toBe(canonicalizeIntentContractDsl(dsl));
    expect(hashIntentContractDsl(reordered)).toBe(hashIntentContractDsl(dsl));
  });

  function minimalDslFromIntentContractFixture(): IntentContractDsl {
    return {
      version: "intent-contract.dsl.v1",
      document: {
        id: "d",
        type: createField("document.type", "SERVICE_AGREEMENT", "CONFIRMED", true),
        title: createField("document.title", "T", "ASSUMED", false),
        language: createField("document.language", "pl", "CONFIRMED", true)
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
  }
});
