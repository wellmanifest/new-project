import { readFile } from "node:fs/promises";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { parseIntentContractDsl } from "../packages/intent-contract-model/src/index.js";
import {
  TEST_GENERATION_CATEGORIES,
  extractTestGenerationInput,
  generateTestSuite,
  generateUnitTestSpecs,
  parseTestGenerationInput,
  renderTestPlanMarkdown,
  validateTestGenerationInput,
  verifyTestCoverage,
  type TestGenerationInput,
  type TestKind
} from "../packages/testgen/src/index.js";

const testgenFixtures = path.join(process.cwd(), "packages", "testgen", "fixtures");
const modelFixtures = path.join(process.cwd(), "packages", "intent-contract-model", "fixtures");

async function loadInput(): Promise<TestGenerationInput> {
  return parseTestGenerationInput(
    await readFile(path.join(testgenFixtures, "testgen-input.json"), "utf8")
  );
}

describe("test-generation DSL inputs", () => {
  it("validates a well-formed input with all seven categories", async () => {
    const input = await loadInput();
    expect(validateTestGenerationInput(input).ok).toBe(true);
    const categories = new Set(input.items.map((item) => item.category));
    for (const category of TEST_GENERATION_CATEGORIES) {
      expect(categories.has(category)).toBe(true);
    }
  });

  it("rejects unknown categories, duplicate ids, and empty text", () => {
    const bad = {
      version: "intent-contract.testgen-input.v1",
      dslHash: null,
      items: [
        { id: "a", category: "REQUIREMENT", text: "ok", sourceDslPaths: [], sourceIds: [] },
        { id: "a", category: "NONSENSE", text: "", sourceDslPaths: [], sourceIds: [] }
      ]
    };
    const result = validateTestGenerationInput(bad);
    expect(result.ok).toBe(false);
    const paths = result.issues.map((issue) => issue.path);
    expect(paths).toContain("items[1].id");
    expect(paths).toContain("items[1].category");
    expect(paths).toContain("items[1].text");
  });

  it("extracts inputs deterministically from an Intent/Contract DSL snapshot", async () => {
    const dsl = parseIntentContractDsl(
      await readFile(path.join(modelFixtures, "service-agreement.intent-contract.json"), "utf8")
    );
    const input = extractTestGenerationInput(dsl);
    expect(validateTestGenerationInput(input).ok).toBe(true);
    expect(input.dslHash).toHaveLength(64);
    const categories = new Set(input.items.map((item) => item.category));
    // The service-agreement fixture has intents/obligations, deliverables,
    // exclusions, and risks, so these categories must be present.
    expect(categories.has("REQUIREMENT")).toBe(true);
    expect(categories.has("EXPECTED_OUTPUT")).toBe(true);
    expect(categories.has("PROHIBITED_BEHAVIOR")).toBe(true);
    expect(categories.has("ERROR_HANDLING")).toBe(true);
    // Every extracted item is traceable to a DSL path.
    for (const item of input.items) {
      expect(item.sourceDslPaths.length).toBeGreaterThan(0);
    }
    // Re-extraction is deterministic.
    const again = extractTestGenerationInput(dsl);
    expect(JSON.stringify(again)).toBe(JSON.stringify(input));
  });
});

describe("unit test spec generation", () => {
  it("maps every acceptance criterion to a unit test spec", async () => {
    const input = await loadInput();
    const acceptanceIds = input.items
      .filter((item) => item.category === "ACCEPTANCE_CRITERIA")
      .map((item) => item.id);
    const unit = generateUnitTestSpecs(input);
    for (const acceptanceId of acceptanceIds) {
      const spec = unit.find((current) => current.mapsToItemIds.includes(acceptanceId));
      expect(spec).toBeDefined();
      expect(spec?.kind).toBe("unit");
      expect(spec?.dslPaths.length).toBeGreaterThan(0);
    }
  });
});

describe("integration/API/E2E/security/error-handling spec generation", () => {
  it("produces each applicable kind from the fixture inputs", async () => {
    const input = await loadInput();
    const suite = generateTestSuite(input);
    const kinds = new Set<TestKind>(suite.map((spec) => spec.kind));
    for (const kind of [
      "unit",
      "integration",
      "api",
      "e2e",
      "security",
      "error-handling"
    ] as const) {
      expect(kinds.has(kind)).toBe(true);
    }
    const security = suite.filter((spec) => spec.kind === "security");
    expect(security.some((spec) => spec.mapsToItemIds.includes("sec-no-secret-exfil"))).toBe(true);
    const errors = suite.filter((spec) => spec.kind === "error-handling");
    expect(errors.some((spec) => spec.mapsToItemIds.includes("err-payment-missing"))).toBe(true);
  });
});

describe("coverage verification against acceptance criteria", () => {
  it("reports full acceptance coverage for the generated suite", async () => {
    const input = await loadInput();
    const suite = generateTestSuite(input);
    const coverage = verifyTestCoverage(input, suite);
    expect(coverage.acceptanceCriteriaCovered).toBe(true);
    expect(coverage.uncoveredAcceptanceCriteria).toHaveLength(0);
    expect(coverage.coverageRatio).toBe(1);
  });

  it("surfaces uncovered acceptance criteria in the verifier output", async () => {
    const input = await loadInput();
    // Drop specs that cover one acceptance criterion to simulate a gap.
    const partial = generateTestSuite(input).filter(
      (spec) => !spec.mapsToItemIds.includes("acc-responsive")
    );
    const coverage = verifyTestCoverage(input, partial);
    expect(coverage.acceptanceCriteriaCovered).toBe(false);
    expect(coverage.uncoveredAcceptanceCriteria.map((item) => item.id)).toContain("acc-responsive");
    expect(coverage.verifierInput.uncoveredAcceptanceCriteriaIds).toContain("acc-responsive");
    expect(coverage.verifierInput.uncoveredItemIds).toContain("acc-responsive");
  });

  it("renders a traceable Markdown test plan", async () => {
    const input = await loadInput();
    const suite = generateTestSuite(input);
    const coverage = verifyTestCoverage(input, suite);
    const markdown = renderTestPlanMarkdown(input, suite, coverage);
    expect(markdown).toContain("# Generated Test Plan (Draft)");
    expect(markdown).toContain("## Coverage");
    expect(markdown).toContain("acceptanceCriteria.acceptance-form.description");
  });
});
