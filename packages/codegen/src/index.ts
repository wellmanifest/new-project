import { execFile } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { promisify } from "node:util";
import {
  collectFormalFields,
  hashIntentContractDsl,
  validateIntentContractDsl,
  type FormalField,
  type IntentContractDsl,
  type SourceReference
} from "../../intent-contract-model/src/index.js";

const execFileAsync = promisify(execFile);

export const CODEGEN_VERSION = "codegen.node.v1";

export type CodeGenerationTarget = "node-esm-contract-module";

export interface AllowedCodeGenerationTarget {
  id: CodeGenerationTarget;
  runtime: "node";
  moduleFormat: "esm";
  dependencyPolicy: "none";
  filesystemPolicy: "read-only-fixtures";
  networkPolicy: "disabled";
  processPolicy: "no-child-process";
  outputFiles: string[];
}

export interface CodeGenerationOptions {
  target?: CodeGenerationTarget;
  now?: string;
}

export interface CodeGenerationPlanStep {
  id: string;
  description: string;
  inputDslPaths: string[];
  outputPath: string;
}

export interface CodeGenerationPlan {
  version: typeof CODEGEN_VERSION;
  target: AllowedCodeGenerationTarget;
  dslHash: string;
  approvedBy: string[];
  generatedAt: string;
  steps: CodeGenerationPlanStep[];
}

export interface GeneratedCodeFile {
  path: string;
  content: string;
  sha256: string;
}

export interface CodeGenerationResult {
  version: typeof CODEGEN_VERSION;
  plan: CodeGenerationPlan;
  files: GeneratedCodeFile[];
  verifierInput: CodeGenerationVerifierInput;
}

export interface GeneratedTestResult {
  name: string;
  passed: boolean;
  message?: string;
}

export interface CodeGenerationTestRun {
  version: typeof CODEGEN_VERSION;
  dslHash: string;
  target: CodeGenerationTarget;
  passed: boolean;
  tests: GeneratedTestResult[];
  verifierInput: CodeGenerationVerifierInput;
}

export interface CodeGenerationVerifierInput {
  version: "codegen.verifier-input.v1";
  dslHash: string;
  target: CodeGenerationTarget;
  generatedFiles: Array<{ path: string; sha256: string }>;
  testResults: GeneratedTestResult[];
  approvedBy: string[];
}

export const ALLOWED_CODE_GENERATION_TARGETS: AllowedCodeGenerationTarget[] = [
  {
    id: "node-esm-contract-module",
    runtime: "node",
    moduleFormat: "esm",
    dependencyPolicy: "none",
    filesystemPolicy: "read-only-fixtures",
    networkPolicy: "disabled",
    processPolicy: "no-child-process",
    outputFiles: ["package.json", "src/contract-spec.mjs", "test/contract-spec.test.mjs"]
  }
];

export class CodeGenerationError extends Error {}

export function hashCodeGenerationDslSnapshot(dsl: IntentContractDsl): string {
  const approvalFreeDsl: IntentContractDsl = { ...dsl, approvals: [] };
  return hashIntentContractDsl(approvalFreeDsl);
}

export function getAllowedCodeGenerationTarget(
  target: CodeGenerationTarget = "node-esm-contract-module"
): AllowedCodeGenerationTarget {
  const found = ALLOWED_CODE_GENERATION_TARGETS.find((candidate) => candidate.id === target);
  if (!found) throw new CodeGenerationError(`Unsupported code generation target: ${target}`);
  return found;
}

export function assertDslApprovedForCodeGeneration(dsl: IntentContractDsl): string[] {
  const validation = validateIntentContractDsl(dsl);
  if (!validation.ok) {
    throw new CodeGenerationError(
      validation.issues.map((issue) => `${issue.path}: ${issue.message}`).join("; ")
    );
  }
  const dslHash = hashCodeGenerationDslSnapshot(dsl);
  const approvedParties = new Set(
    dsl.approvals
      .filter((approval) => approval.decision === "APPROVED" && approval.dslHash === dslHash)
      .map((approval) => approval.partyId)
  );
  const requiredParties = dsl.parties
    .filter((party) => party.role.value === "Human1" || party.role.value === "Human2")
    .map((party) => party.id);
  const missing = requiredParties.filter((partyId) => !approvedParties.has(partyId));
  if (requiredParties.length === 0 || missing.length > 0) {
    throw new CodeGenerationError(
      `Code generation requires APPROVED records for the current DSL hash from all Human1/Human2 parties. Missing: ${missing.join(", ") || "Human1/Human2 parties"}`
    );
  }
  return requiredParties.sort();
}

