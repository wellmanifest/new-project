export {
  runPythonSemanticVerifier,
  type SemanticVerificationReport,
  type SemanticVerifierInput
} from "./python-verifier.js";
import { createHash, randomUUID } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { TaskDsl, Step, validateTaskDsl } from "@office-dsl/dsl-model";
import {
  runPythonSemanticVerifier,
  type PythonSemanticVerifierOptions,
  type SemanticVerifierInput
} from "./python-verifier.js";
import {
  hashIntentContractDsl,
  officeDslToIntentContractDsl,
  validateIntentContractDsl,
  type IntentContractDsl
} from "@office-dsl/intent-contract-model";

export type TaskState =
  | "CREATED"
  | "PLANNING"
  | "DSL_GENERATED"
  | "VALIDATING"
  | "VERIFICATION_FAILED"
  | "WAITING_FOR_INPUT"
  | "WAITING_FOR_CONFIRMATION"
  | "READY"
  | "RUNNING"
  | "SUCCEEDED"
  | "FAILED"
  | "DENIED"
  | "CANCELLED";

export type PolicyDecision =
  | "ALLOW"
  | "DENY"
  | "REQUIRE_CONFIRMATION"
  | "REQUIRE_INPUT"
  | "REQUIRE_CAPABILITY";
export type RuntimeApprovalParty = "Human1" | "Human2";
export type RuntimeApprovalDecision = "APPROVED" | "REJECTED";

export interface RuntimeApprovalRecord {
  id: string;
  party: RuntimeApprovalParty;
  dslHash: string;
  decision: RuntimeApprovalDecision;
  approvedAt: string;
  status: "ACTIVE" | "INVALIDATED";
  invalidatedAt?: string;
  invalidatedByHash?: string;
  reason?: string;
}

export interface PlanAction {
  stepId: string;
  action: string;
  description: string;
  risk: "low" | "medium" | "high";
  requiresConfirmation: boolean;
  input: Record<string, unknown>;
}

export interface ExecutionPlan {
  taskId: string;
  actions: PlanAction[];
  dryRun: boolean;
}

export interface AuditRecord {
  task_id: string;
  timestamp: string;
  nl_command: string;
  llm_mode: string;
  dsl: TaskDsl;
  validation: ReturnType<typeof validateTaskDsl>;
  verifier: unknown;
  plan: ExecutionPlan;
  plan_hash: string;
  intent_contract_hash: string;
  approvals: RuntimeApprovalRecord[];
  answers: Record<string, string>;
  confirmations: Record<string, string>;
  policy_decisions: PolicyFinding[];
  executed_actions: ActionResult[];
  errors: string[];
  final_status: TaskState;
  history: StateHistory[];
}

export interface TaskSession {
  id: string;
  state: TaskState;
  dsl: TaskDsl;
  plan: ExecutionPlan;
  planHash: string;
  intentContractDsl: IntentContractDsl;
  intentContractHash: string;
  approvals: RuntimeApprovalRecord[];
  answers: Record<string, string>;
  confirmations: Record<string, string>;
  audit: AuditRecord;
}

export interface StateHistory {
  from: TaskState;
  to: TaskState;
  at: string;
  reason: string;
}

export interface PolicyFinding {
  decision: PolicyDecision;
  stepId?: string;
  reason: string;
}

export interface ActionContext {
  vars: Record<string, unknown>;
  dryRun: boolean;
  dataDir: string;
  exportDir: string;
}

export interface ActionResult {
  stepId: string;
  action: string;
  dryRun: boolean;
  output: unknown;
}

export interface RegisteredAction {
  name: string;
  risk: "low" | "medium" | "high";
  capability: string;
  requiresConfirmation: boolean;
  run(step: Step, context: ActionContext): Promise<unknown>;
}

