import {
  hashIntentContractDsl,
  validateIntentContractDsl,
  type FormalField,
  type IntentContractDsl
} from "@office-dsl/intent-contract-model";

export const TESTGEN_INPUT_VERSION = "intent-contract.testgen-input.v1";
export const TESTGEN_VERSION = "testgen.v1";

/**
 * Test-generation DSL input categories.
 *
 * These are the typed inputs the generator understands. They are either
 * authored directly or extracted deterministically from an
 * `intent-contract.dsl.v1` snapshot.
 */
export type TestGenerationCategory =
  | "REQUIREMENT"
  | "INVARIANT"
  | "ACCEPTANCE_CRITERIA"
  | "PROHIBITED_BEHAVIOR"
  | "EXPECTED_OUTPUT"
  | "ERROR_HANDLING"
  | "SECURITY_POLICY";

export const TEST_GENERATION_CATEGORIES: TestGenerationCategory[] = [
  "REQUIREMENT",
  "INVARIANT",
  "ACCEPTANCE_CRITERIA",
  "PROHIBITED_BEHAVIOR",
  "EXPECTED_OUTPUT",
  "ERROR_HANDLING",
  "SECURITY_POLICY"
];

export interface TestGenerationItem {
  id: string;
  category: TestGenerationCategory;
  text: string;
  sourceDslPaths: string[];
  sourceIds: string[];
}

export interface TestGenerationInput {
  version: typeof TESTGEN_INPUT_VERSION;
  dslHash: string | null;
  items: TestGenerationItem[];
}

export type TestKind = "unit" | "integration" | "api" | "e2e" | "security" | "error-handling";

export interface TestSpec {
  id: string;
  kind: TestKind;
  title: string;
  mapsToItemIds: string[];
  categories: TestGenerationCategory[];
  dslPaths: string[];
  given: string;
  when: string;
  then: string;
}

export interface TestGenerationVerifierInput {
  version: "testgen.verifier-input.v1";
  dslHash: string | null;
  specCount: number;
  specs: Array<{ id: string; kind: TestKind; mapsToItemIds: string[] }>;
  uncoveredItemIds: string[];
  uncoveredAcceptanceCriteriaIds: string[];
}

export interface TestCoverageReport {
  version: "testgen.coverage.v1";
  totalItems: number;
  coveredItemIds: string[];
  uncoveredItems: TestGenerationItem[];
  uncoveredAcceptanceCriteria: TestGenerationItem[];
  acceptanceCriteriaCovered: boolean;
  coverageRatio: number;
  verifierInput: TestGenerationVerifierInput;
}

export interface TestGenerationValidationIssue {
  path: string;
  message: string;
}

export interface TestGenerationValidationResult {
  ok: boolean;
  issues: TestGenerationValidationIssue[];
}

export class TestGenerationError extends Error {}

const categorySet = new Set<TestGenerationCategory>(TEST_GENERATION_CATEGORIES);

const SECURITY_KEYWORDS =
  /(secret|password|token|api[_ -]?key|shell|rm\s+-rf|injection|inject|unauthor|delete|traversal|escalat|exfiltrat)/i;

/**
 * Validate a test-generation input document. Ensures the version, unique
 * non-empty ids, known categories, non-empty text, and array-typed source
 * references.
 */
