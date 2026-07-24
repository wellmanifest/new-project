import { createHash } from "node:crypto";
import type { PolicySpec, SourceRef, Step, TaskDsl } from "../../dsl-model/src/index.js";

export const INTENT_CONTRACT_DSL_VERSION = "intent-contract.dsl.v1";

export type FieldStatus =
  | "CONFIRMED"
  | "MISSING"
  | "INCOMPLETE"
  | "AMBIGUOUS"
  | "CONFLICTING"
  | "ASSUMED"
  | "REJECTED"
  | "NOT_APPLICABLE";

export type DocumentType =
  | "OFFICE_COMMAND"
  | "TASK_DELEGATION"
  | "SERVICE_AGREEMENT"
  | "EMPLOYMENT_AGREEMENT"
  | "CONTRACT"
  | "TECHNICAL_SPECIFICATION"
  | "IMPLEMENTATION_PLAN";

export interface SourceReference {
  type: "message" | "conversation" | "file" | "human" | "system" | "derived";
  id: string;
  speaker?: "Human1" | "Human2" | "system" | "unknown";
  path?: string;
  quote?: string;
}

export interface FormalField<T> {
  field: string;
  value: T | null;
  status: FieldStatus;
  requiredForCompletion: boolean;
  source: SourceReference | null;
  approvedBy: string[];
}

export interface IntentContractDsl {
  version: typeof INTENT_CONTRACT_DSL_VERSION;
  document: DocumentNode;
  contract: ContractNode | null;
  parties: PartyNode[];
  roles: RoleNode[];
  intents: IntentNode[];
  subjects: SubjectNode[];
  obligations: ObligationNode[];
  deliverables: DeliverableNode[];
  deadlines: DeadlineNode[];
  payments: PaymentNode[];
  conditions: ConditionNode[];
  dependencies: DependencyNode[];
  acceptanceCriteria: AcceptanceCriterionNode[];
  exclusions: ExclusionNode[];
  assumptions: AssumptionNode[];
  risks: RiskNode[];
  conflicts: ConflictNode[];
  questions: QuestionNode[];
  approvals: ApprovalNode[];
  sourceReferences: SourceReference[];
  render: RenderDirective[];
  execution: ExecutionDirective[];
}

export interface DocumentNode {
  id: string;
  type: FormalField<DocumentType>;
  title: FormalField<string>;
  language: FormalField<string>;
}

export interface ContractNode {
  id: string;
  title: FormalField<string>;
  governingLaw: FormalField<string>;
}

export interface PartyNode {
  id: string;
  name: FormalField<string>;
  role: FormalField<"Human1" | "Human2" | "third_party">;
}

export interface RoleNode {
  id: string;
  partyId: FormalField<string>;
  name: FormalField<string>;
}

export interface IntentNode {
  id: string;
  requesterPartyId: FormalField<string>;
  description: FormalField<string>;
}

export interface SubjectNode {
  id: string;
  description: FormalField<string>;
}

export interface ObligationNode {
  id: string;
  partyId: FormalField<string>;
  description: FormalField<string>;
}

export interface DeliverableNode {
  id: string;
  description: FormalField<string>;
  ownerPartyId: FormalField<string>;
}

export interface DeadlineNode {
  id: string;
  forId: FormalField<string>;
  dueAt: FormalField<string>;
}

export interface PaymentNode {
  id: string;
  payerPartyId: FormalField<string>;
  payeePartyId: FormalField<string>;
  total: FormalField<{ amount: number; currency: string }>;
}

export interface ConditionNode {
  id: string;
  description: FormalField<string>;
}

export interface DependencyNode {
  id: string;
  description: FormalField<string>;
}

export interface AcceptanceCriterionNode {
  id: string;
  description: FormalField<string>;
  appliesToId: FormalField<string>;
}

export interface ExclusionNode {
  id: string;
  description: FormalField<string>;
}

export interface AssumptionNode {
  id: string;
  description: FormalField<string>;
}

export interface RiskNode {
  id: string;
  description: FormalField<string>;
  level: FormalField<"low" | "medium" | "high">;
}

export interface ConflictNode {
  id: string;
  field: string;
  description: FormalField<string>;
  sourceIds: string[];
}

