import { createHash } from "node:crypto";
import { mkdir, readFile, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { block, assign } from "@office-dsl/dsl-artifact-renderer";
import { compareSubset, stableJson } from "@office-dsl/regression-runner";
import { renderTextAsMinimalPdf } from "@office-dsl/pdf-generator";

export const CHAT_SCENARIO_VERSION = "example-chat.scenario.v1";
export type ChatParty = "user1" | "user2";
export type ChatOutcome = "AGREED" | "CANCELLED" | "NEGOTIATING";

export interface ChatScenarioManifest {
  version: typeof CHAT_SCENARIO_VERSION;
  id: string;
  title: string;
  input: { chat: string };
  expected: { summary: string };
}

export interface ChatLine {
  event: number;
  line: number;
  author: ChatParty;
  text: string;
  raw: string;
}

export interface ContractValue {
  value: string;
  source: { party: ChatParty; line: number; text: string };
  acceptedBy: ChatParty[];
  rejectedBy: ChatParty[];
}

export interface PartyContract {
  party: ChatParty;
  fields: Record<string, ContractValue>;
  changes: Array<{ line: number; field: string; previous: string; next: string }>;
}

export interface Conflict {
  field: string;
  values: ContractValue[];
}

export interface MergedContract {
  version: "merged-contract.v1";
  fields: Record<string, ContractValue>;
  missing: string[];
  conflicts: Conflict[];
  hash: string;
}

export interface ApprovalRecord {
  party: ChatParty;
  approvedHash: string;
  line: number;
  status: "ACTIVE" | "INVALIDATED";
  invalidatedByLine?: number;
  reason?: string;
}

export interface ChatRunSummary {
  id: string;
  outcome: ChatOutcome;
  eventCount: number;
  finalCreated: boolean;
  finalHash: string | null;
  approvals: ApprovalRecord[];
  conflicts: Array<{ field: string; values: string[] }>;
  missing: string[];
  cancelledReason: string | null;
}

export interface ChatRunResult {
  id: string;
  scenarioDir: string;
  generatedDir: string;
  ok: boolean;
  failures: string[];
  summary: ChatRunSummary;
}

interface IntentUpdate {
  field: string;
  value: string;
}

interface IntentArtifact {
  version: "chat-intent.v1";
  event: number;
  line: number;
  author: ChatParty;
  text: string;
  updates: IntentUpdate[];
  approval: boolean;
  cancellation: boolean;
}

const requiredFields = [
  "service",
  "price",
  "deadline",
  "acceptanceCriteria",
  "completionCondition",
  "paymentCondition"
];

export async function discoverChatScenarios(repoRoot: string): Promise<string[]> {
  const { readdir } = await import("node:fs/promises");
  const examplesDir = path.join(repoRoot, "examples-chat");
  const entries = await readdir(examplesDir, { withFileTypes: true });
  return entries
    .filter((entry) => entry.isDirectory())
    .map((entry) => path.join(examplesDir, entry.name))
    .sort((a, b) => path.basename(a).localeCompare(path.basename(b)));
}

export async function loadChatScenarioManifest(scenarioDir: string): Promise<ChatScenarioManifest> {
  const manifest = JSON.parse(
    await readFile(path.join(scenarioDir, "scenario.json"), "utf8")
  ) as ChatScenarioManifest;
  validateChatScenarioManifest(manifest, scenarioDir);
  return manifest;
}

export function validateChatScenarioManifest(
  manifest: ChatScenarioManifest,
  scenarioDir = "."
): void {
  if (manifest.version !== CHAT_SCENARIO_VERSION) {
    throw new Error(`${scenarioDir}: chat scenario version must be ${CHAT_SCENARIO_VERSION}`);
  }
  if (!manifest.id || !manifest.title) throw new Error(`${scenarioDir}: id and title are required`);
  if (!manifest.input?.chat) throw new Error(`${scenarioDir}: input.chat is required`);
  if (!manifest.expected?.summary) throw new Error(`${scenarioDir}: expected.summary is required`);
}

export function parseChat(text: string): ChatLine[] {
  const events: ChatLine[] = [];
  const lines = text.split(/\r?\n/);
  for (let index = 0; index < lines.length; index += 1) {
    const raw = lines[index] ?? "";
    if (!raw.trim()) continue;
    const match = raw.match(/^@(user1|user2)\s+(.+)$/);
    if (!match) throw new Error(`Invalid chat line ${index + 1}: ${raw}`);
    events.push({
      event: events.length + 1,
      line: index + 1,
      author: match[1] as ChatParty,
      text: match[2].trim(),
      raw
    });
  }
  return events;
}

export async function runChatScenario(options: {
  repoRoot: string;
  scenarioDir: string;
  generatedRoot?: string;
}): Promise<ChatRunResult> {
  const manifest = await loadChatScenarioManifest(options.scenarioDir);
  const generatedDir = options.generatedRoot ?? path.join(options.scenarioDir, "generated");
  await rm(generatedDir, { recursive: true, force: true });
  await mkdir(generatedDir, { recursive: true });

  const chat = parseChat(
    await readFile(path.join(options.scenarioDir, manifest.input.chat), "utf8")
  );
  const user1 = emptyPartyContract("user1");
  const user2 = emptyPartyContract("user2");
  const approvals: ApprovalRecord[] = [];
  const diffSummary: string[] = [];
  let merged = mergeContracts(user1, user2);
  let outcome: ChatOutcome = "NEGOTIATING";
  let cancelledReason: string | null = null;

  for (const event of chat) {
    const previousHash = merged.hash;
    const intent = interpretLine(event);
    const diffLines: string[] = [];

    if (outcome === "CANCELLED") {
      diffLines.push(`Line ${event.line} rejected because conversation is already cancelled.`);
    } else if (intent.cancellation) {
      outcome = "CANCELLED";
      cancelledReason = event.text;
      diffLines.push(`Conversation cancelled by ${event.author} on line ${event.line}.`);
      invalidateApprovals(approvals, event.line, "conversation cancelled");
    } else {
      const party = event.author === "user1" ? user1 : user2;
      applyUpdates(party, intent, diffLines);
      merged = mergeContracts(user1, user2);
      if (
        merged.hash !== previousHash &&
        approvals.some((approval) => approval.status === "ACTIVE")
      ) {
        invalidateApprovals(approvals, event.line, "merged contract changed after approval");
        diffLines.push("Existing approvals invalidated because merged contract hash changed.");
      }
      if (intent.approval) {
        if (merged.conflicts.length || merged.missing.length) {
          diffLines.push("Approval ignored because merged contract is incomplete or conflicting.");
        } else {
          approvals.push({
            party: event.author,
            approvedHash: merged.hash,
            line: event.line,
            status: "ACTIVE"
          });
          diffLines.push(`${event.author} approved merged contract hash ${merged.hash}.`);
        }
      }
      if (hasBothApprovalsForCurrentHash(approvals, merged.hash)) outcome = "AGREED";
    }

    const status = createStatus(outcome, merged, approvals, cancelledReason);
    await writeEventArtifacts(
      generatedDir,
      event,
      intent,
      event.author === "user1" ? user1 : user2,
      merged,
      diffLines,
      status
    );
    diffSummary.push(
      `## ${event.event}. ${event.author} line ${event.line}\n\n${diffLines.join("\n") || "No contract change."}`
    );
  }

  if (outcome === "AGREED") {
    await writeFinalArtifacts(generatedDir, merged, approvals, diffSummary);
  } else {
    await mkdir(path.join(generatedDir, "final"), { recursive: true });
    await writeFile(
      path.join(generatedDir, "final", "cancelled-summary.md"),
      `# Conversation ${outcome}\n\n${cancelledReason ?? "No bilateral agreement reached."}\n`,
      "utf8"
    );
  }

  const summary = createSummary(
    manifest.id,
    outcome,
    chat.length,
    merged,
    approvals,
    cancelledReason
  );
  await writeDsl(path.join(generatedDir, "summary.dsl.hcl"), renderSummaryDsl(summary));
  const failures = await compareExpectedSummary(options.scenarioDir, manifest, summary);
  return {
    id: manifest.id,
    scenarioDir: options.scenarioDir,
    generatedDir,
    ok: failures.length === 0,
    failures,
    summary
  };
}

function emptyPartyContract(party: ChatParty): PartyContract {
  return { party, fields: {}, changes: [] };
}

function interpretLine(event: ChatLine): IntentArtifact {
  const updates: IntentUpdate[] = [];
  const text = event.text;
  const normalized = normalizeForMatch(text);

  capture(updates, "price", text.match(/(\d[\d ]*)\s*PLN/i)?.[0]?.replace(/\s+/g, " "));
  capture(
    updates,
    "deadline",
    normalized.match(/(?:termin(?:em)? do|termin do|do)\s+([^,.]+?)(?:\.|,|$)/i)?.[1]?.trim()
  );
  if (normalized.includes("strona internetowa") || normalized.includes("strone internetowa")) {
    capture(updates, "service", "strona internetowa");
  }
  const role = normalized.match(/(?:stanowisko|rola)[:\s]+([^,.]+?)(?:\.|,|$)/i)?.[1]?.trim();
  capture(updates, "service", role);

  const acceptance = normalized
    .match(/(?:odbior|akceptacja|kryteria odbioru)[:\s]+([^,.]+?)(?:\.|,|$)/i)?.[1]
    ?.trim();
  capture(updates, "acceptanceCriteria", acceptance);
  if (normalized.includes("dziala formularz")) {
    capture(updates, "acceptanceCriteria", "dziala formularz kontaktowy");
  }
  const completion = normalized
    .match(/(?:gotowe gdy|wykonane gdy|uznajemy za wykonane)[:\s]+([^,.]+?)(?:\.|,|$)/i)?.[1]
    ?.trim();
  capture(updates, "completionCondition", completion);
  if (normalized.includes("wdrozona") || normalized.includes("wdrozone")) {
    capture(updates, "completionCondition", "strona wdrozona na hostingu");
  }
  const payment = normalized.match(/(?:platnosc|zaplata)[:\s]+([^,.]+?)(?:\.|,|$)/i)?.[1]?.trim();
  capture(updates, "paymentCondition", payment);
  if (normalized.includes("po odbiorze")) capture(updates, "paymentCondition", "po odbiorze");
  if (normalized.includes("po akceptacji")) capture(updates, "paymentCondition", "po akceptacji");

  return {
    version: "chat-intent.v1",
    event: event.event,
    line: event.line,
    author: event.author,
    text: event.text,
    updates: uniqueUpdates(updates),
    approval: isWholeContractApproval(text),
    cancellation: isCancellation(text)
  };
}

function normalizeForMatch(value: string): string {
  return value
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/ł/g, "l");
}