export class StateMachine {
  private readonly transitions: Record<TaskState, TaskState[]> = {
    CREATED: ["PLANNING", "CANCELLED"],
    PLANNING: ["DSL_GENERATED", "FAILED", "CANCELLED"],
    DSL_GENERATED: ["VALIDATING", "CANCELLED"],
    VALIDATING: [
      "READY",
      "WAITING_FOR_INPUT",
      "WAITING_FOR_CONFIRMATION",
      "VERIFICATION_FAILED",
      "DENIED",
      "CANCELLED"
    ],
    VERIFICATION_FAILED: ["PLANNING", "DENIED", "CANCELLED"],
    WAITING_FOR_INPUT: ["VALIDATING", "CANCELLED"],
    WAITING_FOR_CONFIRMATION: ["READY", "DENIED", "CANCELLED"],
    READY: ["RUNNING", "DENIED", "CANCELLED"],
    RUNNING: ["SUCCEEDED", "FAILED", "CANCELLED"],
    SUCCEEDED: [],
    FAILED: [],
    DENIED: [],
    CANCELLED: []
  };

  transition(session: TaskSession, to: TaskState, reason: string): void {
    const allowed = this.transitions[session.state] ?? [];
    if (!allowed.includes(to)) throw new Error(`Invalid transition ${session.state} -> ${to}`);
    const from = session.state;
    session.state = to;
    session.audit.final_status = to;
    session.audit.history.push({ from, to, at: new Date().toISOString(), reason });
  }
}

export class ActionRegistry {
  private actions = new Map<string, RegisteredAction>();
  register(action: RegisteredAction): void {
    this.actions.set(action.name, action);
  }
  get(name: string): RegisteredAction | undefined {
    return this.actions.get(name);
  }
  list(): RegisteredAction[] {
    return [...this.actions.values()];
  }
}