export interface QuestionNode {
  id: string;
  targetPartyId: FormalField<string>;
  field: string;
  prompt: FormalField<string>;
}

export interface ApprovalNode {
  id: string;
  partyId: string;
  dslHash: string;
  decision: "APPROVED" | "REJECTED";
  approvedAt: string;
}

export interface RenderDirective {
  id: string;
  target: FormalField<"summary" | "formal_document" | "technical_specification">;
}

export interface ExecutionDirective {
  id: string;
  target: FormalField<"none" | "mock" | "codegen" | "testgen">;
}

export interface IntentContractValidationIssue {
  path: string;
  message: string;
}

export interface IntentContractValidationResult {
  ok: boolean;
  issues: IntentContractValidationIssue[];
}

const topLevelArrays: Array<keyof IntentContractDsl> = [
  "parties",
  "roles",
  "intents",
  "subjects",
  "obligations",
  "deliverables",
  "deadlines",
  "payments",
  "conditions",
  "dependencies",
  "acceptanceCriteria",
  "exclusions",
  "assumptions",
  "risks",
  "conflicts",
  "questions",
  "approvals",
  "sourceReferences",
  "render",
  "execution"
];

const statuses = new Set<FieldStatus>([
  "CONFIRMED",
  "MISSING",
  "INCOMPLETE",
  "AMBIGUOUS",
  "CONFLICTING",
  "ASSUMED",
  "REJECTED",
  "NOT_APPLICABLE"
]);

export function createField<T>(
  field: string,
  value: T | null,
  status: FieldStatus,
  requiredForCompletion: boolean,
  source: SourceReference | null = null,
  approvedBy: string[] = []
): FormalField<T> {
  return { field, value, status, requiredForCompletion, source, approvedBy };
}

export function parseIntentContractDsl(input: string): IntentContractDsl {
  const parsed = JSON.parse(input) as unknown;
  const result = validateIntentContractDsl(parsed);
  if (!result.ok) {
    throw new Error(result.issues.map((issue) => `${issue.path}: ${issue.message}`).join("; "));
  }
  return parsed as IntentContractDsl;
}

export function validateIntentContractDsl(value: unknown): IntentContractValidationResult {
  const issues: IntentContractValidationIssue[] = [];
  if (!value || typeof value !== "object") return fail("$", "DSL must be an object");
  const root = value as Partial<IntentContractDsl>;
  if (root.version !== INTENT_CONTRACT_DSL_VERSION) {
    issues.push({
      path: "version",
      message: `must be ${INTENT_CONTRACT_DSL_VERSION}`
    });
  }
  if (!root.document || typeof root.document !== "object") {
    issues.push({ path: "document", message: "is required" });
  }
  if (!("contract" in root) || (root.contract !== null && typeof root.contract !== "object")) {
    issues.push({ path: "contract", message: "must be an object or null" });
  }
  for (const key of topLevelArrays) {
    if (!Array.isArray(root[key])) issues.push({ path: String(key), message: "must be an array" });
  }
  validateNodeFields(root.document, "document", issues);
  if (root.contract !== null) validateNodeFields(root.contract, "contract", issues);
  for (const key of topLevelArrays) validateArrayFields(root[key], String(key), issues);
  return { ok: issues.length === 0, issues };

  function fail(path: string, message: string): IntentContractValidationResult {
    return { ok: false, issues: [{ path, message }] };
  }
}

export function canonicalizeIntentContractDsl(dsl: IntentContractDsl): string {
  return `${JSON.stringify(sortValue(dsl))}\n`;
}

export function hashIntentContractDsl(dsl: IntentContractDsl): string {
  return createHash("sha256").update(canonicalizeIntentContractDsl(dsl)).digest("hex");
}

function validateArrayFields(
  value: unknown,
  path: string,
  issues: IntentContractValidationIssue[]
): void {
  if (!Array.isArray(value)) return;
  value.forEach((item, index) => validateNodeFields(item, `${path}[${index}]`, issues));
}

function validateNodeFields(
  value: unknown,
  path: string,
  issues: IntentContractValidationIssue[]
): void {
  if (!value || typeof value !== "object") return;
  for (const [key, child] of Object.entries(value)) {
    const childPath = `${path}.${key}`;
    if (isFormalFieldLike(child)) validateFormalField(child, childPath, issues);
    else if (Array.isArray(child)) validateArrayFields(child, childPath, issues);
    else if (child && typeof child === "object") validateNodeFields(child, childPath, issues);
  }
}