function capture(updates: IntentUpdate[], field: string, value: string | undefined): void {
  if (value?.trim()) updates.push({ field, value: normalizeValue(value) });
}

function normalizeValue(value: string): string {
  return value.trim().replace(/\s+/g, " ").replace(/[.]$/, "");
}

function uniqueUpdates(updates: IntentUpdate[]): IntentUpdate[] {
  const byField = new Map<string, IntentUpdate>();
  for (const update of updates) byField.set(update.field, update);
  return [...byField.values()];
}

function isWholeContractApproval(text: string): boolean {
  return /^(zgoda|akceptuje caly kontrakt|zgadzam sie na aktualne warunki)[.!]?$/i.test(
    normalizeForMatch(text).trim()
  );
}

function isCancellation(text: string): boolean {
  return /(rezygnuje|koncze rozmowy|nie akceptuje tych warunkow|zrywam)/i.test(
    normalizeForMatch(text)
  );
}

function applyUpdates(contract: PartyContract, intent: IntentArtifact, diffLines: string[]): void {
  for (const update of intent.updates) {
    const previous = contract.fields[update.field];
    contract.fields[update.field] = {
      value: update.value,
      source: { party: contract.party, line: intent.line, text: intent.text },
      acceptedBy: [],
      rejectedBy: previous && previous.value !== update.value ? [contract.party] : []
    };
    if (!previous) diffLines.push(`Added ${update.field}: ${update.value}.`);
    else if (previous.value !== update.value) {
      contract.changes.push({
        line: intent.line,
        field: update.field,
        previous: previous.value,
        next: update.value
      });
      diffLines.push(`Changed ${update.field}: ${previous.value} -> ${update.value}.`);
    }
  }
}

