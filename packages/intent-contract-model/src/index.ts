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
  span?: { start: number; end: number };
}

export interface FormalField<T> {
  field: string;
  value: T | null;
  status: FieldStatus;
  requiredForCompletion: boolean;
  source: SourceReference | null;
  approvedBy: string[];
  interpretations?: string[];
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

export interface ConflictValue {
  partyId?: string;
  value: unknown;
  source: SourceReference | null;
}

export interface ConflictNode {
  id: string;
  field: string;
  description: FormalField<string>;
  sourceIds: string[];
  values?: ConflictValue[];
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
  field?: string;
  reason?: string;
  source?: SourceReference | null;
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

export interface CollectedField {
  path: string;
  field: FormalField<unknown>;
}

export function collectFormalFields(dsl: IntentContractDsl): CollectedField[] {
  const out: CollectedField[] = [];
  walk(dsl as unknown, "");
  return out;

  function walk(value: unknown, path: string): void {
    if (!value || typeof value !== "object") return;
    if (isFormalFieldLike(value)) {
      out.push({ path, field: value as FormalField<unknown> });
      return;
    }
    if (Array.isArray(value)) {
      value.forEach((item, index) => walk(item, `${path}[${index}]`));
      return;
    }
    for (const [key, child] of Object.entries(value)) {
      walk(child, path ? `${path}.${key}` : key);
    }
  }
}

export type GeneratedQuestionReason =
  | "MISSING"
  | "AMBIGUOUS"
  | "CONFLICTING"
  | "UNAPPROVED_ASSUMPTION"
  | "REJECTED";

export type PartyRoute = "Human1" | "Human2" | "unknown";

export interface CompletenessGap {
  path: string;
  field: string;
  status: FieldStatus;
}

export interface AmbiguityReport {
  path: string;
  field: string;
  interpretations: string[];
}

export interface ConflictReport {
  path: string;
  field: string;
  sourceIds: string[];
  values: ConflictValue[];
}

export interface AssumptionReport {
  path: string;
  field: string;
  value: unknown;
}

export interface TraceabilityGap {
  path: string;
  field: string;
}

export interface RejectedApprovalReport {
  path: string;
  partyId: string;
  party: PartyRoute;
  field: string;
  reason: string;
}

export interface GeneratedQuestion {
  path: string;
  field: string;
  reason: GeneratedQuestionReason;
  prompt: string;
  targetParties: PartyRoute[];
  interpretations?: string[];
}

export interface IntentContractDiagnosis {
  completenessGaps: CompletenessGap[];
  ambiguities: AmbiguityReport[];
  conflicts: ConflictReport[];
  unapprovedAssumptions: AssumptionReport[];
  traceabilityGaps: TraceabilityGap[];
  rejectedApprovals: RejectedApprovalReport[];
  generatedQuestions: GeneratedQuestion[];
  finalizationReady: boolean;
  blockingReasons: string[];
}

export function diagnoseIntentContractDsl(dsl: IntentContractDsl): IntentContractDiagnosis {
  const fields = collectFormalFields(dsl);
  const completenessGaps: CompletenessGap[] = [];
  const ambiguities: AmbiguityReport[] = [];
  const unapprovedAssumptions: AssumptionReport[] = [];
  const traceabilityGaps: TraceabilityGap[] = [];
  const rejectedApprovals: RejectedApprovalReport[] = [];
  const conflicts: ConflictReport[] = [];
  const generatedQuestions: GeneratedQuestion[] = [];

  for (const { path, field } of fields) {
    const material = field.requiredForCompletion;
    const hasValue = field.value !== null;
    const route = routeFromSource(field.source);

    if (material && (field.status === "MISSING" || field.status === "INCOMPLETE")) {
      completenessGaps.push({ path, field: field.field, status: field.status });
      generatedQuestions.push({
        path,
        field: field.field,
        reason: "MISSING",
        prompt: `Provide a value for "${field.field}"; it is required for completion and currently ${field.status}.`,
        targetParties: route
      });
    }

    if (field.status === "AMBIGUOUS") {
      const interpretations = field.interpretations ?? [];
      ambiguities.push({ path, field: field.field, interpretations });
      generatedQuestions.push({
        path,
        field: field.field,
        reason: "AMBIGUOUS",
        prompt:
          interpretations.length > 0
            ? `Choose a single interpretation for "${field.field}": ${interpretations.join(" | ")}.`
            : `Clarify the intended meaning of "${field.field}"; it is ambiguous.`,
        targetParties: route,
        interpretations
      });
    }

    if (field.status === "CONFLICTING") {
      conflicts.push({
        path,
        field: field.field,
        sourceIds: field.source ? [field.source.id] : [],
        values: []
      });
      generatedQuestions.push({
        path,
        field: field.field,
        reason: "CONFLICTING",
        prompt: `Resolve the conflicting value for "${field.field}" before finalization.`,
        targetParties: route
      });
    }

    if (field.status === "ASSUMED" && hasValue && field.approvedBy.length === 0) {
      unapprovedAssumptions.push({ path, field: field.field, value: field.value });
      generatedQuestions.push({
        path,
        field: field.field,
        reason: "UNAPPROVED_ASSUMPTION",
        prompt: `Approve or correct the assumed value for "${field.field}": ${JSON.stringify(field.value)}.`,
        targetParties: route
      });
    }

    if (material && hasValue && field.source === null) {
      traceabilityGaps.push({ path, field: field.field });
    }
  }

  dsl.conflicts.forEach((node, index) => {
    conflicts.push({
      path: `conflicts[${index}]`,
      field: node.field,
      sourceIds: node.sourceIds,
      values: node.values ?? []
    });
    generatedQuestions.push({
      path: `conflicts[${index}]`,
      field: node.field,
      reason: "CONFLICTING",
      prompt: `Resolve the conflict on "${node.field}" between sources ${
        node.sourceIds.length > 0 ? node.sourceIds.join(", ") : "unknown"
      } before finalization.`,
      targetParties: routeConflictNode(dsl, node)
    });
  });

  dsl.approvals.forEach((approval, index) => {
    if (approval.decision !== "REJECTED") return;
    const party = routeApprovalParty(dsl, approval);
    const field = approval.field ?? "contract";
    const reason = approval.reason ?? "Approval was rejected without a detailed reason.";
    rejectedApprovals.push({
      path: `approvals[${index}]`,
      partyId: approval.partyId,
      party,
      field,
      reason
    });
    generatedQuestions.push({
      path: `approvals[${index}]`,
      field,
      reason: "REJECTED",
      prompt: `${party} rejected "${field}" and needs clarification from Human1: ${reason}`,
      targetParties: party === "Human2" ? ["Human1"] : ["unknown"]
    });
  });

  const blockingReasons: string[] = [];
  for (const gap of completenessGaps) {
    blockingReasons.push(`${gap.path} is ${gap.status} but required for completion.`);
  }
  for (const ambiguity of ambiguities) {
    blockingReasons.push(`${ambiguity.path} is ambiguous and needs a single interpretation.`);
  }
  for (const conflict of conflicts) {
    blockingReasons.push(`${conflict.path} has an unresolved conflict on "${conflict.field}".`);
  }
  for (const assumption of unapprovedAssumptions) {
    blockingReasons.push(`${assumption.path} is an assumed value that requires explicit approval.`);
  }
  for (const trace of traceabilityGaps) {
    blockingReasons.push(`${trace.path} carries a material value without a source reference.`);
  }

  for (const rejection of rejectedApprovals) {
    blockingReasons.push(
      `${rejection.path} was rejected by ${rejection.party} for "${rejection.field}": ${rejection.reason}`
    );
  }

  return {
    completenessGaps,
    ambiguities,
    conflicts,
    unapprovedAssumptions,
    traceabilityGaps,
    rejectedApprovals,
    generatedQuestions,
    finalizationReady: blockingReasons.length === 0,
    blockingReasons
  };
}

export function questionsForParty(
  diagnosis: IntentContractDiagnosis,
  party: PartyRoute
): GeneratedQuestion[] {
  return diagnosis.generatedQuestions.filter((question) => question.targetParties.includes(party));
}

function routeApprovalParty(dsl: IntentContractDsl, approval: ApprovalNode): PartyRoute {
  const role = partyRoleFromId(dsl, approval.partyId);
  if (role) return role;
  const normalized = approval.partyId.toLowerCase();
  if (normalized === "human1" || normalized.includes("human1")) return "Human1";
  if (normalized === "human2" || normalized.includes("human2")) return "Human2";
  return "unknown";
}

function routeFromSource(source: SourceReference | null): PartyRoute[] {
  const speaker = source?.speaker;
  if (speaker === "Human1" || speaker === "Human2") return [speaker];
  return ["unknown"];
}

function routeConflictNode(dsl: IntentContractDsl, node: ConflictNode): PartyRoute[] {
  const parties = new Set<PartyRoute>();
  for (const value of node.values ?? []) {
    const speaker = value.source?.speaker;
    if (speaker === "Human1" || speaker === "Human2") parties.add(speaker);
    const role = partyRoleFromId(dsl, value.partyId);
    if (role) parties.add(role);
  }
  for (const id of node.sourceIds) {
    const ref = dsl.sourceReferences.find((reference) => reference.id === id);
    if (ref?.speaker === "Human1" || ref?.speaker === "Human2") parties.add(ref.speaker);
  }
  return parties.size > 0 ? sortRoutes([...parties]) : ["unknown"];
}

function partyRoleFromId(dsl: IntentContractDsl, partyId: string | undefined): PartyRoute | null {
  if (!partyId) return null;
  const party = dsl.parties.find((candidate) => candidate.id === partyId);
  const role = party?.role.value;
  return role === "Human1" || role === "Human2" ? role : null;
}

const routeOrder: Record<PartyRoute, number> = { Human1: 0, Human2: 1, unknown: 2 };

function sortRoutes(routes: PartyRoute[]): PartyRoute[] {
  return [...routes].sort((a, b) => routeOrder[a] - routeOrder[b]);
}

export const CONVERSATION_VERSION = "intent-contract.conversation.v1";

export type ConversationSpeaker = "Human1" | "Human2" | "system";

export interface ConversationMessage {
  id: string;
  speaker: ConversationSpeaker;
  timestamp: string;
  text: string;
}

export interface Conversation {
  version: typeof CONVERSATION_VERSION;
  id: string;
  messages: ConversationMessage[];
}

const conversationSpeakers = new Set<ConversationSpeaker>(["Human1", "Human2", "system"]);

export function validateConversation(value: unknown): IntentContractValidationResult {
  const issues: IntentContractValidationIssue[] = [];
  if (!value || typeof value !== "object") {
    return { ok: false, issues: [{ path: "$", message: "conversation must be an object" }] };
  }
  const root = value as Partial<Conversation>;
  if (root.version !== CONVERSATION_VERSION) {
    issues.push({ path: "version", message: `must be ${CONVERSATION_VERSION}` });
  }
  if (!root.id || typeof root.id !== "string") {
    issues.push({ path: "id", message: "is required" });
  }
  if (!Array.isArray(root.messages)) {
    issues.push({ path: "messages", message: "must be an array" });
    return { ok: issues.length === 0, issues };
  }
  const seenIds = new Set<string>();
  root.messages.forEach((message, index) => {
    const path = `messages[${index}]`;
    if (!message || typeof message !== "object") {
      issues.push({ path, message: "must be an object" });
      return;
    }
    const msg = message as Partial<ConversationMessage>;
    if (!msg.id || typeof msg.id !== "string") {
      issues.push({ path: `${path}.id`, message: "is required" });
    } else if (seenIds.has(msg.id)) {
      issues.push({ path: `${path}.id`, message: `duplicate message id "${msg.id}"` });
    } else {
      seenIds.add(msg.id);
    }
    if (!conversationSpeakers.has(msg.speaker as ConversationSpeaker)) {
      issues.push({ path: `${path}.speaker`, message: "must be Human1, Human2, or system" });
    }
    if (
      !msg.timestamp ||
      typeof msg.timestamp !== "string" ||
      Number.isNaN(Date.parse(msg.timestamp))
    ) {
      issues.push({ path: `${path}.timestamp`, message: "must be an ISO-8601 timestamp" });
    }
    if (!msg.text || typeof msg.text !== "string" || !msg.text.trim()) {
      issues.push({ path: `${path}.text`, message: "is required" });
    }
  });
  return { ok: issues.length === 0, issues };
}

export function parseConversation(input: string): Conversation {
  const parsed = JSON.parse(input) as unknown;
  const result = validateConversation(parsed);
  if (!result.ok) {
    throw new Error(result.issues.map((issue) => `${issue.path}: ${issue.message}`).join("; "));
  }
  return parsed as Conversation;
}

export function messageToSourceReference(message: ConversationMessage): SourceReference {
  return {
    type: "message",
    id: message.id,
    speaker: message.speaker,
    quote: message.text
  };
}

export function conversationToSourceReferences(conversation: Conversation): SourceReference[] {
  return conversation.messages.map(messageToSourceReference);
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
