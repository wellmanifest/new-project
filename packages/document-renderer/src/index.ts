import {
  type AcceptanceCriterionNode,
  type ConditionNode,
  type DeadlineNode,
  type DependencyNode,
  type DeliverableNode,
  type DocumentType,
  type ExclusionNode,
  type FormalField,
  type IntentContractDsl,
  type ObligationNode,
  type PaymentNode
} from "@office-dsl/intent-contract-model";

export const DOCUMENT_RENDERER_VERSION = "document-renderer.v1";

/**
 * Legal disclaimer prepended to every rendered document.
 *
 * The renderer never invents terms: any field that is missing, ambiguous,
 * conflicting, rejected, or absent from the DSL is emitted as an explicit gap
 * and never filled with assumed legal language.
 */
export const DRAFT_DISCLAIMER =
  "DRAFT - This document was generated automatically from an Intent/Contract DSL snapshot. " +
  "It is a non-binding draft that must be reviewed by the parties and by qualified legal counsel. " +
  "The renderer does not add, infer, or invent any term that is not present in the DSL. " +
  "Fields that are missing, ambiguous, conflicting, or unapproved are shown as explicit gaps.";

/**
 * Field statuses whose value may appear in a rendered document.
 *
 * `CONFIRMED` and `INCOMPLETE` values come from the DSL directly. `ASSUMED`
 * values are rendered but flagged as needing approval. All other statuses are
 * treated as gaps.
 */
const RENDERABLE_STATUSES = new Set(["CONFIRMED", "INCOMPLETE", "ASSUMED"]);

export interface TraceabilityEntry {
  section: string;
  label: string;
  dslPaths: string[];
  sourceIds: string[];
}

export interface RenderedDocument {
  version: typeof DOCUMENT_RENDERER_VERSION;
  documentType: DocumentType;
  title: string;
  markdown: string;
  traceability: TraceabilityEntry[];
  gaps: string[];
  assumptions: string[];
}

interface RenderContext {
  dsl: IntentContractDsl;
  lines: string[];
  traceability: TraceabilityEntry[];
  gaps: string[];
  assumptions: string[];
  currentSection: string;
}

function createContext(dsl: IntentContractDsl): RenderContext {
  return {
    dsl,
    lines: [],
    traceability: [],
    gaps: [],
    assumptions: [],
    currentSection: "Preamble"
  };
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return "";
  if (typeof value === "object") {
    const record = value as Record<string, unknown>;
    if ("amount" in record && "currency" in record) {
      return `${String(record.amount)} ${String(record.currency)}`;
    }
    return JSON.stringify(value);
  }
  return String(value);
}

function heading(context: RenderContext, title: string): void {
  context.currentSection = title;
  context.lines.push("", `## ${title}`, "");
}

function trace(
  context: RenderContext,
  label: string,
  field: FormalField<unknown> | null,
  extraSourceIds: string[] = []
): void {
  const dslPaths = field ? [field.field] : [];
  const sourceIds = [...extraSourceIds];
  if (field?.source?.id) sourceIds.push(field.source.id);
  context.traceability.push({
    section: context.currentSection,
    label,
    dslPaths,
    sourceIds
  });
}

/**
 * Render a single labeled field as a paragraph. Renderable values become body
 * text; every other status becomes an explicit gap. Assumed values are flagged.
 * Traceability is always recorded so each paragraph maps back to the DSL.
 */
function renderField(
  context: RenderContext,
  label: string,
  field: FormalField<unknown> | null | undefined
): boolean {
  if (!field) {
    context.lines.push(`- **${label}:** [GAP: not present in DSL]`);
    context.gaps.push(`${label}: not present in DSL`);
    trace(context, label, null);
    return false;
  }
  const renderable = field.value !== null && RENDERABLE_STATUSES.has(field.status);
  if (!renderable) {
    context.lines.push(`- **${label}:** [GAP: ${field.field} is ${field.status}]`);
    context.gaps.push(`${field.field} is ${field.status}`);
    trace(context, label, field);
    return false;
  }
  const assumed = field.status === "ASSUMED" && field.approvedBy.length === 0;
  const marker = assumed ? " _(ASSUMED - needs approval)_" : "";
  if (assumed) context.assumptions.push(field.field);
  context.lines.push(`- **${label}:** ${formatValue(field.value)}${marker}`);
  trace(context, label, field);
  return true;
}

/**
 * Render a list of nodes, each described by one field. Empty lists become an
 * explicit "none stated" gap so the reader knows the DSL did not provide any.
 */