export function createDefaultRegistry(): ActionRegistry {
  const registry = new ActionRegistry();
  registry.register({
    name: "database.query",
    risk: "low",
    capability: "mock.read",
    requiresConfirmation: false,
    async run(step, context) {
      const dataset = String(step.with.dataset ?? "");
      const rows = await readJsonArray(path.join(context.dataDir, `${dataset}.json`));
      if (step.with.kind === "unpaidInvoicesOlderThanDays") {
        const days = Number(step.with.days ?? 30);
        return rows.filter((row) => row.status === "unpaid" && Number(row.daysOverdue) > days);
      }
      if (step.with.kind === "salesReport") return rows;
      throw new Error("Unsupported safe query kind");
    }
  });
  registry.register({
    name: "log.search",
    risk: "low",
    capability: "mock.logs.read",
    requiresConfirmation: false,
    async run(step, context) {
      const rows = await readJsonArray(path.join(context.dataDir, "activity_logs.json"));
      const contains = String(step.with.contains ?? "").toLowerCase();
      return rows.filter((row) => JSON.stringify(row).toLowerCase().includes(contains));
    }
  });
  registry.register({
    name: "report.generate",
    risk: "low",
    capability: "report.write",
    requiresConfirmation: false,
    async run(step, context) {
      const input = context.vars[String(step.with.from)] ?? [];
      return {
        title: step.with.title,
        rows: input,
        summary: `Generated report with ${Array.isArray(input) ? input.length : 0} rows`
      };
    }
  });
  registry.register({
    name: "email.prepare",
    risk: "medium",
    capability: "email.draft",
    requiresConfirmation: false,
    async run(step, context) {
      const rows = context.vars[String(step.with.from)] as
        | Array<Record<string, unknown>>
        | undefined;
      return (rows ?? []).map((row) => ({
        to: row.email,
        subject: "Payment reminder",
        body: `Please review invoice ${String(row.invoiceId ?? row.id)}.`
      }));
    }
  });
  registry.register({
    name: "email.send",
    risk: "high",
    capability: "email.send",
    requiresConfirmation: true,
    async run(step, context) {
      const messages = (context.vars[String(step.with.from)] ?? []) as unknown[];
      const outbox = path.join(context.dataDir, "outbox.json");
      if (context.dryRun) return { wouldSend: messages.length, outbox };
      await writeFile(outbox, `${JSON.stringify(messages, null, 2)}\n`, "utf8");
      return { sent: messages.length, outbox };
    }
  });
  registry.register({
    name: "file.export",
    risk: "medium",
    capability: "file.export",
    requiresConfirmation: false,
    async run(step, context) {
      const requested = String(step.with.path ?? "report.json");
      const target = safeResolve(context.exportDir, requested);
      const payload = context.vars[String(step.with.from)] ?? {};
      await mkdir(path.dirname(target), { recursive: true });
      if (context.dryRun) return { wouldWrite: target };
      await writeFile(target, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
      return { path: target };
    }
  });
  registry.register({
    name: "user.ask",
    risk: "low",
    capability: "user.input",
    requiresConfirmation: false,
    async run(step) {
      return step.ask;
    }
  });
  registry.register({
    name: "user.confirm",
    risk: "low",
    capability: "user.confirm",
    requiresConfirmation: true,
    async run(step) {
      return step.confirm;
    }
  });
  return registry;
}

export class PolicyEngine {
  evaluate(dsl: TaskDsl, registry: ActionRegistry): PolicyFinding[] {
    const findings: PolicyFinding[] = [];
    for (const step of dsl.steps) {
      const action = registry.get(step.action);
      if (!action)
        findings.push({
          decision: "DENY",
          stepId: step.id,
          reason: `Unknown action ${step.action}`
        });
      if (
        step.action.includes("shell") ||
        JSON.stringify(step.with).match(/\b(eval|Function|rm\s+-rf|del\s+\/)/i)
      ) {
        findings.push({
          decision: "DENY",
          stepId: step.id,
          reason: "Dynamic code or shell command attempt is blocked"
        });
      }
      if (step.action === "email.send" && step.confirm?.required !== true) {
        findings.push({
          decision: "REQUIRE_CONFIRMATION",
          stepId: step.id,
          reason: "email.send always requires confirmation"
        });
      }
      if (
        (step.action === "email.prepare" || step.action === "email.send") &&
        !step.with.from &&
        !step.with.to
      ) {
        findings.push({
          decision: "DENY",
          stepId: step.id,
          reason: "Email operation has no recipient source"
        });
      }
      if (step.action === "file.export") {
        try {
          safeResolve(".office-dsl/exports", String(step.with.path ?? ""));
        } catch {
          findings.push({ decision: "DENY", stepId: step.id, reason: "Path traversal is blocked" });
        }
      }
    }
    return findings.length
      ? findings
      : [{ decision: "ALLOW", reason: "Deterministic policy checks passed" }];
  }
}

function verifierBlocksExecution(verifier: unknown): boolean {
  if (!verifier || typeof verifier !== "object") return false;
  const verdict = (verifier as { verdict?: unknown }).verdict;
  return verdict === "FAIL" || verdict === "NEEDS_REVIEW";
}

export class Runtime {
  private state = new StateMachine();
  constructor(
    private registry = createDefaultRegistry(),
    private policy = new PolicyEngine(),
    private dataDir = process.env.OFFICE_DSL_DATA_DIR ?? "mock-data",
    private exportDir = process.env.OFFICE_DSL_EXPORT_DIR ?? ".office-dsl/exports"
  ) {}

  create(dsl: TaskDsl, verifier: unknown = { verdict: "PASS", score: 1 }): TaskSession {
    const validation = validateTaskDsl(dsl);
    const plan = this.plan(dsl, true);
    const planHash = hashPlan(plan);
    const intentContractDsl = officeDslToIntentContractDsl(dsl).dsl;
    const intentContractHash = hashIntentContractDsl(intentContractDsl);
    const session: TaskSession = {
      id: dsl.task.id || randomUUID(),
      state: "CREATED",
      dsl,
      plan,
      planHash,
      intentContractDsl,
      intentContractHash,
      approvals: [],
      answers: {},
      confirmations: {},
      audit: {
        task_id: dsl.task.id,
        timestamp: new Date().toISOString(),
        nl_command: dsl.task.input,
        llm_mode: dsl.task.createdBy,
        dsl,
        validation,
        verifier,
        plan,
        plan_hash: planHash,
        intent_contract_hash: intentContractHash,
        approvals: [],
        answers: {},
        confirmations: {},
        policy_decisions: [],
        executed_actions: [],
        errors: [],
        final_status: "CREATED",
        history: []
      }
    };
    this.state.transition(session, "PLANNING", "task created");
    this.state.transition(session, "DSL_GENERATED", "dsl attached");
    this.state.transition(session, "VALIDATING", "validation started");
    const policies = this.policy.evaluate(dsl, this.registry);
    session.audit.policy_decisions = policies;
    if (!validation.ok || policies.some((finding) => finding.decision === "DENY")) {
      this.state.transition(session, "DENIED", "validation or policy denied task");
    } else if (verifierBlocksExecution(verifier)) {
      this.state.transition(session, "VERIFICATION_FAILED", "semantic verifier did not pass");
    } else if (dsl.steps.some((step) => step.ask)) {
      this.state.transition(session, "WAITING_FOR_INPUT", "clarification required");
    } else if (dsl.steps.some((step) => step.confirm?.required)) {
      this.state.transition(session, "WAITING_FOR_CONFIRMATION", "confirmation required");
    } else {
      this.state.transition(session, "READY", "ready to run");
    }
    return session;
  }

  async createWithPythonSemanticVerifier(
    dsl: TaskDsl,
    input: SemanticVerifierInput,
    options: PythonSemanticVerifierOptions = {}
  ): Promise<TaskSession> {
    const verifier = await runPythonSemanticVerifier(input, options);
    return this.create(dsl, verifier);
  }

  answer(session: TaskSession, questionId: string, answer: string): void {
    if (session.state !== "WAITING_FOR_INPUT") throw new Error("Task is not waiting for input");
    session.answers[questionId] = answer;
    session.audit.answers[questionId] = answer;
    this.state.transition(session, "VALIDATING", "answer received");
    if (session.dsl.steps.some((step) => step.confirm?.required))
      this.state.transition(session, "WAITING_FOR_CONFIRMATION", "confirmation required");
    else this.state.transition(session, "READY", "ready after answer");
  }

  approveIntentContract(
    session: TaskSession,
    party: RuntimeApprovalParty,
    dslHash: string,
    decision: RuntimeApprovalDecision = "APPROVED",
    approvedAt = new Date().toISOString()
  ): RuntimeApprovalRecord {
    if (dslHash !== session.intentContractHash) {
      throw new Error("Intent/Contract DSL hash changed; approval is invalid");
    }
    for (const approval of session.approvals) {
      if (approval.status === "ACTIVE" && approval.party === party) {
        approval.status = "INVALIDATED";
        approval.invalidatedAt = approvedAt;
        approval.invalidatedByHash = session.intentContractHash;
        approval.reason = "superseded by a newer approval from the same party";
      }
    }
    const approval: RuntimeApprovalRecord = {
      id: `${session.id}:${party}:${session.approvals.length + 1}`,
      party,
      dslHash,
      decision,
      approvedAt,
      status: "ACTIVE"
    };
    session.approvals.push(approval);
    session.audit.approvals = session.approvals;
    return approval;
  }

  hasBilateralIntentContractApproval(session: TaskSession): boolean {
    const activeApprovals = session.approvals.filter(
      (approval) =>
        approval.status === "ACTIVE" &&
        approval.decision === "APPROVED" &&
        approval.dslHash === session.intentContractHash
    );
    return (
      activeApprovals.some((approval) => approval.party === "Human1") &&
      activeApprovals.some((approval) => approval.party === "Human2")
    );
  }

  updateIntentContractDsl(
    session: TaskSession,
    dsl: IntentContractDsl,
    reason = "intent contract dsl changed",
    changedAt = new Date().toISOString()
  ): string {
    const validation = validateIntentContractDsl(dsl);
    if (!validation.ok) {
      throw new Error(
        validation.issues.map((issue) => `${issue.path}: ${issue.message}`).join("; ")
      );
    }
    const nextHash = hashIntentContractDsl(dsl);
    if (nextHash === session.intentContractHash) return nextHash;
    for (const approval of session.approvals) {
      if (approval.status === "ACTIVE") {
        approval.status = "INVALIDATED";
        approval.invalidatedAt = changedAt;
        approval.invalidatedByHash = nextHash;
        approval.reason = reason;
      }
    }
    session.intentContractDsl = dsl;
    session.intentContractHash = nextHash;
    session.audit.intent_contract_hash = nextHash;
    session.audit.approvals = session.approvals;
    return nextHash;
  }
  confirm(session: TaskSession, confirmationId: string, planHash: string): void {
    if (planHash !== session.planHash)
      throw new Error("Plan hash changed; confirmation is invalid");
    if (session.confirmations[confirmationId]) throw new Error("Confirmation already used");
    session.confirmations[confirmationId] = planHash;
    session.audit.confirmations[confirmationId] = planHash;
    if (session.state === "WAITING_FOR_CONFIRMATION")
      this.state.transition(session, "READY", "confirmation received");
  }

  reject(session: TaskSession): void {
    if (["SUCCEEDED", "FAILED", "DENIED", "CANCELLED"].includes(session.state))
      throw new Error("Task already terminal");
    this.state.transition(session, "DENIED", "user rejected task");
  }

  cancel(session: TaskSession): void {
    if (["SUCCEEDED", "FAILED", "DENIED", "CANCELLED"].includes(session.state))
      throw new Error("Task already terminal");
    this.state.transition(session, "CANCELLED", "user cancelled task");
  }

  async execute(session: TaskSession, execute = false): Promise<ActionResult[]> {
    if (session.state !== "READY") throw new Error(`Task is not ready: ${session.state}`);
    this.state.transition(session, "RUNNING", "execution started");
    const context: ActionContext = {
      vars: { ...session.answers },
      dryRun: !execute,
      dataDir: this.dataDir,
      exportDir: this.exportDir
    };
    try {
      for (const step of session.dsl.steps) {
        if (step.ask || step.action === "user.ask") continue;
        if (step.confirm?.required && !session.confirmations[step.confirm.id])
          throw new Error(`Missing confirmation ${step.confirm.id}`);
        const action = this.registry.get(step.action);
        if (!action) throw new Error(`Unknown action ${step.action}`);
        const output = await action.run(step, context);
        if (step.saveAs) context.vars[step.saveAs] = output;
        session.audit.executed_actions.push({
          stepId: step.id,
          action: step.action,
          dryRun: context.dryRun,
          output
        });
      }
      this.state.transition(session, "SUCCEEDED", "execution finished");
      return session.audit.executed_actions;
    } catch (error) {
      session.audit.errors.push(error instanceof Error ? error.message : String(error));
      this.state.transition(session, "FAILED", "execution failed");
      throw error;
    }
  }

  plan(dsl: TaskDsl, dryRun = true): ExecutionPlan {
    return {
      taskId: dsl.task.id,
      dryRun,
      actions: dsl.steps.map((step) => {
        const action = this.registry.get(step.action);
        return {
          stepId: step.id,
          action: step.action,
          description: step.description,
          risk: action?.risk ?? "high",
          requiresConfirmation: action?.requiresConfirmation ?? false,
          input: step.with
        };
      })
    };
  }
}

export function hashPlan(plan: ExecutionPlan): string {
  return createHash("sha256").update(JSON.stringify(plan)).digest("hex");
}

async function readJsonArray(file: string): Promise<Array<Record<string, unknown>>> {
  return JSON.parse(await readFile(file, "utf8")) as Array<Record<string, unknown>>;
}

function safeResolve(root: string, requested: string): string {
  const base = path.resolve(root);
  const target = path.resolve(base, requested);
  if (target !== base && !target.startsWith(`${base}${path.sep}`))
    throw new Error("Path traversal blocked");
  return target;
}
