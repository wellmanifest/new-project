import { readFile } from "node:fs/promises";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { parseIntentContractDsl } from "../packages/intent-contract-model/src/index.js";
import {
  DRAFT_DISCLAIMER,
  renderDocument,
  renderEmploymentAgreement,
  renderServiceAgreement,
  renderTaskDelegation,
  type RenderedDocument
} from "../packages/document-renderer/src/index.js";

const modelFixtures = path.join(process.cwd(), "packages", "intent-contract-model", "fixtures");
const rendererFixtures = path.join(process.cwd(), "packages", "document-renderer", "fixtures");

async function loadDsl(dir: string, file: string) {
  return parseIntentContractDsl(await readFile(path.join(dir, file), "utf8"));
}

function traceabilityPaths(doc: RenderedDocument): string[] {
  return doc.traceability.flatMap((entry) => entry.dslPaths);
}

describe("document renderers", () => {
  it("prepends the draft disclaimer to every document", async () => {
    const service = await loadDsl(modelFixtures, "service-agreement.intent-contract.json");
    const delegation = await loadDsl(rendererFixtures, "task-delegation.intent-contract.json");
    const employment = await loadDsl(rendererFixtures, "employment-agreement.intent-contract.json");
    for (const doc of [
      renderServiceAgreement(service),
      renderTaskDelegation(delegation),
      renderEmploymentAgreement(employment)
    ]) {
      expect(doc.markdown).toContain(DRAFT_DISCLAIMER);
      expect(doc.markdown).toMatch(/does not add, infer, or invent/i);
    }
  });

  describe("task delegation renderer", () => {
    it("renders assignee, deliverable, deadline, dependencies, and exclusions from DSL only", async () => {
      const dsl = await loadDsl(rendererFixtures, "task-delegation.intent-contract.json");
      const doc = renderTaskDelegation(dsl);
      expect(doc.documentType).toBe("TASK_DELEGATION");
      expect(doc.markdown).toContain("**Assignee:** Ania");
      expect(doc.markdown).toContain("**Delegator:** Human1");
      expect(doc.markdown).toContain("Quarterly report document in PDF.");
      expect(doc.markdown).toContain("2026-09-30");
      expect(doc.markdown).toContain("Requester must provide the source sales data.");
      expect(doc.markdown).toContain("Graphic design of the report is out of scope.");
    });

    it("reports a missing acceptance criterion as an explicit gap and never invents it", async () => {
      const dsl = await loadDsl(rendererFixtures, "task-delegation.intent-contract.json");
      const doc = renderTaskDelegation(dsl);
      expect(doc.gaps).toContain("acceptanceCriteria.acceptance-report.description is MISSING");
      expect(doc.markdown).toContain(
        "[GAP: acceptanceCriteria.acceptance-report.description is MISSING]"
      );
    });
  });

  describe("service agreement renderer", () => {
    it("renders parties, scope, and exclusions and marks missing payment/acceptance as gaps", async () => {
      const dsl = await loadDsl(modelFixtures, "service-agreement.intent-contract.json");
      const doc = renderServiceAgreement(dsl);
      expect(doc.documentType).toBe("SERVICE_AGREEMENT");
      expect(doc.markdown).toContain("Adam");
      expect(doc.markdown).toContain("Hosting is not included unless confirmed.");
      expect(doc.gaps).toContain("payments.payment-website.total is MISSING");
      expect(doc.gaps).toContain("acceptanceCriteria.acceptance-website.description is MISSING");
      expect(doc.gaps).toContain("contract.governingLaw is MISSING");
    });

    it("flags assumed unapproved values instead of presenting them as confirmed", async () => {
      const dsl = await loadDsl(modelFixtures, "service-agreement.intent-contract.json");
      const doc = renderServiceAgreement(dsl);
      expect(doc.assumptions.length).toBeGreaterThan(0);
      expect(doc.markdown).toMatch(/ASSUMED - needs approval/);
    });
  });

  describe("employment agreement renderer", () => {
    it("renders employer, employee, remuneration, and guidelines without unsupported fields", async () => {
      const dsl = await loadDsl(rendererFixtures, "employment-agreement.intent-contract.json");
      const doc = renderEmploymentAgreement(dsl);
      expect(doc.documentType).toBe("EMPLOYMENT_AGREEMENT");
      expect(doc.markdown).toContain("**Employer:** Acme Sp. z o.o.");
      expect(doc.markdown).toContain("**Employee:** Jan Kowalski");
      expect(doc.markdown).toContain("12000 PLN");
      expect(doc.markdown).toContain("Employee follows the code review and security guidelines.");
      expect(doc.markdown).toContain("Three-month probation period applies.");
      // The model has no deliverables for this input; renderer must not invent any.
      expect(doc.markdown).not.toContain("deliverable");
      expect(doc.gaps.length).toBe(0);
    });
  });

  describe("document-to-DSL traceability map", () => {
    it("maps every rendered field to DSL paths and source references", async () => {
      const dsl = await loadDsl(rendererFixtures, "task-delegation.intent-contract.json");
      const doc = renderTaskDelegation(dsl);
      expect(doc.markdown).toContain("## Traceability Map");
      const paths = traceabilityPaths(doc);
      expect(paths).toContain("deliverables.deliverable-report.description");
      expect(paths).toContain("deadlines.deadline-report.dueAt");
      const sourceIds = doc.traceability.flatMap((entry) => entry.sourceIds);
      expect(sourceIds).toContain("message-1");
      expect(sourceIds).toContain("message-2");
    });

    it("records a traceability entry for every rendered paragraph", async () => {
      const dsl = await loadDsl(rendererFixtures, "employment-agreement.intent-contract.json");
      const doc = renderEmploymentAgreement(dsl);
      for (const entry of doc.traceability) {
        expect(entry.section).toBeTruthy();
        expect(entry.label).toBeTruthy();
      }
    });
  });

  describe("renderDocument dispatch", () => {
    it("dispatches by document type and falls back to service agreement", async () => {
      const delegation = await loadDsl(rendererFixtures, "task-delegation.intent-contract.json");
      const employment = await loadDsl(
        rendererFixtures,
        "employment-agreement.intent-contract.json"
      );
      const service = await loadDsl(modelFixtures, "service-agreement.intent-contract.json");
      expect(renderDocument(delegation).documentType).toBe("TASK_DELEGATION");
      expect(renderDocument(employment).documentType).toBe("EMPLOYMENT_AGREEMENT");
      expect(renderDocument(service).documentType).toBe("SERVICE_AGREEMENT");
    });
  });
});