export function createImplementationPlanFromApprovedDsl(
  dsl: IntentContractDsl,
  options: CodeGenerationOptions = {}
): CodeGenerationPlan {
  const target = getAllowedCodeGenerationTarget(options.target);
  const approvedBy = assertDslApprovedForCodeGeneration(dsl);
  const dslHash = hashCodeGenerationDslSnapshot(dsl);
  const inputDslPaths = collectFormalFields(dsl)
    .filter(({ field }) => field.value !== null)
    .map(({ path }) => path)
    .sort();
  return {
    version: CODEGEN_VERSION,
    target,
    dslHash,
    approvedBy,
    generatedAt: options.now ?? "1970-01-01T00:00:00.000Z",
    steps: [
      {
        id: "extract-approved-contract-spec",
        description:
          "Extract a deterministic contract specification from approved Intent/Contract DSL fields.",
        inputDslPaths,
        outputPath: "src/contract-spec.mjs"
      },
      {
        id: "emit-generated-tests",
        description:
          "Emit dependency-free Node.js tests derived from the approved DSL hash and spec.",
        inputDslPaths: ["approvals", ...inputDslPaths],
        outputPath: "test/contract-spec.test.mjs"
      },
      {
        id: "emit-package-manifest",
        description:
          "Emit a bounded package manifest with no dependencies and ESM runtime metadata.",
        inputDslPaths: ["version", "execution"],
        outputPath: "package.json"
      }
    ]
  };
}

export function generateNodeCodeFromApprovedDsl(
  dsl: IntentContractDsl,
  options: CodeGenerationOptions = {}
): CodeGenerationResult {
  const plan = createImplementationPlanFromApprovedDsl(dsl, options);
  const spec = createContractSpec(dsl, plan.dslHash, plan.approvedBy);
  const files: GeneratedCodeFile[] = [
    file("package.json", renderPackageJson()),
    file("src/contract-spec.mjs", renderContractSpecModule(spec)),
    file("test/contract-spec.test.mjs", renderContractSpecTest(plan.dslHash))
  ];
  return {
    version: CODEGEN_VERSION,
    plan,
    files,
    verifierInput: createVerifierInput(plan, files, [])
  };
}

export async function runGeneratedNodeTests(
  result: CodeGenerationResult
): Promise<CodeGenerationTestRun> {
  const tempDir = await mkdtemp(path.join(os.tmpdir(), "office-dsl-codegen-"));
  try {
    for (const generated of result.files) {
      const fullPath = path.join(tempDir, generated.path);
      await writeFileWithParents(fullPath, generated.content);
    }
    const testFile = path.join(tempDir, "test", "contract-spec.test.mjs");
    const source = await readFile(path.join(tempDir, "src", "contract-spec.mjs"), "utf8");
    const tests: GeneratedTestResult[] = [
      await asyncTest("generated Node.js test file exits successfully", async () => {
        await execFileAsync(process.execPath, [testFile], { cwd: tempDir });
        return true;
      }),
      test("generated code contains no dynamic evaluation", () =>
        !/\b(eval|Function|child_process|fetch|XMLHttpRequest)\b/.test(source)),
      test("generated files match recorded hashes", () =>
        result.files.every((generated) => sha256(generated.content) === generated.sha256))
    ];
    const passed = tests.every((item) => item.passed);
    return {
      version: CODEGEN_VERSION,
      dslHash: result.plan.dslHash,
      target: result.plan.target.id,
      passed,
      tests,
      verifierInput: createVerifierInput(result.plan, result.files, tests)
    };
  } finally {
    await rm(tempDir, { recursive: true, force: true });
  }
}

interface ContractSpec {
  version: typeof CODEGEN_VERSION;
  dslHash: string;
  approvedBy: string[];
  document: { id: string; type: string | null; title: string | null; language: string | null };
  parties: Array<{ id: string; name: string | null; role: string | null }>;
  deliverables: string[];
  obligations: string[];
  acceptanceCriteria: string[];
  sourceReferences: string[];
}

