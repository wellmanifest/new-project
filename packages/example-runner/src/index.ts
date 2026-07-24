#!/usr/bin/env node
import path from "node:path";
import { pathToFileURL } from "node:url";
import { discoverScenarios, runScenario } from "./scenario.js";

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
  console.log("Usage: example-runner run <scenario-name-or-path> | all");
  process.exitCode = 2;
}

function resolveScenario(repoRoot: string, target: string): string {
  if (path.isAbsolute(target)) return target;
  if (target.includes("/") || target.includes("\\")) return path.resolve(repoRoot, target);
  return path.join(repoRoot, "examples", target);
}

function printResult(result: Awaited<ReturnType<typeof runScenario>>): void {
  const marker = result.ok ? "PASS" : "FAIL";
  console.log(`${marker} ${result.id}`);
  console.log(`  generated: ${path.relative(process.cwd(), result.generatedDir)}`);
  for (const failure of result.failures) console.log(`  - ${failure}`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main(process.argv.slice(2)).catch((error) => {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  });
}