function mergeContracts(user1: PartyContract, user2: PartyContract): MergedContract {
  const fields: Record<string, ContractValue> = {};
  const conflicts: Conflict[] = [];
  for (const field of requiredFields) {
    const left = user1.fields[field];
    const right = user2.fields[field];
    if (left && right && left.value !== right.value)
      conflicts.push({ field, values: [left, right] });
    else if (left && right)
      fields[field] = { ...right, acceptedBy: ["user1", "user2"], rejectedBy: [] };
    else if (left) fields[field] = left;
    else if (right) fields[field] = right;
  }
  const missing = requiredFields.filter(
    (field) => !fields[field] && !conflicts.some((conflict) => conflict.field === field)
  );
  const base = { version: "merged-contract.v1" as const, fields, missing, conflicts };
  return { ...base, hash: hashStable(base) };
}

function hashStable(value: unknown): string {
  return createHash("sha256")
    .update(`${stableJson(value)}\n`)
    .digest("hex");
}

function invalidateApprovals(approvals: ApprovalRecord[], line: number, reason: string): void {
  for (const approval of approvals) {
    if (approval.status === "ACTIVE") {
      approval.status = "INVALIDATED";
      approval.invalidatedByLine = line;
      approval.reason = reason;
    }
  }
}

function hasBothApprovalsForCurrentHash(approvals: ApprovalRecord[], hash: string): boolean {
  const active = approvals.filter(
    (approval) => approval.status === "ACTIVE" && approval.approvedHash === hash
  );
  return (
    active.some((approval) => approval.party === "user1") &&
    active.some((approval) => approval.party === "user2")
  );
}

