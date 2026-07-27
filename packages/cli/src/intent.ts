#!/usr/bin/env node
import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import {
  hashIntentContractDsl,
  parseIntentContractDsl,
  validateIntentContractDsl
} from "@office-dsl/intent-contract-model";
import {
  mockPlanGuidelineFileToIntentContractDsl,
  mockPlanIntentContractFromNaturalLanguage
} from "../../llm-planner/src/intent-contract.js";
import { renderDocument } from "@office-dsl/document-renderer";
import {
  extractTestGenerationInput,
  generateTestSuite,
  renderTestPlanMarkdown,
  verifyTestCoverage
} from "@office-dsl/testgen";
import { generateNodeCodeFromApprovedDsl } from "@office-dsl/codegen";
import { runChatScenario } from "@office-dsl/chat-negotiation";
import { runScenario } from "../../example-runner/src/scenario.js";
import { runRecruitmentScenario } from "@office-dsl/recruitment-workflow";
import { fileUrlToPath, normalizePathArgument, platformName } from "./cross-platform.js";

export const INTENT_CLI_VERSION = "well-manifest-intent.cli.v1";

export interface IntentCliOptions {
  json?: boolean;
  human?: boolean;
  outDir?: string;
  write?: boolean;
  platform?: string;
}

interface IntentCliResult {
  version: string;
  command: string;
  platform: string;
  ok: boolean;
  error?: string;
  output?: unknown;
}

function parseOptions(argv: string[]): { options: IntentCliOptions; rest: string[] } {
  const options: IntentCliOptions = {};
  const rest: string[] = [];
  let i = 0;
  while (i < argv.length) {
    const arg = argv[i];
    if (arg === "--json") options.json = true;
    else if (arg === "--human") options.human = true;
    else if (arg === "--write") options.write = true;
    else if (arg === "--out-dir" || arg === "-o") {
      i++;
      options.outDir = argv[i];
    } else if (arg?.startsWith("--")) {
      throw new Error(`Unknown option: ${arg}`);
    } else {
      rest.push(arg);
    }
    i++;
  }
  return { options, rest };
}

export async function runIntentCli(argv: string[]): Promise<IntentCliResult> {
  const { options, rest } = parseOptions(argv);
  const [command, ...args] = rest;
  const platform = options.platform ?? platformName();

  try {
    switch (command) {
      case "version":
        return outputResult(command, platform, { version: INTENT_CLI_VERSION }, options);
      case "plan":
        return await runPlan(args, options, platform);
      case "plan-file":
        return await runPlanFile(args, options, platform);
      case "render":
        return await runRender(args, options, platform);
      case "testgen":
        return await runTestgen(args, options, platform);
      case "codegen":
        return await runCodegen(args, options, platform);
      case "verify":
        return await runVerify(args, options, platform);
      case "approve":
        return await runApprove(args, options, platform);
      case "chat":
        return await runChat(args, options, platform);
      case "example":
        return await runExample(args, options, platform);
      case "recruitment":
        return await runRecruitment(args, options, platform);
      case "help":
      default:
        return outputResult(command ?? "help", platform, { help: usage() }, options);
    }
  } catch (error) {
    return result(
      command ?? "unknown",
      platform,
      false,
      undefined,
      error instanceof Error ? error.message : String(error)
    );
  }
}

async function runPlan(
  args: string[],
  options: IntentCliOptions,
  platform: string
): Promise<IntentCliResult> {
  const input = args.join(" ");
  if (!input) throw new Error("Usage: intent plan <natural language message>");
  const dsl = mockPlanIntentContractFromNaturalLanguage(input, {
    id: "cli-plan",
    sourceId: "cli-message-1"
  });
  return outputResult("plan", platform, { dslHash: hashIntentContractDsl(dsl), dsl }, options);
}

async function runPlanFile(
  args: string[],
  options: IntentCliOptions,
  platform: string
): Promise<IntentCliResult> {
  const file = normalizePathArgument(args[0] ?? "");
  if (!file) throw new Error("Usage: intent plan-file <path-to-guideline-file>");
  const text = await readFile(file, "utf8");
  const dsl = mockPlanGuidelineFileToIntentContractDsl(text, {
    id: "cli-guideline",
    sourceId: "cli-guideline-1",
    sourcePath: file
  });
  return outputResult("plan-file", platform, { dslHash: hashIntentContractDsl(dsl), dsl }, options);
}

