import { mkdir, readFile, rm } from "node:fs/promises";
import path from "node:path";
import {
  parseTaskDsl,
  renderHumanDsl,
  TaskDsl,
  validateTaskDsl,
  ValidationResult
} from "@office-dsl/dsl-model";
import { Runtime, TaskSession } from "@office-dsl/dsl-runtime";
import { writeDslHcl } from "@office-dsl/dsl-artifact-renderer";
import { compareJson, compareSubset } from "@office-dsl/regression-runner";
import { runOfficeDslVerifier } from "@office-dsl/verifier-bridge";

export const SCENARIO_VERSION = "example.scenario.v1";

export interface ScenarioManifest {
  version: typeof SCENARIO_VERSION;
  id: string;
  title: string;
  kind:
    | "office-command"
    | "chat-to-dsl"
    | "conversation-to-contract"
    | "guidelines-to-document"
    | "task-delegation";
  input: {
    message?: string;
    conversation?: string;
    guidelines?: string[];
  };
  pipeline: {
    planner: FixturePlannerConfig | MockPlannerConfig | OpenRouterPlannerConfig;
    runtime: {
      mode: "mock";
      dryRun: boolean;
      execute: boolean;
      answers?: Array<{ questionId: string; value: string }>;
      confirmations?: Array<{ confirmationId: string; planHash?: "current" | string }>;
    };
    verifier: {
      kind: "python";
      mode: "mock" | "openrouter";
    };
  };
  expected: {
    dsl?: string;
    plan?: string;
    verification?: string;
  };
}

export interface FixturePlannerConfig {
  kind: "fixture";
  dsl: string;
}

export interface MockPlannerConfig {
  kind: "mock";
}

export interface OpenRouterPlannerConfig {
  kind: "openrouter";
  model?: string;
}

export interface ScenarioRunOptions {
  repoRoot: string;
  scenarioDir: string;
  update?: boolean;
  generatedRoot?: string;
}

export interface ScenarioRunResult {
  id: string;
  scenarioDir: string;
  generatedDir: string;
  ok: boolean;
  failures: string[];
  artifacts: {
    dsl: TaskDsl;
    validation: unknown;
    questions: unknown;
    plan: PlanSummary;
    verification: Record<string, unknown>;
    humanDsl: string;
  };
}

export interface PlanSummary {
  actions: string[];
  requiresInput: boolean;
  requiresConfirmation: boolean;
  dryRun: boolean;
  expectedState: TaskSession["state"];
}

export async function loadScenarioManifest(scenarioDir: string): Promise<ScenarioManifest> {
  const manifest = JSON.parse(
    await readFile(path.join(scenarioDir, "scenario.json"), "utf8")
  ) as ScenarioManifest;
  validateScenarioManifest(manifest, scenarioDir);
  return manifest;
}

export function validateScenarioManifest(manifest: ScenarioManifest, scenarioDir = "."): void {
  if (manifest.version !== SCENARIO_VERSION) {
    throw new Error(`${scenarioDir}: scenario version must be ${SCENARIO_VERSION}`);
  }
  if (!manifest.id || !manifest.title || !manifest.kind) {
    throw new Error(`${scenarioDir}: id, title, and kind are required`);
  }
  if (
    !manifest.input.message &&
    !manifest.input.conversation &&
    !manifest.input.guidelines?.length
  ) {
    throw new Error(`${scenarioDir}: at least one input file must be declared`);
  }
  if (manifest.pipeline.planner.kind === "fixture" && !manifest.pipeline.planner.dsl) {
    throw new Error(`${scenarioDir}: fixture planner requires a dsl path`);
  }
  if (manifest.pipeline.verifier.kind !== "python") {
    throw new Error(`${scenarioDir}: only python verifier is currently implemented`);
  }
}