function createStatus(
  outcome: ChatOutcome,
  merged: MergedContract,
  approvals: ApprovalRecord[],
  cancelledReason: string | null
): Record<string, unknown> {
  return {
    outcome,
    currentHash: merged.hash,
    missing: merged.missing,
    conflicts: merged.conflicts.map((conflict) => ({
      field: conflict.field,
      values: conflict.values.map((value) => value.value)
    })),
    approvals,
    finalAllowed: outcome === "AGREED",
    cancelledReason
  };
}

async function writeEventArtifacts(
  generatedDir: string,
  event: ChatLine,
  intent: IntentArtifact,
  partyContract: PartyContract,
  merged: MergedContract,
  diffLines: string[],
  status: Record<string, unknown>
): Promise<void> {
  const eventDir = generatedDir;
  await mkdir(eventDir, { recursive: true });
  await writeFile(
    path.join(eventDir, `${eventPrefix(event)}.prompt.txt`),
    `${event.raw}\n`,
    "utf8"
  );
  await writeDsl(
    path.join(eventDir, `${eventPrefix(event)}.intent-contract.dsl.hcl`),
    renderIntentDsl(intent)
  );
  await writeDsl(
    path.join(eventDir, `${eventPrefix(event)}.party-contract.dsl.hcl`),
    renderPartyContractDsl(partyContract)
  );
  await writeDsl(
    path.join(eventDir, `${eventPrefix(event)}.merged-contract.dsl.hcl`),
    renderMergedContractDsl(merged)
  );
  await writeFile(
    path.join(eventDir, `${eventPrefix(event)}.diff.md`),
    `${diffLines.join("\n") || "No contract change."}\n`,
    "utf8"
  );
  await writeDsl(
    path.join(eventDir, `${eventPrefix(event)}.status.dsl.hcl`),
    renderStatusDsl(status)
  );
}

function eventPrefix(event: ChatLine): string {
  return `${String(event.event).padStart(3, "0")}-${event.author}`;
}

async function writeFinalArtifacts(
  generatedDir: string,
  merged: MergedContract,
  approvals: ApprovalRecord[],
  diffSummary: string[]
): Promise<void> {
  const finalDir = path.join(generatedDir, "final");
  await mkdir(finalDir, { recursive: true });
  const finalContract = {
    version: "final-contract.v1",
    status: "AGREED",
    hash: merged.hash,
    merged
  };
  await writeDsl(
    path.join(finalDir, "final-contract.dsl.hcl"),
    renderFinalContractDsl(finalContract)
  );
  const markdown = renderContractMarkdown(finalContract);
  await writeFile(path.join(finalDir, "contract.md"), markdown, "utf8");
  await writeFile(path.join(finalDir, "contract.pdf"), renderTextAsMinimalPdf(markdown), "binary");
  await writeDsl(
    path.join(finalDir, "approvals.dsl.hcl"),
    renderApprovalsDsl(merged.hash, approvals)
  );
  await writeFile(path.join(finalDir, "diff-summary.md"), `${diffSummary.join("\n\n")}\n`, "utf8");
  await writeDsl(path.join(finalDir, "annex.dsl.hcl"), renderAnnexDsl(finalContract));
}

function renderContractMarkdown(finalContract: {
  status: string;
  hash: string;
  merged: MergedContract;
}): string {
  const lines = [
    "# Contract",
    "",
    `Status: ${finalContract.status}`,
    `Hash: ${finalContract.hash}`,
    "",
    "## Terms"
  ];
  for (const field of requiredFields) {
    lines.push(`- ${field}: ${finalContract.merged.fields[field]?.value ?? "MISSING"}`);
  }
  lines.push("", "## Annex", "See annex.dsl.hcl for the canonical DSL representation.", "");
  return lines.join("\n");
}