function createContractSpec(
  dsl: IntentContractDsl,
  dslHash: string,
  approvedBy: string[]
): ContractSpec {
  return {
    version: CODEGEN_VERSION,
    dslHash,
    approvedBy,
    document: {
      id: dsl.document.id,
      type: stringValue(dsl.document.type),
      title: stringValue(dsl.document.title),
      language: stringValue(dsl.document.language)
    },
    parties: dsl.parties.map((party) => ({
      id: party.id,
      name: stringValue(party.name),
      role: stringValue(party.role)
    })),
    deliverables: dsl.deliverables.map((node) => stringValue(node.description)).filter(isString),
    obligations: dsl.obligations.map((node) => stringValue(node.description)).filter(isString),
    acceptanceCriteria: dsl.acceptanceCriteria
      .map((node) => stringValue(node.description))
      .filter(isString),
    sourceReferences: dsl.sourceReferences.map(sourceLabel).sort()
  };
}

function renderPackageJson(): string {
  return `${JSON.stringify({ type: "module", private: true, dependencies: {} }, null, 2)}\n`;
}

function renderContractSpecModule(spec: ContractSpec): string {
  return [
    "// Generated from approved intent-contract.dsl.v1. Do not edit by hand.",
    "// Runtime boundary: no dependencies, no filesystem writes, no network, no dynamic code execution.",
    `export const contractSpec = ${JSON.stringify(spec, null, 2)};`,
    "",
    "export function summarizeContract() {",
    "  return [",
    "    `Document: ${contractSpec.document.title ?? contractSpec.document.id}` ,",
    "    `Type: ${contractSpec.document.type ?? 'UNKNOWN'}` ,",
    "    `Parties: ${contractSpec.parties.map((party) => party.name ?? party.id).join(', ')}` ,",
    "    `Deliverables: ${contractSpec.deliverables.join('; ') || 'none'}` ,",
    "    `Acceptance: ${contractSpec.acceptanceCriteria.join('; ') || 'none'}`",
    "  ].join('\\n');",
    "}",
    ""
  ].join("\n");
}

function renderContractSpecTest(dslHash: string): string {
  return [
    "import assert from 'node:assert/strict';",
    "import { contractSpec, summarizeContract } from '../src/contract-spec.mjs';",
    "",
    `assert.equal(contractSpec.dslHash, ${JSON.stringify(dslHash)});`,
    "assert.equal(contractSpec.version, 'codegen.node.v1');",
    "assert.ok(contractSpec.approvedBy.length >= 2);",
    "assert.ok(summarizeContract().includes(contractSpec.document.title ?? contractSpec.document.id));",
    "console.log('generated contract-spec tests passed');",
    ""
  ].join("\n");
}

function createVerifierInput(
  plan: CodeGenerationPlan,
  files: GeneratedCodeFile[],
  testResults: GeneratedTestResult[]
): CodeGenerationVerifierInput {
  return {
    version: "codegen.verifier-input.v1",
    dslHash: plan.dslHash,
    target: plan.target.id,
    generatedFiles: files.map((generated) => ({ path: generated.path, sha256: generated.sha256 })),
    testResults,
    approvedBy: plan.approvedBy
  };
}

function file(pathName: string, content: string): GeneratedCodeFile {
  return { path: pathName, content, sha256: sha256(content) };
}

function test(name: string, fn: () => boolean): GeneratedTestResult {
  try {
    return { name, passed: fn() };
  } catch (error) {
    return { name, passed: false, message: error instanceof Error ? error.message : String(error) };
  }
}

async function asyncTest(name: string, fn: () => Promise<boolean>): Promise<GeneratedTestResult> {
  try {
    return { name, passed: await fn() };
  } catch (error) {
    return { name, passed: false, message: error instanceof Error ? error.message : String(error) };
  }
}

async function writeFileWithParents(filePath: string, content: string): Promise<void> {
  const { mkdir } = await import("node:fs/promises");
  await mkdir(path.dirname(filePath), { recursive: true });
  await writeFile(filePath, content);
}

function stringValue(field: FormalField<unknown>): string | null {
  return typeof field.value === "string"
    ? field.value
    : field.value === null
      ? null
      : String(field.value);
}

function sourceLabel(source: SourceReference): string {
  return [source.type, source.id, source.path].filter(Boolean).join(":");
}

function sha256(content: string): string {
  return createHash("sha256").update(content).digest("hex");
}

function isString(value: string | null): value is string {
  return typeof value === "string";
}