function renderList<T>(
  context: RenderContext,
  label: string,
  nodes: T[],
  pick: (node: T) => FormalField<unknown>
): void {
  if (nodes.length === 0) {
    context.lines.push(`- **${label}:** [GAP: none stated in DSL]`);
    context.gaps.push(`${label}: none stated in DSL`);
    trace(context, label, null);
    return;
  }
  nodes.forEach((node, index) => {
    renderField(context, `${label} ${index + 1}`, pick(node));
  });
}

function partyName(dsl: IntentContractDsl, partyId: string | null | undefined): string | null {
  if (!partyId) return null;
  const party = dsl.parties.find((candidate) => candidate.id === partyId);
  return party?.name.value ?? null;
}

function partyByRole(
  dsl: IntentContractDsl,
  role: "Human1" | "Human2"
): IntentContractDsl["parties"][number] | undefined {
  return dsl.parties.find((party) => party.role.value === role);
}

function documentTitle(dsl: IntentContractDsl, fallback: string): string {
  const title = dsl.document.title;
  return title.value !== null && RENDERABLE_STATUSES.has(title.status)
    ? formatValue(title.value)
    : fallback;
}

function renderPreamble(context: RenderContext, title: string): void {
  context.lines.push(`# ${title}`, "", `> ${DRAFT_DISCLAIMER}`);
}

function traceabilityMarkdown(traceability: TraceabilityEntry[]): string[] {
  const lines = ["", "## Traceability Map", ""];
  lines.push("| Section | Item | DSL paths | Source references |");
  lines.push("| --- | --- | --- | --- |");
  for (const entry of traceability) {
    const paths = entry.dslPaths.length > 0 ? entry.dslPaths.join(", ") : "-";
    const sources = entry.sourceIds.length > 0 ? entry.sourceIds.join(", ") : "-";
    lines.push(`| ${entry.section} | ${entry.label} | ${paths} | ${sources} |`);
  }
  return lines;
}

function renderGapsSection(context: RenderContext): void {
  heading(context, "Open Items And Gaps");
  if (context.gaps.length === 0) {
    context.lines.push("- No gaps: every rendered field carries a DSL-backed value.");
    return;
  }
  for (const gap of context.gaps) context.lines.push(`- ${gap}`);
}

function finish(
  context: RenderContext,
  documentType: DocumentType,
  title: string
): RenderedDocument {
  renderGapsSection(context);
  context.lines.push(...traceabilityMarkdown(context.traceability));
  return {
    version: DOCUMENT_RENDERER_VERSION,
    documentType,
    title,
    markdown: `${context.lines.join("\n").trim()}\n`,
    traceability: context.traceability,
    gaps: context.gaps,
    assumptions: context.assumptions
  };
}

/**
 * Task delegation renderer.
 *
 * Renders assignee, deliverables, deadlines, dependencies, exclusions, and
 * acceptance criteria strictly from the DSL.
 */
export function renderTaskDelegation(dsl: IntentContractDsl): RenderedDocument {
  const context = createContext(dsl);
  const title = documentTitle(dsl, "Task Delegation (Draft)");
  renderPreamble(context, title);

  heading(context, "Parties");
  const requester = partyByRole(dsl, "Human1");
  const assignee = partyByRole(dsl, "Human2");
  renderField(context, "Delegator", requester?.name);
  renderField(context, "Assignee", assignee?.name);

  heading(context, "Deliverables");
  renderList(context, "Deliverable", dsl.deliverables, (node: DeliverableNode) => node.description);

  heading(context, "Deadlines");
  renderList(context, "Deadline", dsl.deadlines, (node: DeadlineNode) => node.dueAt);

  heading(context, "Dependencies");
  renderList(context, "Dependency", dsl.dependencies, (node: DependencyNode) => node.description);

  heading(context, "Exclusions");
  renderList(context, "Exclusion", dsl.exclusions, (node: ExclusionNode) => node.description);

  heading(context, "Acceptance Criteria");
  renderList(
    context,
    "Acceptance criterion",
    dsl.acceptanceCriteria,
    (node: AcceptanceCriterionNode) => node.description
  );

  return finish(context, "TASK_DELEGATION", title);
}

/**
 * Service agreement renderer.
 *
 * Renders parties, scope, payment, acceptance criteria, and exclusions from the
 * DSL. Payment references are resolved to party names when available.
 */