function isFormalFieldLike(value: unknown): value is Partial<FormalField<unknown>> {
  return Boolean(value && typeof value === "object" && "field" in value && "status" in value);
}

function validateFormalField(
  field: Partial<FormalField<unknown>>,
  path: string,
  issues: IntentContractValidationIssue[]
): void {
  if (!field.field) issues.push({ path: `${path}.field`, message: "is required" });
  if (!statuses.has(field.status as FieldStatus)) {
    issues.push({ path: `${path}.status`, message: "unknown status" });
  }
  if (typeof field.requiredForCompletion !== "boolean") {
    issues.push({ path: `${path}.requiredForCompletion`, message: "must be boolean" });
  }
  if (!Array.isArray(field.approvedBy)) {
    issues.push({ path: `${path}.approvedBy`, message: "must be an array" });
  }
  if (field.status === "CONFIRMED" && field.value === null) {
    issues.push({ path: `${path}.value`, message: "confirmed fields must have a value" });
  }
  if (
    (field.status === "MISSING" ||
      field.status === "AMBIGUOUS" ||
      field.status === "CONFLICTING") &&
    field.requiredForCompletion !== true
  ) {
    issues.push({
      path: `${path}.requiredForCompletion`,
      message: `${field.status} fields must be required for completion`
    });
  }
}

function sortValue(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(sortValue);
  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([key, item]) => [key, sortValue(item)])
    );
  }
  return value;
}

export interface OfficeDslMigrationNote {
  fromPath: string;
  toPath: string;
  decision: "mapped" | "assumed" | "omitted";
  status: FieldStatus;
  reason: string;
}

export interface OfficeDslMigrationResult {
  dsl: IntentContractDsl;
  notes: OfficeDslMigrationNote[];
}