async function runRender(
  args: string[],
  options: IntentCliOptions,
  platform: string
): Promise<IntentCliResult> {
  const dsl = await loadDsl(args[0]);
  const rendered = renderDocument(dsl);
  return outputResult("render", platform, { rendered }, options);
}

async function runTestgen(
  args: string[],
  options: IntentCliOptions,
  platform: string
): Promise<IntentCliResult> {
  const dsl = await loadDsl(args[0]);
  const input = extractTestGenerationInput(dsl);
  const specs = generateTestSuite(input);
  const coverage = verifyTestCoverage(input, specs);
  const markdown = renderTestPlanMarkdown(input, specs, coverage);
  const payload = { input, specs, coverage, markdown };
  if (options.write) {
    const outDir = normalizePathArgument(options.outDir ?? process.cwd());
    const outFile = path.join(outDir, "test-plan.md");
    await writeFile(outFile, markdown);
    return outputResult("testgen", platform, { ...payload, written: outFile }, options);
  }
  return outputResult("testgen", platform, payload, options);
}

async function runCodegen(
  args: string[],
  options: IntentCliOptions,
  platform: string
): Promise<IntentCliResult> {
  const dsl = await loadDsl(args[0]);
  const generated = generateNodeCodeFromApprovedDsl(dsl, { now: new Date().toISOString() });
  if (options.write) {
    const outDir = normalizePathArgument(options.outDir ?? process.cwd());
    const written: string[] = [];
    for (const file of generated.files) {
      const outFile = path.join(outDir, file.path);
      await writeFile(outFile, file.content);
      written.push(outFile);
    }
    return outputResult(
      "codegen",
      platform,
      { plan: generated.plan, verifierInput: generated.verifierInput, written },
      options
    );
  }
  return outputResult(
    "codegen",
    platform,
    { plan: generated.plan, files: generated.files, verifierInput: generated.verifierInput },
    options
  );
}

async function runVerify(
  args: string[],
  options: IntentCliOptions,
  platform: string
): Promise<IntentCliResult> {
  const dsl = await loadDsl(args[0]);
  const validation = validateIntentContractDsl(dsl);
  const ok = validation.ok;
  return outputResult(
    "verify",
    platform,
    { ok, issues: validation.issues, dslHash: hashIntentContractDsl(dsl) },
    options
  );
}

async function runApprove(
  args: string[],
  options: IntentCliOptions,
  platform: string
): Promise<IntentCliResult> {
  const dsl = await loadDsl(args[0]);
  const partyId = args[1];
  if (!partyId) throw new Error("Usage: intent approve <dsl-file> <party-id>");
  const dslHash = hashIntentContractDsl(dsl);
  dsl.approvals.push({
    id: `approval-${partyId}-${Date.now()}`,
    partyId,
    decision: "APPROVED",
    dslHash,
    approvedAt: new Date().toISOString()
  });
  const approvedBy = new Set(
    dsl.approvals
      .filter((a) => a.dslHash === dslHash && a.decision === "APPROVED")
      .map((a) => a.partyId)
  );
  const requiredParties = dsl.parties
    .filter((party) => party.role.value === "Human1" || party.role.value === "Human2")
    .map((party) => party.id);
  const bilateral = requiredParties.length > 0 && requiredParties.every((id) => approvedBy.has(id));
  return outputResult(
    "approve",
    platform,
    { dslHash, approvedBy: [...approvedBy].sort(), bilateral },
    options
  );
}

async function runChat(
  args: string[],
  options: IntentCliOptions,
  platform: string
): Promise<IntentCliResult> {
  const repoRoot = process.cwd();
  const target = args[0] ?? "";
  const scenarioDir = resolveScenario(repoRoot, "examples-chat", target);
  const status = await runChatScenario({ repoRoot, scenarioDir });
  return outputResult(
    "chat",
    platform,
    { ok: status.ok, id: status.id, summary: status.summary },
    options
  );
}

async function runExample(
  args: string[],
  options: IntentCliOptions,
  platform: string
): Promise<IntentCliResult> {
  const repoRoot = process.cwd();
  const target = args[0] ?? "";
  const scenarioDir = resolveScenario(repoRoot, "examples", target);
  const status = await runScenario({ repoRoot, scenarioDir });
  return outputResult(
    "example",
    platform,
    { ok: status.ok, id: status.id, generated: status.generatedDir, failures: status.failures },
    options
  );
}

