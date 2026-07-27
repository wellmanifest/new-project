#!/usr/bin/env node
import path from "node:path";
import { pathToFileURL } from "node:url";
import { discoverChatScenarios, runChatScenario } from "./chat.js";
import { discoverScenarios, runScenario } from "./scenario.js";
import { discoverRecruitmentScenarios, runRecruitmentScenario } from "./recruitment.js";

export {
  discoverRecruitmentScenarios,
  extractPdfText,
  loadRecruitmentScenarioManifest,
  loadRecruitmentSources,
  ocrPdfToMarkdownFixture,
  renderMarkdownAsPdfTextFixture,
  runRecruitmentScenario,
  validateRecruitmentScenarioManifest
} from "./recruitment.js";
export {
  discoverChatScenarios,
  loadChatScenarioManifest,
  parseChat,
  runChatScenario,
  validateChatDslText,
  validateChatScenarioManifest
} from "./chat.js";
export {
  discoverScenarios,
  loadScenarioManifest,
  runScenario,
  validateScenarioManifest
} from "./scenario.js";

async function main(argv: string[]): Promise<void> {
  const normalizedArgv = argv.filter((arg) => arg !== "--");
  const [command, target] = normalizedArgv;
  const repoRoot = process.cwd();
  if (command === "chat-run") {
    if (!target) throw new Error("Usage: example-runner chat-run <scenario-name-or-path>");
    const scenarioDir = resolveChatScenario(repoRoot, target);
    const result = await runChatScenario({ repoRoot, scenarioDir });
    printChatResult(result);
    process.exitCode = result.ok ? 0 : 1;
    return;
  }
  if (command === "chat-all") {
    const dirs = await discoverChatScenarios(repoRoot);
    const results = [];
    for (const scenarioDir of dirs) {
      const result = await runChatScenario({ repoRoot, scenarioDir });
      results.push(result);
      printChatResult(result);
    }
    const failed = results.filter((result) => !result.ok);
    console.log(`\nexamples-chat: ${results.length - failed.length}/${results.length} passed`);
    process.exitCode = failed.length ? 1 : 0;
    return;
  }
  if (command === "recruitment-run") {
    if (!target) throw new Error("Usage: example-runner recruitment-run <scenario-name-or-path>");
    const scenarioDir = resolveRecruitmentScenario(repoRoot, target);
    const result = await runRecruitmentScenario({ repoRoot, scenarioDir });
    printRecruitmentResult(result);
    process.exitCode = result.ok ? 0 : 1;
    return;
  }
  if (command === "recruitment-all") {
    const dirs = await discoverRecruitmentScenarios(repoRoot);
    const results = [];
    for (const scenarioDir of dirs) {
      const result = await runRecruitmentScenario({ repoRoot, scenarioDir });
      results.push(result);
      printRecruitmentResult(result);
    }
    const failed = results.filter((result) => !result.ok);
    console.log(
      `\nexamples-recruitment: ${results.length - failed.length}/${results.length} passed`
    );
    process.exitCode = failed.length ? 1 : 0;
    return;
  }
  if (command === "run") {
    if (!target) throw new Error("Usage: example-runner run <scenario-name-or-path>");
    const scenarioDir = resolveScenario(repoRoot, target);
    const result = await runScenario({ repoRoot, scenarioDir });
    printResult(result);
    process.exitCode = result.ok ? 0 : 1;
    return;
  }
  if (command === "all") {
    const dirs = await discoverScenarios(repoRoot);
    const results = [];
    for (const scenarioDir of dirs) {
      const result = await runScenario({ repoRoot, scenarioDir });
      results.push(result);
      printResult(result);
    }
    const failed = results.filter((result) => !result.ok);
    console.log(`\nexamples: ${results.length - failed.length}/${results.length} passed`);
    process.exitCode = failed.length ? 1 : 0;
    return;
  }
  console.log(
    "Usage: example-runner run <scenario-name-or-path> | all | chat-run <scenario-name-or-path> | chat-all | recruitment-run <scenario-name-or-path> | recruitment-all"
  );
  process.exitCode = 2;
}

function resolveScenario(repoRoot: string, target: string): string {
  if (path.isAbsolute(target)) return target;
  if (target.includes("/") || target.includes("\\")) return path.resolve(repoRoot, target);
  return path.join(repoRoot, "examples", target);
}

function resolveChatScenario(repoRoot: string, target: string): string {
  if (path.isAbsolute(target)) return target;
  if (target.includes("/") || target.includes("\\")) return path.resolve(repoRoot, target);
  return path.join(repoRoot, "examples-chat", target);
}

function resolveRecruitmentScenario(repoRoot: string, target: string): string {
  if (path.isAbsolute(target)) return target;
  if (target.includes("/") || target.includes("\\")) return path.resolve(repoRoot, target);
  return path.join(repoRoot, "examples-recruitment", target);
}

function printResult(result: Awaited<ReturnType<typeof runScenario>>): void {
  const marker = result.ok ? "PASS" : "FAIL";
  console.log(`${marker} ${result.id}`);
  console.log(`  generated: ${path.relative(process.cwd(), result.generatedDir)}`);
  for (const failure of result.failures) console.log(`  - ${failure}`);
}

function printRecruitmentResult(result: Awaited<ReturnType<typeof runRecruitmentScenario>>): void {
  const marker = result.ok ? "PASS" : "FAIL";
  console.log(`${marker} ${result.id}`);
  console.log(`  accepted: ${result.summary.accepted.length}`);
  console.log(`  rejected: ${result.summary.rejected.length}`);
  console.log(`  generated: ${path.relative(process.cwd(), result.generatedDir)}`);
  for (const failure of result.failures) console.log(`  - ${failure}`);
}

function printChatResult(result: Awaited<ReturnType<typeof runChatScenario>>): void {
  const marker = result.ok ? "PASS" : "FAIL";
  console.log(`${marker} ${result.id}`);
  console.log(`  outcome: ${result.summary.outcome}`);
  console.log(`  generated: ${path.relative(process.cwd(), result.generatedDir)}`);
  for (const failure of result.failures) console.log(`  - ${failure}`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main(process.argv.slice(2)).catch((error) => {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  });
}