export function officeDslToIntentContractDsl(task: TaskDsl): OfficeDslMigrationResult {
  const notes: OfficeDslMigrationNote[] = [];
  const inputSource: SourceReference = {
    type: "message",
    id: `${task.task.id}:input`,
    speaker: task.task.createdBy === "human" ? "Human1" : "system",
    quote: task.task.input
  };
  const systemSource: SourceReference = {
    type: "system",
    id: `${task.task.id}:office-dsl`,
    quote: "Migrated from office.dsl.v1"
  };
  const sourceReferences = [
    inputSource,
    systemSource,
    ...task.sources.map(sourceToReference),
    ...task.steps.map(stepToReference),
    ...task.policies.map(policyToReference)
  ];

  const dsl: IntentContractDsl = {
    version: INTENT_CONTRACT_DSL_VERSION,
    document: {
      id: `${task.task.id}:document`,
      type: field("document.type", "OFFICE_COMMAND", "CONFIRMED", false, inputSource, notes, {
        fromPath: "task",
        toPath: "document.type"
      }),
      title: field("document.title", task.task.title, "CONFIRMED", false, inputSource, notes, {
        fromPath: "task.title",
        toPath: "document.title"
      }),
      language: field("document.language", "und", "ASSUMED", false, systemSource, notes, {
        fromPath: "task.input",
        toPath: "document.language",
        reason:
          "Office DSL does not carry a language code; adapter preserves an undetermined language marker."
      })
    },
    contract: null,
    parties: [
      {
        id: "human1",
        name: field("party.name", "Requester", "ASSUMED", false, inputSource, notes, {
          fromPath: "task.createdBy",
          toPath: "parties[0].name",
          reason: "Office DSL tracks creator kind, not a named party."
        }),
        role: field("party.role", "Human1", "ASSUMED", false, inputSource, notes, {
          fromPath: "task.createdBy",
          toPath: "parties[0].role",
          reason: "Single-request Office DSL is treated as Human1 intent."
        })
      },
      {
        id: "office-runtime",
        name: field("party.name", "Office DSL Runtime", "ASSUMED", false, systemSource, notes, {
          fromPath: "version",
          toPath: "parties[1].name"
        }),
        role: field("party.role", "third_party", "ASSUMED", false, systemSource, notes, {
          fromPath: "version",
          toPath: "parties[1].role"
        })
      }
    ],
    roles: [
      {
        id: "requester-role",
        partyId: field("role.partyId", "human1", "ASSUMED", false, inputSource, notes, {
          fromPath: "task.createdBy",
          toPath: "roles[0].partyId"
        }),
        name: field("role.name", "requester", "ASSUMED", false, inputSource, notes, {
          fromPath: "task.createdBy",
          toPath: "roles[0].name"
        })
      }
    ],
    intents: [
      {
        id: `${task.task.id}:intent`,
        requesterPartyId: field(
          "intent.requesterPartyId",
          "human1",
          "ASSUMED",
          false,
          inputSource,
          notes,
          {
            fromPath: "task.createdBy",
            toPath: "intents[0].requesterPartyId"
          }
        ),
        description: field(
          "intent.description",
          task.task.input,
          "CONFIRMED",
          true,
          inputSource,
          notes,
          {
            fromPath: "task.input",
            toPath: "intents[0].description"
          }
        )
      }
    ],
    subjects: task.sources.map((source, index) => ({
      id: `source-${source.id}`,
      description: field(
        "subject.description",
        `${source.name} via ${source.connector}`,
        "CONFIRMED",
        false,
        sourceToReference(source),
        notes,
        { fromPath: `sources[${index}]`, toPath: `subjects[${index}].description` }
      )
    })),
    obligations: task.steps.map((step, index) => ({
      id: step.id,
      partyId: field(
        "obligation.partyId",
        "office-runtime",
        "ASSUMED",
        false,
        stepToReference(step),
        notes,
        {
          fromPath: `steps[${index}].action`,
          toPath: `obligations[${index}].partyId`,
          reason: "Office DSL actions are executable runtime steps rather than human obligations."
        }
      ),
      description: field(
        "obligation.description",
        `${step.description} (${step.action})`,
        "CONFIRMED",
        true,
        stepToReference(step),
        notes,
        { fromPath: `steps[${index}]`, toPath: `obligations[${index}].description` }
      )
    })),
    deliverables: [
      {
        id: task.output.saveAs,
        description: field(
          "deliverable.description",
          `${task.output.format} output saved as ${task.output.saveAs}`,
          "CONFIRMED",
          true,
          systemSource,
          notes,
          { fromPath: "output", toPath: "deliverables[0].description" }
        ),
        ownerPartyId: field(
          "deliverable.ownerPartyId",
          "office-runtime",
          "ASSUMED",
          false,
          systemSource,
          notes,
          { fromPath: "output.saveAs", toPath: "deliverables[0].ownerPartyId" }
        )
      }
    ],
    deadlines: [],
    payments: [],
    conditions: task.steps.flatMap((step, index) =>
      step.when
        ? [
            {
              id: `${step.id}:condition`,
              description: field(
                "condition.description",
                `${step.when.var} ${step.when.op} ${JSON.stringify(step.when.value ?? true)}`,
                "CONFIRMED",
                true,
                stepToReference(step),
                notes,
                { fromPath: `steps[${index}].when`, toPath: `conditions[${index}].description` }
              )
            }
          ]
        : []
    ),
    dependencies: task.steps.slice(1).map((step, index) => ({
      id: `${step.id}:depends-on-previous-step`,
      description: field(
        "dependency.description",
        `${step.id} follows ${task.steps[index]?.id}`,
        "ASSUMED",
        false,
        stepToReference(step),
        notes,
        {
          fromPath: `steps[${index + 1}]`,
          toPath: `dependencies[${index}].description`,
          reason: "Office DSL step order is represented as an assumed execution dependency."
        }
      )
    })),
    acceptanceCriteria: task.expectedResults.map((expected, index) => ({
      id: `expected-${index + 1}`,
      description: field(
        "acceptanceCriterion.description",
        expected,
        "CONFIRMED",
        true,
        inputSource,
        notes,
        {
          fromPath: `expectedResults[${index}]`,
          toPath: `acceptanceCriteria[${index}].description`
        }
      ),
      appliesToId: field(
        "acceptanceCriterion.appliesToId",
        task.output.saveAs,
        "ASSUMED",
        false,
        systemSource,
        notes,
        {
          fromPath: "output.saveAs",
          toPath: `acceptanceCriteria[${index}].appliesToId`
        }
      )
    })),
    exclusions: task.policies
      .filter((policy) => policy.decision === "DENY")
      .map((policy, index) => ({
        id: `policy-deny-${index + 1}`,
        description: field(
          "exclusion.description",
          `${policy.subject}: ${policy.reason}`,
          "CONFIRMED",
          true,
          policyToReference(policy),
          notes,
          { fromPath: `policies[${index}]`, toPath: `exclusions[${index}].description` }
        )
      })),
    assumptions: [
      {
        id: "office-dsl-compatibility",
        description: field(
          "assumption.description",
          "Office DSL migration preserves executable intent but does not infer legal contract terms.",
          "ASSUMED",
          false,
          systemSource,
          notes,
          { fromPath: "version", toPath: "assumptions[0].description" }
        )
      }
    ],
    risks: task.policies.map((policy, index) => ({
      id: `policy-risk-${index + 1}`,
      description: field(
        "risk.description",
        `${policy.subject}: ${policy.reason}`,
        "CONFIRMED",
        false,
        policyToReference(policy),
        notes,
        {
          fromPath: `policies[${index}]`,
          toPath: `risks[${index}].description`
        }
      ),
      level: field(
        "risk.level",
        policy.decision === "DENY" ? "high" : "medium",
        "ASSUMED",
        false,
        policyToReference(policy),
        notes,
        {
          fromPath: `policies[${index}].decision`,
          toPath: `risks[${index}].level`
        }
      )
    })),
    conflicts: [],
    questions: task.steps.flatMap((step, index) =>
      step.ask
        ? [
            {
              id: step.ask.id,
              targetPartyId: field(
                "question.targetPartyId",
                "human1",
                "ASSUMED",
                true,
                stepToReference(step),
                notes,
                {
                  fromPath: `steps[${index}].ask`,
                  toPath: `questions[${index}].targetPartyId`
                }
              ),
              field: step.ask.saveAs,
              prompt: field(
                "question.prompt",
                step.ask.prompt,
                "MISSING",
                true,
                stepToReference(step),
                notes,
                {
                  fromPath: `steps[${index}].ask.prompt`,
                  toPath: `questions[${index}].prompt`
                }
              )
            }
          ]
        : []
    ),
    approvals: [],
    sourceReferences,
    render: [
      {
        id: "office-summary",
        target: field("render.target", "summary", "ASSUMED", false, systemSource, notes, {
          fromPath: "output.format",
          toPath: "render[0].target"
        })
      }
    ],
    execution: [
      {
        id: "office-runtime-mock",
        target: field("execution.target", "mock", "ASSUMED", false, systemSource, notes, {
          fromPath: "version",
          toPath: "execution[0].target"
        })
      }
    ]
  };

  const validation = validateIntentContractDsl(dsl);
  if (!validation.ok) {
    throw new Error(validation.issues.map((issue) => `${issue.path}: ${issue.message}`).join("; "));
  }
  return { dsl, notes };
}

function field<T>(
  fieldName: string,
  value: T | null,
  status: FieldStatus,
  requiredForCompletion: boolean,
  source: SourceReference | null,
  notes: OfficeDslMigrationNote[],
  note: { fromPath: string; toPath: string; reason?: string }
): FormalField<T> {
  notes.push({
    fromPath: note.fromPath,
    toPath: note.toPath,
    decision: status === "ASSUMED" ? "assumed" : "mapped",
    status,
    reason: note.reason ?? "Mapped deterministically from office.dsl.v1."
  });
  return createField(fieldName, value, status, requiredForCompletion, source);
}

function sourceToReference(source: SourceRef): SourceReference {
  return {
    type: "system",
    id: `source:${source.id}`,
    quote: `${source.connector}:${source.name}`
  };
}

function stepToReference(step: Step): SourceReference {
  return {
    type: "system",
    id: `step:${step.id}`,
    quote: `${step.action} ${step.description}`
  };
}

function policyToReference(policy: PolicySpec): SourceReference {
  return {
    type: "system",
    id: `policy:${policy.decision}:${policy.subject}`,
    quote: policy.reason
  };
}
