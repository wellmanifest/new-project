export const DSL_VERSION = "office.dsl.v1";

export type RiskLevel = "low" | "medium" | "high";
export type ActionName =
  | "database.query"
  | "report.generate"
  | "file.export"
  | "email.prepare"
  | "email.send"
  | "user.ask"
  | "user.confirm"
  | "log.search";

export interface TaskDsl {
  version: typeof DSL_VERSION;
  task: {
    id: string;
    title: string;
    input: string;
    createdBy: "mock-llm" | "openrouter" | "human" | "example";
  };
  sources: SourceRef[];
  steps: Step[];
  output: OutputSpec;
  policies: PolicySpec[];
  expectedResults: string[];
  errorHandling: {
    onFailure: "stop" | "continue";
  };
}

export interface SourceRef {
  id: string;
  connector: "mock";
  name:
    | "mock.customers"
    | "mock.invoices"
    | "mock.employees"
    | "mock.activity_logs"
    | "mock.outbox";
}

export interface Step {
  id: string;
  description: string;
  when?: Condition;
  action: ActionName;
  with: Record<string, unknown>;
  saveAs?: string;
  ask?: ClarifyingQuestion;
  confirm?: Confirmation;
}

export interface Condition {
  var: string;
  op: "exists" | "equals";
  value?: unknown;
}

export interface ClarifyingQuestion {
  id: string;
  prompt: string;
  saveAs: string;
}

export interface Confirmation {
  id: string;
  prompt: string;
  required: boolean;
}

export interface OutputSpec {
  format: "json" | "markdown";
  saveAs: string;
}

export interface PolicySpec {
  decision: "ALLOW" | "DENY" | "REQUIRE";
  subject: string;
  reason: string;
}

export interface ValidationIssue {
  path: string;
  message: string;
}

export interface ValidationResult {
  ok: boolean;
  issues: ValidationIssue[];
}

const actions = new Set<ActionName>([
  "database.query",
  "report.generate",
  "file.export",
  "email.prepare",
  "email.send",
  "user.ask",
  "user.confirm",
  "log.search"
]);

const sources = new Set<SourceRef["name"]>([
  "mock.customers",
  "mock.invoices",
  "mock.employees",
  "mock.activity_logs",
  "mock.outbox"
]);

export const taskDslJsonSchema = {
  $schema: "https://json-schema.org/draft/2020-12/schema",
  $id: "https://wellmanifest.local/schemas/office-dsl-v1.json",
  title: "Office DSL v1",
  type: "object",
  required: [
    "version",
    "task",
    "sources",
    "steps",
    "output",
    "policies",
    "expectedResults",
    "errorHandling"
  ],
  properties: {
    version: { const: DSL_VERSION },
    task: { type: "object" },
    sources: { type: "array" },
    steps: { type: "array", minItems: 1 },
    output: { type: "object" },
    policies: { type: "array" },
    expectedResults: { type: "array", items: { type: "string" } },
    errorHandling: { type: "object" }
  }
} as const;

export function parseTaskDsl(input: string): TaskDsl {
  const parsed = JSON.parse(input) as unknown;
  const result = validateTaskDsl(parsed);
  if (!result.ok) {
    throw new Error(result.issues.map((issue) => `${issue.path}: ${issue.message}`).join("; "));
  }
  return parsed as TaskDsl;
}

export function validateTaskDsl(value: unknown): ValidationResult {
  const issues: ValidationIssue[] = [];
  const root = value as Partial<TaskDsl> | null;
  if (!root || typeof root !== "object") return fail("$", "DSL must be an object");
  if (root.version !== DSL_VERSION)
    issues.push({ path: "version", message: `must be ${DSL_VERSION}` });
  if (!root.task?.id || !root.task.input)
    issues.push({ path: "task", message: "id and input are required" });
  if (!Array.isArray(root.sources)) issues.push({ path: "sources", message: "must be an array" });
  else {
    root.sources.forEach((source, index) => {
      if (!source.id) issues.push({ path: `sources[${index}].id`, message: "is required" });
      if (source.connector !== "mock")
        issues.push({ path: `sources[${index}].connector`, message: "only mock is allowed" });
      if (!sources.has(source.name))
        issues.push({ path: `sources[${index}].name`, message: "unknown source" });
    });
  }
  if (!Array.isArray(root.steps) || root.steps.length === 0)
    issues.push({ path: "steps", message: "must not be empty" });
  else {
    root.steps.forEach((step, index) => {
      if (!step.id) issues.push({ path: `steps[${index}].id`, message: "is required" });
      if (!actions.has(step.action))
        issues.push({ path: `steps[${index}].action`, message: "unknown action" });
      if (step.action === "email.send" && step.confirm?.required !== true) {
        issues.push({
          path: `steps[${index}].confirm`,
          message: "email.send requires confirmation"
        });
      }
      if (step.action === "user.ask" && !step.ask)
        issues.push({ path: `steps[${index}].ask`, message: "is required" });
    });
  }
  if (!root.output?.saveAs || !root.output.format)
    issues.push({ path: "output", message: "format and saveAs are required" });
  if (!root.errorHandling?.onFailure)
    issues.push({ path: "errorHandling", message: "onFailure is required" });
  return { ok: issues.length === 0, issues };

  function fail(path: string, message: string): ValidationResult {
    return { ok: false, issues: [{ path, message }] };
  }
}

export function renderHumanDsl(dsl: TaskDsl): string {
  const lines = [
    `TASK ${dsl.task.id} "${dsl.task.title}"`,
    `INPUT "${dsl.task.input}"`,
    ...dsl.sources.map((source) => `SOURCE ${source.id} ${source.name}`),
    ...dsl.steps.flatMap((step) => [
      `STEP ${step.id} "${step.description}"`,
      step.when
        ? `WHEN ${step.when.var} ${step.when.op} ${JSON.stringify(step.when.value ?? true)}`
        : "",
      `DO ${step.action}`,
      `WITH ${JSON.stringify(step.with)}`,
      step.saveAs ? `SAVE ${step.saveAs}` : "",
      step.ask ? `ASK ${step.ask.id} "${step.ask.prompt}" SAVE ${step.ask.saveAs}` : "",
      step.confirm ? `CONFIRM ${step.confirm.id} "${step.confirm.prompt}"` : ""
    ]),
    `OUTPUT ${dsl.output.format} SAVE ${dsl.output.saveAs}`,
    ...dsl.policies.map(
      (policy) => `POLICY ${policy.decision} ${policy.subject} "${policy.reason}"`
    )
  ];
  return lines.filter(Boolean).join("\n");
}
