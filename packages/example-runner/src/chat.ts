import { createHash } from "node:crypto";
import { mkdir, readFile, rm, writeFile } from "node:fs/promises";
import path from "node:path";

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
  const generatedDir =
    options.generatedRoot ??
    path.join(options.repoRoot, ".office-dsl", "generated", "examples-chat", manifest.id);
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
  await writeJson(path.join(generatedDir, "summary.json"), summary);
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

function stableJson(value: unknown): string {
  return JSON.stringify(sortValue(value), null, 2);
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
  const eventDir = path.join(generatedDir, event.author, String(event.event).padStart(3, "0"));
  await mkdir(eventDir, { recursive: true });
  await writeFile(path.join(eventDir, "prompt.txt"), `${event.raw}\n`, "utf8");
  await writeDsl(path.join(eventDir, "intent-contract.dsl"), renderIntentDsl(intent));
  await writeDsl(path.join(eventDir, "party-contract.dsl"), renderPartyContractDsl(partyContract));
  await writeDsl(path.join(eventDir, "merged-contract.dsl"), renderMergedContractDsl(merged));
  await writeFile(
    path.join(eventDir, "diff.md"),
    `${diffLines.join("\n") || "No contract change."}\n`,
    "utf8"
  );
  await writeJson(path.join(eventDir, "status.json"), status);
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
  await writeDsl(path.join(finalDir, "final-contract.dsl"), renderFinalContractDsl(finalContract));
  const markdown = renderContractMarkdown(finalContract);
  await writeFile(path.join(finalDir, "contract.md"), markdown, "utf8");
  await writeFile(path.join(finalDir, "contract.pdf"), renderMinimalPdf(markdown), "binary");
  await writeJson(path.join(finalDir, "approvals.json"), {
    status: "APPROVED",
    hash: merged.hash,
    approvals: approvals.filter((approval) => approval.status === "ACTIVE")
  });
  await writeFile(path.join(finalDir, "diff-summary.md"), `${diffSummary.join("\n\n")}\n`, "utf8");
  await writeDsl(path.join(finalDir, "annex.dsl"), renderAnnexDsl(finalContract));
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
  lines.push("", "## Annex", "See annex.dsl for the canonical DSL representation.", "");
  return lines.join("\n");
}

function renderMinimalPdf(markdown: string): string {
  const text = markdown
    .split(/\r?\n/)
    .filter(Boolean)
    .slice(0, 24)
    .map((line) => line.replace(/[()\\]/g, ""));
  const content = `BT /F1 10 Tf 50 780 Td ${text.map((line, index) => `${index ? "0 -14 Td " : ""}(${line}) Tj`).join(" ")} ET`;
  const objects = [
    "<< /Type /Catalog /Pages 2 0 R >>",
    "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
    "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
    "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    `<< /Length ${Buffer.byteLength(content, "binary")} >>\nstream\n${content}\nendstream`
  ];
  let pdf = "%PDF-1.4\n";
  const offsets = [0];
  objects.forEach((object, index) => {
    offsets.push(Buffer.byteLength(pdf, "binary"));
    pdf += `${index + 1} 0 obj\n${object}\nendobj\n`;
  });
  const xrefOffset = Buffer.byteLength(pdf, "binary");
  pdf += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`;
  for (const offset of offsets.slice(1)) pdf += `${String(offset).padStart(10, "0")} 00000 n \n`;
  pdf += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF\n`;
  return pdf;
}