export async function runScenario(options: ScenarioRunOptions): Promise<ScenarioRunResult> {
  const manifest = await loadScenarioManifest(options.scenarioDir);
  const generatedDir = options.generatedRoot ?? path.join(options.scenarioDir, "generated");
  await rm(generatedDir, { recursive: true, force: true });
  await mkdir(generatedDir, { recursive: true });

  const inputText = await readScenarioInput(options.scenarioDir, manifest);
  const dsl = await loadDsl(options.scenarioDir, manifest);
  const runtime = new Runtime();
  const session = runtime.create(dsl);
  applyAnswersAndConfirmations(session, runtime, manifest);

  const validation = validateTaskDsl(dsl);
  const questions = dsl.steps
    .filter((step) => step.ask)
    .map((step) => ({ stepId: step.id, ...step.ask }));
  const plan = summarizePlan(session);
  const rawVerification = await runPythonVerifier(
    options.repoRoot,
    inputText,
    dsl,
    plan,
    manifest.pipeline.verifier.mode,
    generatedDir
  );
  const verification = normalizeVerification(rawVerification, plan);
  const humanDsl = renderHumanDsl(dsl);

  const artifacts = { dsl, validation, questions, plan, verification, humanDsl };
  await writeDslHcl(generatedDir, "actual.dsl.hcl", humanDsl);
  await writeDslHcl(generatedDir, "actual.validation.dsl.hcl", renderValidationDsl(validation));
  await writeDslHcl(generatedDir, "actual.questions.dsl.hcl", renderQuestionsDsl(questions));
  await writeDslHcl(generatedDir, "actual.plan.dsl.hcl", renderPlanDsl(plan));
  await writeDslHcl(
    generatedDir,
    "actual.verification.dsl.hcl",
    renderVerificationDsl(verification)
  );
  await writeDslHcl(
    generatedDir,
    "actual.python-verification.dsl.hcl",
    renderVerificationDsl(rawVerification)
  );

  const failures = await compareExpected(options.scenarioDir, manifest, artifacts);
  return {
    id: manifest.id,
    scenarioDir: options.scenarioDir,
    generatedDir,
    ok: failures.length === 0,
    failures,
    artifacts
  };
}

export async function discoverScenarios(repoRoot: string): Promise<string[]> {
  const examplesDir = path.join(repoRoot, "examples");
  const { readdir } = await import("node:fs/promises");
  const entries = await readdir(examplesDir, { withFileTypes: true });
  return entries
    .filter((entry) => entry.isDirectory())
    .map((entry) => path.join(examplesDir, entry.name))
    .sort((a, b) => path.basename(a).localeCompare(path.basename(b)));
}

async function readScenarioInput(scenarioDir: string, manifest: ScenarioManifest): Promise<string> {
  if (manifest.input.message)
    return readFile(path.join(scenarioDir, manifest.input.message), "utf8");
  if (manifest.input.conversation)
    return readFile(path.join(scenarioDir, manifest.input.conversation), "utf8");
  const guidelines = manifest.input.guidelines ?? [];
  return (
    await Promise.all(guidelines.map((file) => readFile(path.join(scenarioDir, file), "utf8")))
  ).join("\n\n");
}

async function loadDsl(scenarioDir: string, manifest: ScenarioManifest): Promise<TaskDsl> {
  if (manifest.pipeline.planner.kind === "fixture") {
    return parseTaskDsl(
      await readFile(path.join(scenarioDir, manifest.pipeline.planner.dsl), "utf8")
    );
  }
  if (manifest.pipeline.planner.kind === "mock") {
    const { planFromNaturalLanguage } = await import("@office-dsl/llm-planner");
    return planFromNaturalLanguage(await readScenarioInput(scenarioDir, manifest), {
      mode: "mock"
    });
  }
  const { planFromNaturalLanguage } = await import("@office-dsl/llm-planner");
  return planFromNaturalLanguage(await readScenarioInput(scenarioDir, manifest), {
    mode: "openrouter",
    model: manifest.pipeline.planner.model
  });
}

function applyAnswersAndConfirmations(
  session: TaskSession,
  runtime: Runtime,
  manifest: ScenarioManifest
): void {
  for (const answer of manifest.pipeline.runtime.answers ?? []) {
    runtime.answer(session, answer.questionId, answer.value);
  }
  for (const confirmation of manifest.pipeline.runtime.confirmations ?? []) {
    runtime.confirm(
      session,
      confirmation.confirmationId,
      !confirmation.planHash || confirmation.planHash === "current"
        ? session.planHash
        : confirmation.planHash
    );
  }
}

function summarizePlan(session: TaskSession): PlanSummary {
  return {
    actions: session.plan.actions.map((action) => action.action),
    requiresInput: session.dsl.steps.some((step) => Boolean(step.ask)),
    requiresConfirmation: session.plan.actions.some((action) => action.requiresConfirmation),
    dryRun: session.plan.dryRun,
    expectedState: session.state
  };
}

async function runPythonVerifier(
  repoRoot: string,
  inputText: string,
  dsl: TaskDsl,
  plan: PlanSummary,
  mode: string,
  generatedDir: string
): Promise<Record<string, unknown>> {
  const planDsl = ["PLAN", ...plan.actions.map((action) => `ACTION ${action}`)].join("\n");
  return runOfficeDslVerifier({
    repoRoot,
    inputText,
    dslText: renderHumanDsl(dsl),
    planText: planDsl,
    mode,
    generatedDir
  });
}

function normalizeVerification(
  report: Record<string, unknown>,
  plan: PlanSummary
): Record<string, unknown> {
  return {
    ...report,
    recommended_action: plan.requiresInput ? "ASK_USER" : report.recommended_action
  };
}