export function renderServiceAgreement(dsl: IntentContractDsl): RenderedDocument {
  const context = createContext(dsl);
  const title = documentTitle(dsl, "Service Agreement (Draft)");
  renderPreamble(context, title);

  heading(context, "Parties");
  if (dsl.parties.length === 0) {
    context.lines.push("- **Parties:** [GAP: none stated in DSL]");
    context.gaps.push("Parties: none stated in DSL");
    trace(context, "Parties", null);
  } else {
    for (const party of dsl.parties) {
      renderField(context, `Party (${party.role.value ?? party.id})`, party.name);
    }
  }

  heading(context, "Scope");
  renderList(context, "Subject", dsl.subjects, (node) => node.description);
  renderList(context, "Deliverable", dsl.deliverables, (node: DeliverableNode) => node.description);
  renderList(context, "Obligation", dsl.obligations, (node: ObligationNode) => node.description);

  heading(context, "Payment");
  if (dsl.payments.length === 0) {
    context.lines.push("- **Payment:** [GAP: none stated in DSL]");
    context.gaps.push("Payment: none stated in DSL");
    trace(context, "Payment", null);
  } else {
    dsl.payments.forEach((payment: PaymentNode, index) => {
      const payer = partyName(dsl, payment.payerPartyId.value) ?? payment.payerPartyId.value;
      const payee = partyName(dsl, payment.payeePartyId.value) ?? payment.payeePartyId.value;
      renderField(context, `Payment ${index + 1} total`, payment.total);
      context.lines.push(
        `  - Payer: ${payer ?? "[GAP: MISSING]"}, Payee: ${payee ?? "[GAP: MISSING]"}`
      );
      trace(context, `Payment ${index + 1} parties`, payment.payerPartyId);
      trace(context, `Payment ${index + 1} parties`, payment.payeePartyId);
    });
  }

  heading(context, "Acceptance Criteria");
  renderList(
    context,
    "Acceptance criterion",
    dsl.acceptanceCriteria,
    (node: AcceptanceCriterionNode) => node.description
  );

  heading(context, "Exclusions");
  renderList(context, "Exclusion", dsl.exclusions, (node: ExclusionNode) => node.description);

  heading(context, "Governing Law");
  renderField(context, "Governing law", dsl.contract?.governingLaw ?? null);

  return finish(context, "SERVICE_AGREEMENT", title);
}

/**
 * Employment agreement / guideline renderer.
 *
 * Uses only fields that exist in the Intent/Contract model (parties, subjects,
 * obligations, payments, deadlines, conditions, acceptance criteria,
 * exclusions). It never references employment-specific fields that are not part
 * of the DSL, so guideline inputs render without unsupported fields.
 */
export function renderEmploymentAgreement(dsl: IntentContractDsl): RenderedDocument {
  const context = createContext(dsl);
  const title = documentTitle(dsl, "Employment Agreement (Draft)");
  renderPreamble(context, title);

  heading(context, "Parties");
  const employer = partyByRole(dsl, "Human1");
  const employee = partyByRole(dsl, "Human2");
  renderField(context, "Employer", employer?.name);
  renderField(context, "Employee", employee?.name);

  heading(context, "Position And Duties");
  renderList(context, "Subject", dsl.subjects, (node) => node.description);
  renderList(context, "Duty", dsl.obligations, (node: ObligationNode) => node.description);

  heading(context, "Remuneration");
  renderList(context, "Remuneration", dsl.payments, (node: PaymentNode) => node.total);

  heading(context, "Term And Deadlines");
  renderList(context, "Deadline", dsl.deadlines, (node: DeadlineNode) => node.dueAt);

  heading(context, "Conditions");
  renderList(context, "Condition", dsl.conditions, (node: ConditionNode) => node.description);

  heading(context, "Guidelines And Acceptance");
  renderList(
    context,
    "Guideline",
    dsl.acceptanceCriteria,
    (node: AcceptanceCriterionNode) => node.description
  );

  heading(context, "Exclusions");
  renderList(context, "Exclusion", dsl.exclusions, (node: ExclusionNode) => node.description);

  return finish(context, "EMPLOYMENT_AGREEMENT", title);
}

/**
 * Dispatch to the correct renderer based on the DSL document type. Unknown or
 * generic contract types fall back to the service agreement renderer.
 */
export function renderDocument(dsl: IntentContractDsl): RenderedDocument {
  switch (dsl.document.type.value) {
    case "TASK_DELEGATION":
      return renderTaskDelegation(dsl);
    case "EMPLOYMENT_AGREEMENT":
      return renderEmploymentAgreement(dsl);
    default:
      return renderServiceAgreement(dsl);
  }
}