export function validateChatDslText(text: string): void {
  const trimmed = text.trimStart();
  if (!trimmed.startsWith("document ")) throw new Error("DSL/HCL must start with a document block");
  if (/^\s*[\[{]/.test(text))
    throw new Error("DSL/HCL text must not use JSON object or array syntax as the document");
  if (!hasBalancedBraces(text)) throw new Error("DSL/HCL braces are not balanced");
  if ((text.match(/"/g)?.length ?? 0) % 2 !== 0) throw new Error("DSL/HCL quotes are not balanced");
  const allowed =
    /^(document|field|conflict|change|approval)\s+|^(version|type|event|line|author|text|updates|approval|cancellation|party|value|source_party|source_line|accepted_by|rejected_by|hash|status|missing|include|assert|annex|from|to|id|outcome|event_count|final_created|final_hash|cancelled_reason|current_hash|final_allowed|approved_hash|invalidated_by_line|reason)\s*=/;
  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line === "}" || line.startsWith("#")) continue;
    if (!allowed.test(line)) throw new Error(`Unsupported DSL/HCL line: ${rawLine}`);
  }
}

function renderIntentDsl(intent: IntentArtifact): string {
  return block("document", "CHAT_INTENT", [
    assign("version", 1),
    assign("type", intent.version),
    assign("event", intent.event),
    assign("line", intent.line),
    assign("author", partyToken(intent.author)),
    assign("text", intent.text),
    assign(
      "updates",
      intent.updates.map((update) => `${fieldToken(update.field)}=${update.value}`)
    ),
    assign("approval", intent.approval),
    assign("cancellation", intent.cancellation)
  ]);
}

function renderPartyContractDsl(contract: PartyContract): string {
  const body = [assign("version", 1), assign("party", partyToken(contract.party))];
  for (const [field, value] of Object.entries(contract.fields).sort(([a], [b]) =>
    a.localeCompare(b)
  )) {
    body.push(renderContractValue(field, value));
  }
  for (const change of contract.changes) {
    body.push(
      block("change", fieldToken(change.field), [
        assign("line", change.line),
        assign("from", change.previous),
        assign("to", change.next)
      ])
    );
  }
  return block("document", "PARTY_CONTRACT", body);
}

function renderMergedContractDsl(merged: MergedContract): string {
  const body = [assign("version", 1), assign("type", merged.version), assign("hash", merged.hash)];
  for (const field of requiredFields) {
    const value = merged.fields[field];
    if (value) body.push(renderContractValue(field, value));
  }
  body.push(assign("missing", merged.missing.map(fieldToken)));
  for (const conflict of merged.conflicts) {
    body.push(
      block(
        "conflict",
        fieldToken(conflict.field),
        conflict.values.map((value) =>
          block("field", fieldToken(conflict.field), [
            assign("value", value.value),
            assign("source_party", partyToken(value.source.party)),
            assign("source_line", value.source.line)
          ])
        )
      )
    );
  }
  return block("document", "MERGED_CONTRACT", body);
}

function renderFinalContractDsl(finalContract: {
  status: string;
  hash: string;
  merged: MergedContract;
}): string {
  const body = [
    assign("version", 1),
    assign("status", finalContract.status),
    assign("hash", finalContract.hash),
    assign("include", "MERGED_CONTRACT")
  ];
  for (const field of requiredFields) {
    const value = finalContract.merged.fields[field];
    if (value) body.push(renderContractValue(field, value));
  }
  body.push(assign("assert", ["APPROVALS = [USER1, USER2]", "FINAL_ARTIFACTS_ALLOWED"]));
  return block("document", "FINAL_CONTRACT", body);
}

function renderAnnexDsl(finalContract: {
  status: string;
  hash: string;
  merged: MergedContract;
}): string {
  const body = [
    assign("version", 1),
    assign("annex", "FINAL_CONTRACT"),
    assign("hash", finalContract.hash),
    assign("status", finalContract.status),
    assign("include", "MERGED_CONTRACT")
  ];
  for (const field of requiredFields) {
    const value = finalContract.merged.fields[field];
    if (value) body.push(renderContractValue(field, value));
  }
  return block("document", "CONTRACT_ANNEX", body);
}

function renderContractValue(field: string, value: ContractValue): string {
  return block("field", fieldToken(field), [
    assign("value", value.value),
    assign("source_party", partyToken(value.source.party)),
    assign("source_line", value.source.line),
    assign("text", value.source.text),
    assign("accepted_by", value.acceptedBy.map(partyToken)),
    assign("rejected_by", value.rejectedBy.map(partyToken))
  ]);
}

async function writeDsl(file: string, text: string): Promise<void> {
  validateChatDslText(text);
  await writeFile(file, text, "utf8");
}

function hasBalancedBraces(text: string): boolean {
  let depth = 0;
  for (const char of text) {
    if (char === "{") depth += 1;
    if (char === "}") depth -= 1;
    if (depth < 0) return false;
  }
  return depth === 0;
}

function partyToken(party: ChatParty): string {
  return party.toUpperCase();
}

function fieldToken(field: string): string {
  return field.replace(/[A-Z]/g, (letter) => `_${letter}`).toUpperCase();
}
function createSummary(
  id: string,
  outcome: ChatOutcome,
  eventCount: number,
  merged: MergedContract,
  approvals: ApprovalRecord[],
  cancelledReason: string | null
): ChatRunSummary {
  return {
    id,
    outcome,
    eventCount,
    finalCreated: outcome === "AGREED",
    finalHash: outcome === "AGREED" ? merged.hash : null,
    approvals,
    conflicts: merged.conflicts.map((conflict) => ({
      field: conflict.field,
      values: conflict.values.map((value) => value.value)
    })),
    missing: merged.missing,
    cancelledReason
  };
}

async function compareExpectedSummary(
  scenarioDir: string,
  manifest: ChatScenarioManifest,
  actual: ChatRunSummary
): Promise<string[]> {
  const expected = JSON.parse(
    await readFile(path.join(scenarioDir, manifest.expected.summary), "utf8")
  ) as Partial<ChatRunSummary>;
  const failures: string[] = [];
  compareSubset(failures, "summary", expected, actual);
  return failures;
}

function renderSummaryDsl(summary: ChatRunSummary): string {
  const body = [
    assign("id", summary.id),
    assign("outcome", summary.outcome),
    assign("event_count", summary.eventCount),
    assign("final_created", summary.finalCreated)
  ];
  if (summary.finalHash) body.push(assign("final_hash", summary.finalHash));
  if (summary.cancelledReason) body.push(assign("cancelled_reason", summary.cancelledReason));
  body.push(assign("missing", summary.missing.map(fieldToken)));
  for (const conflict of summary.conflicts) {
    body.push(block("conflict", fieldToken(conflict.field), [assign("value", conflict.values)]));
  }
  for (const approval of summary.approvals) body.push(renderApprovalDsl(approval));
  return block("document", "CHAT_SUMMARY", body);
}

function renderStatusDsl(status: Record<string, unknown>): string {
  const body = [
    assign("outcome", String(status.outcome)),
    assign("current_hash", String(status.currentHash)),
    assign("missing", (status.missing as string[]).map(fieldToken)),
    assign("final_allowed", Boolean(status.finalAllowed))
  ];
  if (status.cancelledReason) body.push(assign("cancelled_reason", String(status.cancelledReason)));
  for (const conflict of status.conflicts as Array<{ field: string; values: string[] }>) {
    body.push(block("conflict", fieldToken(conflict.field), [assign("value", conflict.values)]));
  }
  for (const approval of status.approvals as ApprovalRecord[])
    body.push(renderApprovalDsl(approval));
  return block("document", "CHAT_STATUS", body);
}

function renderApprovalsDsl(hash: string, approvals: ApprovalRecord[]): string {
  const active = approvals.filter((approval) => approval.status === "ACTIVE");
  const body = [assign("status", active.length > 0 ? "APPROVED" : "PENDING"), assign("hash", hash)];
  for (const approval of active) body.push(renderApprovalDsl(approval));
  return block("document", "CHAT_APPROVALS", body);
}

function renderApprovalDsl(approval: ApprovalRecord): string {
  const body = [
    assign("party", partyToken(approval.party)),
    assign("approved_hash", approval.approvedHash),
    assign("line", approval.line),
    assign("status", approval.status)
  ];
  if (approval.invalidatedByLine)
    body.push(assign("invalidated_by_line", approval.invalidatedByLine));
  if (approval.reason) body.push(assign("reason", approval.reason));
  return block("approval", partyToken(approval.party), body);
}
