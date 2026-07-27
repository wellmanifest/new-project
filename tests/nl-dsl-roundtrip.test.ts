import { describe, expect, it } from "vitest";
import {
  CONTROLLED_PLANNER_SCHEMA,
  buildOpenRouterIntentContractPrompt,
  extractRenderedStatementPaths,
  intentContractDslFromPlannerResponse,
  mockPlanGuidelineFileToIntentContractDsl,
  mockPlanIntentContractFromNaturalLanguage,
  parseControlledPlannerResponse,
  renderIntentContractDslToNaturalLanguage,
  validateControlledPlannerResponse,
  type ControlledPlannerResponse
} from "../packages/llm-planner/src/index.js";
import {
  collectFormalFields,
  hashIntentContractDsl,
  validateIntentContractDsl
} from "../packages/intent-contract-model/src/index.js";

describe("Phase 5 bidirectional NL <-> DSL", () => {
  it("defines controlled OpenRouter prompts and rejects malformed structured output", () => {
    const prompt = buildOpenRouterIntentContractPrompt("message");

    expect(prompt.schema).toBe(CONTROLLED_PLANNER_SCHEMA);
    expect(prompt.system).toContain("Return only JSON");
    expect(prompt.system).toContain("Do not invent");

    const malformed: ControlledPlannerResponse = {
      version: "intent-contract.planner-response.v1",
      documentId: "bad:document",
      contractId: "bad:contract",
      sources: [{ id: "source-1", kind: "message", quote: "Build a site." }],
      fields: [
        {
          path: "payments.primary.total",
          value: { amount: "1200", currency: "PLN" },
          status: "CONFIRMED",
          requiredForCompletion: true,
          sourceId: "missing-source"
        }
      ]
    } as unknown as ControlledPlannerResponse;

    const validation = validateControlledPlannerResponse(malformed);
    expect(validation.ok).toBe(false);
    expect(validation.issues.map((issue) => issue.path)).toEqual(
      expect.arrayContaining(["fields[0].sourceId", "fields[0].value"])
    );
    expect(() => parseControlledPlannerResponse(JSON.stringify(malformed))).toThrow(
      /unknown source id|payment must/
    );
  });

  it("converts valid controlled planner output into canonical Intent/Contract DSL", () => {
    const response: ControlledPlannerResponse = {
      version: "intent-contract.planner-response.v1",
      documentId: "manual:document",
      contractId: "manual:contract",
      sources: [
        { id: "msg-1", kind: "message", quote: "Scope: Build dashboard. Payment 9000 PLN." }
      ],
      fields: [
        {
          path: "document.type",
          value: "SERVICE_AGREEMENT",
          status: "CONFIRMED",
          requiredForCompletion: true,
          sourceId: "msg-1"
        },
        {
          path: "subjects.scope.description",
          value: "Build dashboard",
          status: "CONFIRMED",
          requiredForCompletion: true,
          sourceId: "msg-1"
        },
        {
          path: "deliverables.primary.description",
          value: "Dashboard",
          status: "CONFIRMED",
          requiredForCompletion: true,
          sourceId: "msg-1"
        },
        {
          path: "payments.primary.total",
          value: { amount: 9000, currency: "PLN" },
          status: "CONFIRMED",
          requiredForCompletion: true,
          sourceId: "msg-1"
        }
      ]
    };

    const dsl = intentContractDslFromPlannerResponse(response);

    expect(validateIntentContractDsl(dsl).ok).toBe(true);
    expect(dsl.document.type.value).toBe("SERVICE_AGREEMENT");
    expect(dsl.payments[0]?.total.value).toEqual({ amount: 9000, currency: "PLN" });
    expect(dsl.payments[0]?.total.source?.id).toBe("msg-1");
    expect(dsl.contract?.governingLaw.status).toBe("MISSING");
  });

  it("plans varied single-message natural language into sourced DSL without office action matching", () => {
    const dsl = mockPlanIntentContractFromNaturalLanguage(
      "Client: Marta Ziel. Provider: Jan Kowal. Scope: build a client portal. Deliverable: working portal. Payment 12000 PLN. Deadline 2026-10-01. Acceptance: login and export work. Exclusion: no paid ads.",
      { id: "portal-message" }
    );

    expect(validateIntentContractDsl(dsl).ok).toBe(true);
    expect(dsl.document.type.value).toBe("SERVICE_AGREEMENT");
    expect(dsl.parties[0]?.name.value).toBe("Marta Ziel");
    expect(dsl.parties[1]?.name.value).toBe("Jan Kowal");
    expect(dsl.subjects[0]?.description.value).toBe("build a client portal");
    expect(dsl.deliverables[0]?.description.source?.id).toBe("message-1");
    expect(dsl.deadlines[0]?.dueAt.value).toBe("2026-10-01");
    expect(dsl.exclusions[0]?.description.value).toBe("no paid ads");
  });

  it("plans guideline-file text with missing fields and file source references", () => {
    const dsl = mockPlanGuidelineFileToIntentContractDsl(
      "Guideline: employment onboarding. Scope: prepare employment agreement template. Deliverable: candidate onboarding checklist. Acceptance: HR can verify required documents.",
      { id: "employment-guidelines", sourcePath: "guidelines/employment.md" }
    );

    expect(validateIntentContractDsl(dsl).ok).toBe(true);
    expect(dsl.document.type.value).toBe("EMPLOYMENT_AGREEMENT");
    expect(dsl.subjects[0]?.description.source?.type).toBe("file");
    expect(dsl.subjects[0]?.description.source?.path).toBe("guidelines/employment.md");
    expect(dsl.contract?.governingLaw.status).toBe("MISSING");
    expect(dsl.questions.map((question) => question.field)).toContain("contract.governingLaw");
  });

  it("renders DSL to natural language statements mapped back to DSL fields", () => {
    const dsl = mockPlanIntentContractFromNaturalLanguage(
      "Scope: migrate reports. Deliverable: migration summary. Payment 5000 PLN. Deadline 2026-11-15. Acceptance: report opens.",
      { id: "render-message" }
    );
    const rendered = renderIntentContractDslToNaturalLanguage(dsl, hashIntentContractDsl(dsl));

    expect(rendered.version).toBe("intent-contract.nl-summary.v1");
    expect(rendered.dslHash).toHaveLength(64);
    expect(rendered.statements.length).toBeGreaterThan(5);
    expect(rendered.statements.every((statement) => statement.dslPath && statement.field)).toBe(
      true
    );
    expect(rendered.text).toContain("[payments[0].total]");
  });

  it("round-trips rendered NL without introducing unauthorized field paths", () => {
    const dsl = mockPlanIntentContractFromNaturalLanguage(
      "Scope: build analytics view. Deliverable: analytics screen. Payment 7000 PLN. Deadline 2026-12-20. Acceptance: charts load.",
      { id: "roundtrip-message" }
    );
    const rendered = renderIntentContractDslToNaturalLanguage(dsl, hashIntentContractDsl(dsl));
    const renderedPaths = new Set(extractRenderedStatementPaths(rendered.text));
    const originalValuedPaths = collectFormalFields(dsl)
      .filter(({ field }) => field.value !== null && field.status !== "NOT_APPLICABLE")
      .map(({ path }) => path);

    expect([...renderedPaths].sort()).toEqual([...originalValuedPaths].sort());
    expect(rendered.text).not.toMatch(/governing law: (?!null)/i);
  });
});