export function validateTestGenerationInput(value: unknown): TestGenerationValidationResult {
  const issues: TestGenerationValidationIssue[] = [];
  if (!value || typeof value !== "object") {
    return { ok: false, issues: [{ path: "$", message: "input must be an object" }] };
  }
  const root = value as Partial<TestGenerationInput>;
  if (root.version !== TESTGEN_INPUT_VERSION) {
    issues.push({ path: "version", message: `must be ${TESTGEN_INPUT_VERSION}` });
  }
  if (!("dslHash" in root) || (root.dslHash !== null && typeof root.dslHash !== "string")) {
    issues.push({ path: "dslHash", message: "must be a string or null" });
  }
  if (!Array.isArray(root.items)) {
    issues.push({ path: "items", message: "must be an array" });
    return { ok: issues.length === 0, issues };
  }
  const seen = new Set<string>();
  root.items.forEach((item, index) => {
    const base = `items[${index}]`;
    if (!item || typeof item !== "object") {
      issues.push({ path: base, message: "must be an object" });
      return;
    }
    const node = item as Partial<TestGenerationItem>;
    if (!node.id || typeof node.id !== "string") {
      issues.push({ path: `${base}.id`, message: "is required" });
    } else if (seen.has(node.id)) {
      issues.push({ path: `${base}.id`, message: `duplicate item id "${node.id}"` });
    } else {
      seen.add(node.id);
    }
    if (!categorySet.has(node.category as TestGenerationCategory)) {
      issues.push({ path: `${base}.category`, message: "unknown category" });
    }
    if (!node.text || typeof node.text !== "string" || !node.text.trim()) {
      issues.push({ path: `${base}.text`, message: "is required" });
    }
    if (!Array.isArray(node.sourceDslPaths)) {
      issues.push({ path: `${base}.sourceDslPaths`, message: "must be an array" });
    }
    if (!Array.isArray(node.sourceIds)) {
      issues.push({ path: `${base}.sourceIds`, message: "must be an array" });
    }
  });
  return { ok: issues.length === 0, issues };
}

export function parseTestGenerationInput(input: string): TestGenerationInput {
  const parsed = JSON.parse(input) as unknown;
  const result = validateTestGenerationInput(parsed);
  if (!result.ok) {
    throw new TestGenerationError(
      result.issues.map((issue) => `${issue.path}: ${issue.message}`).join("; ")
    );
  }
  return parsed as TestGenerationInput;
}

/**
 * Deterministically extract test-generation inputs from an Intent/Contract DSL
 * snapshot. Only valued fields are used; the extractor never invents inputs
 * that are absent from the DSL.
 */
export function extractTestGenerationInput(dsl: IntentContractDsl): TestGenerationInput {
  const validation = validateIntentContractDsl(dsl);
  if (!validation.ok) {
    throw new TestGenerationError(
      validation.issues.map((issue) => `${issue.path}: ${issue.message}`).join("; ")
    );
  }
  const items: TestGenerationItem[] = [];

  const add = (
    prefix: string,
    category: TestGenerationCategory,
    nodeId: string,
    field: FormalField<unknown>
  ): void => {
    if (field.value === null) return;
    items.push({
      id: `${prefix}-${nodeId}`,
      category,
      text: valueText(field),
      sourceDslPaths: [field.field],
      sourceIds: field.source?.id ? [field.source.id] : []
    });
  };

  for (const node of dsl.intents) add("req-int", "REQUIREMENT", node.id, node.description);
  for (const node of dsl.obligations) add("req-obl", "REQUIREMENT", node.id, node.description);
  for (const node of dsl.conditions) add("inv", "INVARIANT", node.id, node.description);
  for (const node of dsl.acceptanceCriteria)
    add("acc", "ACCEPTANCE_CRITERIA", node.id, node.description);
  for (const node of dsl.exclusions) add("proh", "PROHIBITED_BEHAVIOR", node.id, node.description);
  for (const node of dsl.deliverables) add("out", "EXPECTED_OUTPUT", node.id, node.description);
  for (const node of dsl.risks) add("err", "ERROR_HANDLING", node.id, node.description);

  // Security policies are derived from prohibited/risk statements that mention
  // security-sensitive behavior, plus any explicit DENY policy language.
  for (const node of [...dsl.exclusions, ...dsl.risks]) {
    const description = "description" in node ? node.description : null;
    if (
      description &&
      description.value !== null &&
      SECURITY_KEYWORDS.test(valueText(description))
    ) {
      items.push({
        id: `sec-${node.id}`,
        category: "SECURITY_POLICY",
        text: valueText(description),
        sourceDslPaths: [description.field],
        sourceIds: description.source?.id ? [description.source.id] : []
      });
    }
  }

  return {
    version: TESTGEN_INPUT_VERSION,
    dslHash: hashIntentContractDsl(dsl),
    items: dedupeById(items)
  };
}

function itemsByCategory(
  input: TestGenerationInput,
  category: TestGenerationCategory
): TestGenerationItem[] {
  return input.items.filter((item) => item.category === category);
}

/**
 * Generate unit test specifications. Every acceptance criterion maps to a unit
 * test; requirements, invariants, and expected outputs also produce unit specs.
 */
