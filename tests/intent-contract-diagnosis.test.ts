import { describe, expect, it } from "vitest";
import {
  createField,
  diagnoseIntentContractDsl,
  questionsForParty,
  type IntentContractDsl,
  type SourceReference
} from "../packages/intent-contract-model/src/index.js";

const human1Source: SourceReference = {
  type: "message",
  id: "m1",
  speaker: "Human1",
  path: "chat.txt",
  span: { start: 0, end: 10 }
};

const human2Source: SourceReference = {
  type: "message",
  id: "m2",
  speaker: "Human2",
  path: "chat.txt",
  span: { start: 11, end: 20 }
};

function baseDsl(): IntentContractDsl {
  return {
    version: "intent-contract.dsl.v1",
    document: {
      id: "doc-1",
      type: createField("document.type", "SERVICE_AGREEMENT", "CONFIRMED", true, human1Source),
      title: createField("document.title", "Umowa", "CONFIRMED", true, human1Source),
      language: createField("document.language", "pl", "CONFIRMED", false)
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
    sourceReferences: [human1Source, human2Source],
    render: [],
    execution: []
  };
}

describe("Phase 3 - missing, ambiguous, and conflicting information model", () => {
  it("reports a fully sourced, resolved DSL as ready for finalization", () => {
    const diagnosis = diagnoseIntentContractDsl(baseDsl());
    expect(diagnosis.finalizationReady).toBe(true);
    expect(diagnosis.blockingReasons).toEqual([]);
    expect(diagnosis.generatedQuestions).toEqual([]);
    expect(diagnosis.completenessGaps).toEqual([]);
    expect(diagnosis.traceabilityGaps).toEqual([]);
  });

  it("detects a missing required field and generates a question without guessing a value", () => {
    const dsl = baseDsl();
    dsl.payments.push({
      id: "pay-1",
      payerPartyId: createField("payment.payerPartyId", "human1", "CONFIRMED", true, human1Source),
      payeePartyId: createField("payment.payeePartyId", "human2", "CONFIRMED", true, human1Source),
      total: createField<{ amount: number; currency: string }>(
        "payment.total",
        null,
        "MISSING",
        true
      )
    });
    const diagnosis = diagnoseIntentContractDsl(dsl);
    expect(diagnosis.finalizationReady).toBe(false);
    expect(diagnosis.completenessGaps).toEqual([
      { path: "payments[0].total", field: "payment.total", status: "MISSING" }
    ]);
    const question = diagnosis.generatedQuestions.find((q) => q.field === "payment.total");
    expect(question?.reason).toBe("MISSING");
    // The generated question asks for the value; it never invents one.
    expect(question?.prompt).toContain("Provide a value");
    // No source speaker on the missing field, so routing is unknown.
    expect(question?.targetParties).toEqual(["unknown"]);
  });

  it("marks an ambiguous field with competing interpretations and a clarifying question", () => {
    const dsl = baseDsl();
    dsl.deadlines.push({
      id: "d-1",
      forId: createField("deadline.forId", "deliverable-1", "CONFIRMED", true, human1Source),
      dueAt: {
        ...createField("deadline.dueAt", null, "AMBIGUOUS", true, human1Source),
        interpretations: ["2026-01-01", "2026-02-01"]
      }
    });
    const diagnosis = diagnoseIntentContractDsl(dsl);
    expect(diagnosis.finalizationReady).toBe(false);
    expect(diagnosis.ambiguities).toEqual([
      {
        path: "deadlines[0].dueAt",
        field: "deadline.dueAt",
        interpretations: ["2026-01-01", "2026-02-01"]
      }
    ]);
    const question = diagnosis.generatedQuestions.find((q) => q.field === "deadline.dueAt");
    expect(question?.reason).toBe("AMBIGUOUS");
    expect(question?.interpretations).toEqual(["2026-01-01", "2026-02-01"]);
    expect(question?.prompt).toContain("2026-01-01 | 2026-02-01");
    // The ambiguous value came from Human1, so Human1 is asked to clarify.
    expect(question?.targetParties).toEqual(["Human1"]);
  });

  it("represents Human1/Human2 conflicting values with sources and blocks finalization", () => {
    const dsl = baseDsl();
    dsl.conflicts.push({
      id: "c-1",
      field: "payment.total",
      description: createField(
        "conflict.description",
        "Human1 and Human2 disagree on the total",
        "CONFIRMED",
        true,
        human1Source
      ),
      sourceIds: ["m1", "m2"],
      values: [
        { partyId: "human1", value: { amount: 100, currency: "PLN" }, source: human1Source },
        { partyId: "human2", value: { amount: 150, currency: "PLN" }, source: human2Source }
      ]
    });
    const diagnosis = diagnoseIntentContractDsl(dsl);
    expect(diagnosis.finalizationReady).toBe(false);
    const conflict = diagnosis.conflicts.find((c) => c.path === "conflicts[0]");
    expect(conflict?.field).toBe("payment.total");
    expect(conflict?.sourceIds).toEqual(["m1", "m2"]);
    expect(conflict?.values).toHaveLength(2);
    expect(conflict?.values.map((v) => v.partyId)).toEqual(["human1", "human2"]);
    const question = diagnosis.generatedQuestions.find((q) => q.path === "conflicts[0]");
    expect(question?.reason).toBe("CONFLICTING");
    // Both parties introduced competing values, so the conflict routes to both.
    expect(question?.targetParties).toEqual(["Human1", "Human2"]);
  });

  it("requires explicit approval for assumed values and clears once approved", () => {
    const dsl = baseDsl();
    dsl.assumptions.push({
      id: "a-1",
      description: {
        ...createField(
          "assumption.description",
          "Remote work assumed",
          "ASSUMED",
          false,
          human1Source
        ),
        approvedBy: []
      }
    });
    const unapproved = diagnoseIntentContractDsl(dsl);
    expect(unapproved.finalizationReady).toBe(false);
    expect(unapproved.unapprovedAssumptions).toEqual([
      {
        path: "assumptions[0].description",
        field: "assumption.description",
        value: "Remote work assumed"
      }
    ]);
    expect(unapproved.generatedQuestions.some((q) => q.reason === "UNAPPROVED_ASSUMPTION")).toBe(
      true
    );

    dsl.assumptions[0]!.description.approvedBy = ["Human1"];
    const approved = diagnoseIntentContractDsl(dsl);
    expect(approved.unapprovedAssumptions).toEqual([]);
    expect(approved.finalizationReady).toBe(true);
  });

  it("routes generated questions to the party that must answer", () => {
    const dsl = baseDsl();
    // Human1-sourced ambiguous field.
    dsl.deadlines.push({
      id: "d-1",
      forId: createField("deadline.forId", "deliverable-1", "CONFIRMED", true, human1Source),
      dueAt: {
        ...createField("deadline.dueAt", null, "AMBIGUOUS", true, human1Source),
        interpretations: ["a", "b"]
      }
    });
    // Human2-sourced missing required field.
    dsl.deliverables.push({
      id: "del-1",
      description: createField<string>(
        "deliverable.description",
        null,
        "MISSING",
        true,
        human2Source
      ),
      ownerPartyId: createField(
        "deliverable.ownerPartyId",
        "human2",
        "CONFIRMED",
        true,
        human2Source
      )
    });
    const diagnosis = diagnoseIntentContractDsl(dsl);
    const human1Questions = questionsForParty(diagnosis, "Human1");
    const human2Questions = questionsForParty(diagnosis, "Human2");
    expect(human1Questions.map((q) => q.field)).toContain("deadline.dueAt");
    expect(human1Questions.map((q) => q.field)).not.toContain("deliverable.description");
    expect(human2Questions.map((q) => q.field)).toContain("deliverable.description");
    expect(human2Questions.map((q) => q.field)).not.toContain("deadline.dueAt");
  });

  it("flags a material value without a source reference as a traceability gap", () => {
    const dsl = baseDsl();
    dsl.document.type.source = null;
    const diagnosis = diagnoseIntentContractDsl(dsl);
    expect(diagnosis.finalizationReady).toBe(false);
    expect(diagnosis.traceabilityGaps).toEqual([{ path: "document.type", field: "document.type" }]);
    expect(diagnosis.blockingReasons.some((r) => r.includes("without a source reference"))).toBe(
      true
    );
  });
});