async function runRecruitment(
  args: string[],
  options: IntentCliOptions,
  platform: string
): Promise<IntentCliResult> {
  const repoRoot = process.cwd();
  const target = args[0] ?? "";
  const scenarioDir = resolveScenario(repoRoot, "examples-recruitment", target);
  const status = await runRecruitmentScenario({ repoRoot, scenarioDir });
  return outputResult(
    "recruitment",
    platform,
    { ok: status.ok, id: status.id, summary: status.summary, failures: status.failures },
    options
  );
}

async function loadDsl(
  fileOrText: string | undefined
): Promise<ReturnType<typeof parseIntentContractDsl>> {
  if (!fileOrText)
    throw new Error("Usage: intent <render|testgen|codegen|verify|approve> <dsl-file>");
  const file = fileOrText.startsWith("{") ? fileOrText : normalizePathArgument(fileOrText);
  const raw = fileOrText.startsWith("{") ? fileOrText : await readFile(file, "utf8");
  return parseIntentContractDsl(raw);
}

function resolveScenario(repoRoot: string, baseDir: string, target: string): string {
  if (!target) throw new Error("Scenario name or path is required");
  if (target.startsWith("file://")) return fileUrlToPath(target);
  if (path.isAbsolute(target)) return target;
  if (target.includes("/") || target.includes("\\")) return path.resolve(repoRoot, target);
  return path.join(repoRoot, baseDir, target);
}

function outputResult(
  command: string,
  platform: string,
  payload: unknown,
  options: IntentCliOptions
): IntentCliResult {
  if (options.json) return result(command, platform, true, payload);
  if (options.human) return result(command, platform, true, renderHuman(payload));
  return result(command, platform, true, payload);
}

function result(
  command: string,
  platform: string,
  ok: boolean,
  output?: unknown,
  error?: string
): IntentCliResult {
  return {
    version: INTENT_CLI_VERSION,
    command,
    platform,
    ok,
    output,
    error
  };
}

function renderHuman(payload: unknown): string {
  if (typeof payload === "string") return payload;
  if (payload && typeof payload === "object") {
    const lines: string[] = [];
    for (const [key, value] of Object.entries(payload as Record<string, unknown>)) {
      if (typeof value === "string" && value.includes("\n")) {
        lines.push(`${key}:`);
        for (const line of value.split("\n")) lines.push(`  ${line}`);
      } else if (typeof value === "object" && value !== null) {
        lines.push(`${key}:`);
        lines.push(
          JSON.stringify(value, null, 2)
            .split("\n")
            .map((line) => `  ${line}`)
            .join("\n")
        );
      } else {
        lines.push(`${key}: ${value}`);
      }
    }
    return lines.join("\n");
  }
  return String(payload);
}

function usage(): string {
  return `well-manifest-intent commands (Windows/Linux compatible):
  version
  plan "<natural language message>" [--json|--human]
  plan-file <path-to-guideline> [--json|--human]
  render <dsl-file> [--json|--human]
  testgen <dsl-file> [--write] [--out-dir <dir>] [--json|--human]
  codegen <dsl-file> [--write] [--out-dir <dir>] [--json|--human]
  verify <dsl-file> [--json|--human]
  approve <dsl-file> <party-id> [--json|--human]
  chat <scenario-name-or-path> [--json|--human]
  example <scenario-name-or-path> [--json|--human]
  recruitment <scenario-name-or-path> [--json|--human]
  help

Options:
  --json      Output structured JSON (default on Windows without a TTY).
  --human     Output human-readable key-value text.
  --write     For testgen/codegen, write generated files to --out-dir (default cwd).
  --out-dir   Destination directory for generated artifacts.`;
}

function main(): void {
  runIntentCli(process.argv.slice(2))
    .then((result) => {
      if (typeof result.output === "string") {
        console.log(renderHuman(result));
      } else {
        const pretty = process.stdout.isTTY && !result.error ? 2 : undefined;
        console.log(JSON.stringify(result, null, pretty));
      }
      process.exitCode = result.ok ? 0 : 1;
    })
    .catch((error) => {
      console.error(error instanceof Error ? error.message : String(error));
      process.exitCode = 1;
    });
}

if (import.meta.url.startsWith("file:")) {
  main();
}