export function generateUnitTestSpecs(input: TestGenerationInput): TestSpec[] {
  const specs: TestSpec[] = [];
  for (const item of itemsByCategory(input, "ACCEPTANCE_CRITERIA")) {
    specs.push(
      spec("unit", `unit-${item.id}`, `Unit: satisfies acceptance criterion ${item.id}`, [item], {
        given: "the approved contract inputs are available",
        when: "the implementation runs the unit under test",
        then: `the acceptance criterion is met: ${item.text}`
      })
    );
  }
  for (const item of itemsByCategory(input, "REQUIREMENT")) {
    specs.push(
      spec("unit", `unit-${item.id}`, `Unit: fulfills requirement ${item.id}`, [item], {
        given: "the required inputs are provided",
        when: "the requirement behavior executes",
        then: `the requirement holds: ${item.text}`
      })
    );
  }
  for (const item of itemsByCategory(input, "INVARIANT")) {
    specs.push(
      spec("unit", `unit-${item.id}`, `Unit: maintains invariant ${item.id}`, [item], {
        given: "any valid state",
        when: "an operation is applied",
        then: `the invariant is preserved: ${item.text}`
      })
    );
  }
  for (const item of itemsByCategory(input, "EXPECTED_OUTPUT")) {
    specs.push(
      spec("unit", `unit-${item.id}`, `Unit: produces expected output ${item.id}`, [item], {
        given: "the inputs are provided",
        when: "the output is generated",
        then: `the expected output is produced: ${item.text}`
      })
    );
  }
  return specs;
}

/**
 * Generate a full test suite: unit specs plus integration, API, E2E, security,
 * and error-handling specs where the corresponding inputs exist.
 */
export function generateTestSuite(input: TestGenerationInput): TestSpec[] {
  const specs: TestSpec[] = [...generateUnitTestSpecs(input)];

  for (const item of itemsByCategory(input, "REQUIREMENT")) {
    specs.push(
      spec("integration", `integration-${item.id}`, `Integration: requirement ${item.id}`, [item], {
        given: "collaborating components are wired together",
        when: "the requirement path executes end to end within the module boundary",
        then: `the integrated behavior fulfills: ${item.text}`
      })
    );
  }

  for (const item of itemsByCategory(input, "EXPECTED_OUTPUT")) {
    specs.push(
      spec("api", `api-${item.id}`, `API: output contract ${item.id}`, [item], {
        given: "an API request that targets this output",
        when: "the API handler responds",
        then: `the response contains the expected output: ${item.text}`
      })
    );
  }

  for (const item of itemsByCategory(input, "ACCEPTANCE_CRITERIA")) {
    specs.push(
      spec("e2e", `e2e-${item.id}`, `E2E: acceptance criterion ${item.id}`, [item], {
        given: "a full workflow starting from the approved contract",
        when: "the end-to-end flow completes",
        then: `the acceptance criterion is observable end to end: ${item.text}`
      })
    );
  }

  const securityItems = [
    ...itemsByCategory(input, "SECURITY_POLICY"),
    ...itemsByCategory(input, "PROHIBITED_BEHAVIOR")
  ];
  for (const item of securityItems) {
    specs.push(
      spec("security", `security-${item.id}`, `Security: prohibits ${item.id}`, [item], {
        given: "an adversarial or unauthorized attempt",
        when: "the guarded behavior is exercised",
        then: `the prohibited/security-sensitive behavior is blocked: ${item.text}`
      })
    );
  }

  for (const item of itemsByCategory(input, "ERROR_HANDLING")) {
    specs.push(
      spec("error-handling", `error-${item.id}`, `Error handling: ${item.id}`, [item], {
        given: "an input that triggers the failure mode",
        when: "the failure occurs",
        then: `the error is handled without unsafe behavior: ${item.text}`
      })
    );
  }

  return specs;
}

/**
 * Verify test coverage against the input, with a focus on acceptance criteria.
 * Uncovered items (including acceptance criteria) appear in the report and in
 * the verifier input so a downstream verifier can gate on them.
 */