export function validateChatDslText(text: string): void {
  const lines = text.split(/\r?\n/).filter((line) => line.trim() && !line.trim().startsWith("#"));
  if (!lines[0]?.startsWith("DOCUMENT ")) throw new Error("DSL must start with DOCUMENT");
  if (/^\s*[\[{]/.test(text)) throw new Error("DSL text must not use JSON object or array syntax");
  const allowed =
    /^(DOCUMENT|VERSION|TYPE|EVENT|LINE|AUTHOR|TEXT|UPDATE|APPROVAL|CANCELLATION|PARTY|FIELD|VALUE|SOURCE|ACCEPTED_BY|REJECTED_BY|END_FIELD|CHANGE|HASH|STATUS|MISSING|CONFLICT|END_CONFLICT|INCLUDE|ASSERT|ANNEX|END_DOCUMENT)(\b|\s|$)/;
  for (const line of lines) {
    if (!allowed.test(line.trim())) throw new Error(`Unsupported DSL line: ${line}`);
    if ((line.match(/"/g)?.length ?? 0) % 2 !== 0)
      throw new Error(`Unbalanced quotes in DSL line: ${line}`);
  }
}

function renderIntentDsl(intent: IntentArtifact): string {
  const lines = [
    "DOCUMENT CHAT_INTENT",
    "VERSION 1",
    `TYPE ${intent.version}`,
    `EVENT ${intent.event}`,
    `LINE ${intent.line}`,
    `AUTHOR ${partyToken(intent.author)}`,
    `TEXT ${quoteDsl(intent.text)}`
  ];
  for (const update of intent.updates)
    lines.push(`UPDATE ${fieldToken(update.field)} ${quoteDsl(update.value)}`);
  lines.push(`APPROVAL ${boolToken(intent.approval)}`);
  lines.push(`CANCELLATION ${boolToken(intent.cancellation)}`);
  lines.push("END_DOCUMENT");
  return `${lines.join("\n")}\n`;
}

function renderPartyContractDsl(contract: PartyContract): string {
  const lines = ["DOCUMENT PARTY_CONTRACT", "VERSION 1", `PARTY ${partyToken(contract.party)}`];
  for (const [field, value] of Object.entries(contract.fields).sort(([a], [b]) =>
    a.localeCompare(b)
  )) {
    lines.push(`FIELD ${fieldToken(field)}`);
    lines.push(`VALUE ${quoteDsl(value.value)}`);
    lines.push(`SOURCE ${partyToken(value.source.party)} LINE ${value.source.line}`);
    lines.push(`TEXT ${quoteDsl(value.source.text)}`);
    lines.push(`ACCEPTED_BY ${listToken(value.acceptedBy.map(partyToken))}`);
    lines.push(`REJECTED_BY ${listToken(value.rejectedBy.map(partyToken))}`);
    lines.push("END_FIELD");
  }
  for (const change of contract.changes) {
    lines.push(
      `CHANGE ${fieldToken(change.field)} LINE ${change.line} FROM ${quoteDsl(change.previous)} TO ${quoteDsl(change.next)}`
    );
  }
  lines.push("END_DOCUMENT");
  return `${lines.join("\n")}\n`;
}

function renderMergedContractDsl(merged: MergedContract): string {
  const lines = [
    "DOCUMENT MERGED_CONTRACT",
    "VERSION 1",
    `TYPE ${merged.version}`,
    `HASH ${quoteDsl(merged.hash)}`
  ];
  for (const field of requiredFields) {
    const value = merged.fields[field];
    if (!value) continue;
    lines.push(...renderContractValue(field, value));
  }
  lines.push(`MISSING ${listToken(merged.missing.map(fieldToken))}`);
  for (const conflict of merged.conflicts) {
    lines.push(`CONFLICT ${fieldToken(conflict.field)}`);
    for (const value of conflict.values) {
      lines.push(
        `VALUE ${quoteDsl(value.value)} SOURCE ${partyToken(value.source.party)} LINE ${value.source.line}`
      );
    }
    lines.push("END_CONFLICT");
  }
  lines.push("END_DOCUMENT");
  return `${lines.join("\n")}\n`;
}

function renderFinalContractDsl(finalContract: {
  status: string;
  hash: string;
  merged: MergedContract;
}): string {
  const lines = [
    "DOCUMENT FINAL_CONTRACT",
    "VERSION 1",
    `STATUS ${finalContract.status}`,
    `HASH ${quoteDsl(finalContract.hash)}`,
    "INCLUDE MERGED_CONTRACT"
  ];
  for (const field of requiredFields) {
    const value = finalContract.merged.fields[field];
    if (value) lines.push(...renderContractValue(field, value));
  }
  lines.push("ASSERT APPROVALS = [USER1, USER2]");
  lines.push("ASSERT FINAL_ARTIFACTS_ALLOWED");
  lines.push("END_DOCUMENT");
  return `${lines.join("\n")}\n`;
}

function renderAnnexDsl(finalContract: {
  status: string;
  hash: string;
  merged: MergedContract;
}): string {
  const lines = [
    "DOCUMENT CONTRACT_ANNEX",
    "VERSION 1",
    `ANNEX FINAL_CONTRACT HASH ${quoteDsl(finalContract.hash)}`,
    `STATUS ${finalContract.status}`,
    `HASH ${quoteDsl(finalContract.merged.hash)}`,
    "INCLUDE MERGED_CONTRACT"
  ];
  for (const field of requiredFields) {
    const value = finalContract.merged.fields[field];
    if (value) lines.push(...renderContractValue(field, value));
  }
  lines.push("END_DOCUMENT");
  return `${lines.join("\n")}\n`;
}

function renderContractValue(field: string, value: ContractValue): string[] {
  return [
    `FIELD ${fieldToken(field)}`,
    `VALUE ${quoteDsl(value.value)}`,
    `SOURCE ${partyToken(value.source.party)} LINE ${value.source.line}`,
    `TEXT ${quoteDsl(value.source.text)}`,
    `ACCEPTED_BY ${listToken(value.acceptedBy.map(partyToken))}`,
    `REJECTED_BY ${listToken(value.rejectedBy.map(partyToken))}`,
    "END_FIELD"
  ];
}

async function writeDsl(file: string, text: string): Promise<void> {
  validateChatDslText(text);
  await writeFile(file, text, "utf8");
}

function quoteDsl(value: string): string {
  return `"${value.replace(/\\/g, "\\\\").replace(/"/g, '\\"')}"`;
}

function partyToken(party: ChatParty): string {
  return party.toUpperCase();
}

function fieldToken(field: string): string {
  return field.replace(/[A-Z]/g, (letter) => `_${letter}`).toUpperCase();
}

function boolToken(value: boolean): string {
  return value ? "TRUE" : "FALSE";
}

function listToken(values: string[]): string {
  return `[${values.join(", ")}]`;
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

function compareSubset(
  failures: string[],
  label: string,
  expected: unknown,
  actual: unknown
): void {
  if (Array.isArray(expected)) {
    if (stableJson(expected) !== stableJson(actual))
      failures.push(
        `${label} mismatch\nexpected: ${stableJson(expected)}\nactual:   ${stableJson(actual)}`
      );
    return;
  }
  if (expected && typeof expected === "object") {
    for (const [key, value] of Object.entries(expected))
      compareSubset(
        failures,
        `${label}.${key}`,
        value,
        (actual as Record<string, unknown> | undefined)?.[key]
      );
    return;
  }
  if (expected !== actual)
    failures.push(`${label} expected ${String(expected)} but got ${String(actual)}`);
}

async function writeJson(file: string, value: unknown): Promise<void> {
  await writeFile(file, `${stableJson(value)}\n`, "utf8");
}