async function compareExpected(
  scenarioDir: string,
  manifest: ScenarioManifest,
  artifacts: ScenarioRunResult["artifacts"]
): Promise<string[]> {
  const failures: string[] = [];
  if (manifest.expected.dsl) {
    const expected = JSON.parse(
      await readFile(path.join(scenarioDir, manifest.expected.dsl), "utf8")
    );
    compareJson(failures, "dsl", expected, artifacts.dsl);
  }
  if (manifest.expected.plan) {
    const expected = JSON.parse(
      await readFile(path.join(scenarioDir, manifest.expected.plan), "utf8")
    );
    comparePlanAssertions(failures, expected, artifacts.plan);
  }
  if (manifest.expected.verification) {
    const expected = JSON.parse(
      await readFile(path.join(scenarioDir, manifest.expected.verification), "utf8")
    );
    compareSubset(failures, "verification", expected, artifacts.verification);
  }
  return failures;
}

function comparePlanAssertions(
  failures: string[],
  expected: Record<string, unknown>,
  actual: PlanSummary
): void {
  if (expected.actions) compareJson(failures, "plan.actions", expected.actions, actual.actions);
  if (
    typeof expected.requiresInput === "boolean" &&
    expected.requiresInput !== actual.requiresInput
  ) {
    failures.push(
      `plan.requiresInput expected ${expected.requiresInput} but got ${actual.requiresInput}`
    );
  }
  if (
    typeof expected.requiresConfirmation === "boolean" &&
    expected.requiresConfirmation !== actual.requiresConfirmation
  ) {
    failures.push(
      `plan.requiresConfirmation expected ${expected.requiresConfirmation} but got ${actual.requiresConfirmation}`
    );
  }
  if (typeof expected.dryRun === "boolean" && expected.dryRun !== actual.dryRun) {
    failures.push(`plan.dryRun expected ${expected.dryRun} but got ${actual.dryRun}`);
  }
  if (
    typeof expected.expectedState === "string" &&
    expected.expectedState !== actual.expectedState
  ) {
    failures.push(
      `plan.expectedState expected ${expected.expectedState} but got ${actual.expectedState}`
    );
  }
  if (Array.isArray(expected.forbiddenActions)) {
    const present = expected.forbiddenActions.filter((action) =>
      actual.actions.includes(String(action))
    );
    if (present.length)
      failures.push(`plan.forbiddenActions present in generated actions: ${present.join(", ")}`);
  }
}

function renderValidationDsl(validation: ValidationResult): string {
  const lines = ["VALIDATION"];
  if (validation.ok) {
    lines.push("OK true");
  } else {
    lines.push("OK false");
    for (const issue of validation.issues) {
      lines.push(`ISSUE path="${issue.path}" message="${issue.message}"`);
    }
  }
  return lines.join("\n");
}

function renderQuestionsDsl(
  questions: Array<{ stepId: string; id?: string; prompt?: string; saveAs?: string }>
): string {
  const lines = ["QUESTIONS"];
  if (questions.length === 0) {
    lines.push("NONE");
  } else {
    for (const question of questions) {
      const id = question.id ?? question.stepId;
      const prompt = question.prompt ?? "";
      const saveAs = question.saveAs ?? "";
      lines.push(`QUESTION ${id} "${prompt}" SAVE ${saveAs}`);
    }
  }
  return lines.join("\n");
}

function renderPlanDsl(plan: PlanSummary): string {
  const lines = ["PLAN"];
  for (const action of plan.actions) {
    lines.push(`ACTION ${action}`);
  }
  lines.push(`requiresInput ${plan.requiresInput}`);
  lines.push(`requiresConfirmation ${plan.requiresConfirmation}`);
  lines.push(`dryRun ${plan.dryRun}`);
  lines.push(`expectedState ${plan.expectedState}`);
  return lines.join("\n");
}

function renderVerificationDsl(verification: Record<string, unknown>): string {
  const lines = ["VERIFICATION"];
  for (const [key, value] of Object.entries(verification).sort(([a], [b]) => a.localeCompare(b))) {
    if (Array.isArray(value) && value.length === 0) continue;
    if (Array.isArray(value)) {
      for (const item of value) {
        lines.push(`${key.toUpperCase()} "${String(item).replace(/"/g, '\\"')}"`);
      }
    } else if (typeof value === "string") {
      lines.push(`${key.toUpperCase()} "${value.replace(/"/g, '\\"')}"`);
    } else if (typeof value === "boolean" || typeof value === "number") {
      lines.push(`${key.toUpperCase()} ${value}`);
    } else if (value !== null) {
      lines.push(`${key.toUpperCase()} "${String(value).replace(/"/g, '\\"')}"`);
    }
  }
  return lines.join("\n");
}