export function verifyTestCoverage(
  input: TestGenerationInput,
  specs: TestSpec[]
): TestCoverageReport {
  const coveredIds = new Set<string>();
  for (const item of specs.flatMap((current) => current.mapsToItemIds)) coveredIds.add(item);

  const coveredItemIds = input.items.map((item) => item.id).filter((id) => coveredIds.has(id));
  const uncoveredItems = input.items.filter((item) => !coveredIds.has(item.id));
  const uncoveredAcceptanceCriteria = uncoveredItems.filter(
    (item) => item.category === "ACCEPTANCE_CRITERIA"
  );
  const acceptanceCount = itemsByCategory(input, "ACCEPTANCE_CRITERIA").length;
  const coverageRatio = input.items.length === 0 ? 1 : coveredItemIds.length / input.items.length;

  return {
    version: "testgen.coverage.v1",
    totalItems: input.items.length,
    coveredItemIds,
    uncoveredItems,
    uncoveredAcceptanceCriteria,
    acceptanceCriteriaCovered:
      acceptanceCount === 0 ? true : uncoveredAcceptanceCriteria.length === 0,
    coverageRatio,
    verifierInput: {
      version: "testgen.verifier-input.v1",
      dslHash: input.dslHash,
      specCount: specs.length,
      specs: specs.map((current) => ({
        id: current.id,
        kind: current.kind,
        mapsToItemIds: current.mapsToItemIds
      })),
      uncoveredItemIds: uncoveredItems.map((item) => item.id),
      uncoveredAcceptanceCriteriaIds: uncoveredAcceptanceCriteria.map((item) => item.id)
    }
  };
}

/**
 * Render a human-readable Markdown test plan with a traceability table mapping
 * each generated spec back to its DSL-derived input items and DSL paths.
 */
export function renderTestPlanMarkdown(
  input: TestGenerationInput,
  specs: TestSpec[],
  coverage: TestCoverageReport
): string {
  const lines = [
    "# Generated Test Plan (Draft)",
    "",
    "> Generated automatically from an Intent/Contract DSL snapshot. Specifications are derived only from DSL inputs and must be reviewed before use.",
    "",
    `DSL hash: ${input.dslHash ?? "none"}`,
    `Inputs: ${input.items.length}`,
    `Specs: ${specs.length}`,
    `Acceptance criteria covered: ${coverage.acceptanceCriteriaCovered ? "yes" : "no"}`,
    "",
    "## Specifications",
    ""
  ];
  for (const current of specs) {
    lines.push(`### ${current.id} (${current.kind})`, "");
    lines.push(`- **Title:** ${current.title}`);
    lines.push(`- **Given:** ${current.given}`);
    lines.push(`- **When:** ${current.when}`);
    lines.push(`- **Then:** ${current.then}`);
    lines.push(`- **Maps to:** ${current.mapsToItemIds.join(", ") || "-"}`);
    lines.push(`- **DSL paths:** ${current.dslPaths.join(", ") || "-"}`);
    lines.push("");
  }
  lines.push("## Coverage", "");
  lines.push("| Item | Category | Covered |");
  lines.push("| --- | --- | --- |");
  for (const item of input.items) {
    const covered = coverage.coveredItemIds.includes(item.id) ? "yes" : "no";
    lines.push(`| ${item.id} | ${item.category} | ${covered} |`);
  }
  if (coverage.uncoveredItems.length > 0) {
    lines.push("", "## Uncovered Inputs", "");
    for (const item of coverage.uncoveredItems) {
      lines.push(`- ${item.id} (${item.category}): ${item.text}`);
    }
  }
  return `${lines.join("\n").trim()}\n`;
}

function spec(
  kind: TestKind,
  id: string,
  title: string,
  items: TestGenerationItem[],
  gwt: { given: string; when: string; then: string }
): TestSpec {
  return {
    id,
    kind,
    title,
    mapsToItemIds: items.map((item) => item.id),
    categories: unique(items.map((item) => item.category)),
    dslPaths: unique(items.flatMap((item) => item.sourceDslPaths)),
    given: gwt.given,
    when: gwt.when,
    then: gwt.then
  };
}

function valueText(field: FormalField<unknown>): string {
  return typeof field.value === "string" ? field.value : JSON.stringify(field.value);
}

function dedupeById(items: TestGenerationItem[]): TestGenerationItem[] {
  const byId = new Map<string, TestGenerationItem>();
  for (const item of items) if (!byId.has(item.id)) byId.set(item.id, item);
  return [...byId.values()];
}

function unique<T>(values: T[]): T[] {
  return [...new Set(values)];
}
