import { createHash } from "node:crypto";
import { existsSync } from "node:fs";
import { mkdir, readdir, readFile, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import {
  INTENT_CONTRACT_DSL_VERSION,
  createField,
  validateIntentContractDsl,
  type IntentContractDsl,
  type SourceReference
} from "../../intent-contract-model/src/index.js";
import { runChatScenario, type ChatOutcome, type ChatRunResult } from "./chat.js";

export const RECRUITMENT_SCENARIO_VERSION = "example-recruitment.scenario.v1";
export type RecruitmentOutcome = "ACCEPTED" | "REJECTED";
export type RecruitmentSourceKind = "offer-md" | "cv-md" | "cv-pdf-text" | "cv-pdf-ocr";

export interface RecruitmentScenarioManifest {
  version: typeof RECRUITMENT_SCENARIO_VERSION;
  id: string;
  title: string;
  expected: { summary: string };
}

export interface RecruitmentSourceDocument {
  id: string;
  kind: RecruitmentSourceKind;
  relativePath: string;
  text: string;
  extraction: "markdown" | "pdf-text" | "ocr-mock";
  references: SourceReference[];
}

export interface RecruitmentProposal {
  candidateId: string;
  candidateName: string;
  role: string | null;
  salary: { amount: number; currency: string } | null;
  startDate: string | null;
  skills: string[];
  sourceIds: string[];
  hash: string;
}

export interface RecruitmentCandidateSummary {
  id: string;
  outcome: RecruitmentOutcome;
  chatOutcome: ChatOutcome;
  finalCreated: boolean;
  contractPath: string | null;
  proposalHash: string;
  sourceDocuments: Array<{ id: string; kind: RecruitmentSourceKind; extraction: string }>;
}

export interface RecruitmentRunSummary {
  id: string;
  candidateCount: number;
  accepted: string[];
  rejected: string[];
  candidates: RecruitmentCandidateSummary[];
}

export interface RecruitmentRunResult {
  id: string;
  scenarioDir: string;
  generatedDir: string;
  ok: boolean;
  failures: string[];
  summary: RecruitmentRunSummary;
}

interface CandidateRunContext {
  id: string;
  dir: string;
  outDir: string;
  generatedDir: string;
  sources: RecruitmentSourceDocument[];
  proposal: RecruitmentProposal;
  dsl: IntentContractDsl;
  chat: ChatRunResult;
}

export async function discoverRecruitmentScenarios(repoRoot: string): Promise<string[]> {
  const examplesDir = path.join(repoRoot, "examples-recruitment");
  if (!existsSync(examplesDir)) return [];
  const entries = await readdir(examplesDir, { withFileTypes: true });
  return entries
    .filter((entry) => entry.isDirectory())
    .map((entry) => path.join(examplesDir, entry.name))
    .sort((a, b) => path.basename(a).localeCompare(path.basename(b)));
}

export async function loadRecruitmentScenarioManifest(
  scenarioDir: string
): Promise<RecruitmentScenarioManifest> {
  const manifest = JSON.parse(
    await readFile(path.join(scenarioDir, "scenario.json"), "utf8")
  ) as RecruitmentScenarioManifest;
  validateRecruitmentScenarioManifest(manifest, scenarioDir);
  return manifest;
}

export function validateRecruitmentScenarioManifest(
  manifest: RecruitmentScenarioManifest,
  scenarioDir = "."
): void {
  if (manifest.version !== RECRUITMENT_SCENARIO_VERSION) {
    throw new Error(
      `${scenarioDir}: recruitment scenario version must be ${RECRUITMENT_SCENARIO_VERSION}`
    );
  }
  if (!manifest.id || !manifest.title) throw new Error(`${scenarioDir}: id and title are required`);
  if (!manifest.expected?.summary) throw new Error(`${scenarioDir}: expected.summary is required`);
}

export async function runRecruitmentScenario(options: {
  repoRoot: string;
  scenarioDir: string;
  generatedRoot?: string;
}): Promise<RecruitmentRunResult> {
  const manifest = await loadRecruitmentScenarioManifest(options.scenarioDir);
  const generatedDir = options.generatedRoot ?? path.join(options.scenarioDir, "generated");
  await rm(generatedDir, { recursive: true, force: true });
  await mkdir(generatedDir, { recursive: true });

  const candidates = await discoverCandidateDirs(options.scenarioDir);
  const results: CandidateRunContext[] = [];
  for (const candidateDir of candidates) {
    const candidateId = path.basename(candidateDir);
    const outDir = path.join(candidateDir, "out");
    const candidateGeneratedDir = path.join(generatedDir, candidateId);
    await mkdir(outDir, { recursive: true });
    await rm(path.join(outDir, "contract.dsl.txt"), { force: true });

    const sources = await loadRecruitmentSources(candidateDir);
    const proposal = createRecruitmentProposal(candidateId, sources);
    const dsl = createRecruitmentIntentContractDsl(candidateId, sources, proposal);
    await writeFile(path.join(outDir, "proposal.dsl.txt"), renderProposalDsl(proposal), "utf8");
    await mkdir(candidateGeneratedDir, { recursive: true });
    await writeFile(
      path.join(candidateGeneratedDir, "source-documents.dsl.hcl"),
      renderSourcesDsl(candidateId, sources),
      "utf8"
    );
    await writeFile(
      path.join(candidateGeneratedDir, "intent-contract.dsl.hcl"),
      renderRecruitmentIntentDsl(dsl),
      "utf8"
    );

    const chat = await runChatScenario({
      repoRoot: options.repoRoot,
      scenarioDir: candidateDir,
      generatedRoot: path.join(candidateGeneratedDir, "chat")
    });
    if (chat.summary.outcome === "AGREED") {
      await writeFile(
        path.join(outDir, "contract.dsl.txt"),
        renderContractDsl(proposal, chat),
        "utf8"
      );
    }
    await writeFile(
      path.join(outDir, "status.dsl.txt"),
      renderCandidateStatusDsl(candidateId, chat.summary.outcome, proposal.hash),
      "utf8"
    );
    results.push({
      id: candidateId,
      dir: candidateDir,
      outDir,
      generatedDir: candidateGeneratedDir,
      sources,
      proposal,
      dsl,
      chat
    });
  }

  const summary = createRecruitmentSummary(manifest.id, results);
  await writeFile(
    path.join(generatedDir, "summary.dsl.hcl"),
    renderRecruitmentSummaryDsl(summary),
    "utf8"
  );
  const failures = await compareExpectedRecruitmentSummary(options.scenarioDir, manifest, summary);
  for (const result of results) {
    if (!result.chat.ok) failures.push(`${result.id}: chat summary did not match expected output`);
  }
  return {
    id: manifest.id,
    scenarioDir: options.scenarioDir,
    generatedDir,
    ok: failures.length === 0,
    failures,
    summary
  };
}

export async function loadRecruitmentSources(
  candidateDir: string
): Promise<RecruitmentSourceDocument[]> {
  const inputDir = path.join(candidateDir, "in");
  const sources: RecruitmentSourceDocument[] = [];
  await pushMarkdownSource(sources, inputDir, "oferta.md", "offer-md");
  await pushMarkdownSource(sources, inputDir, "cv.md", "cv-md");
  const pdfPath = path.join(inputDir, "cv.pdf");
  if (existsSync(pdfPath)) {
    const pdf = await extractPdfText(pdfPath);
    if (pdf.text.trim()) {
      sources.push(
        createSourceDocument(candidateDir, pdfPath, "cv-pdf-text", pdf.text, "pdf-text")
      );
    } else {
      const ocr = await runMockOcr(pdfPath);
      sources.push(createSourceDocument(candidateDir, pdfPath, "cv-pdf-ocr", ocr, "ocr-mock"));
    }
  }
  return sources;
}

export async function extractPdfText(
  pdfPath: string
): Promise<{ text: string; requiresOcr: boolean }> {
  const raw = await readFile(pdfPath, "latin1");
  if (raw.includes("OFFICE_DSL_SCANNED_IMAGE_ONLY")) return { text: "", requiresOcr: true };
  const markerLines = raw
    .split(/\r?\n/)
    .filter((line) => line.startsWith("%TEXT:"))
    .map((line) => line.slice("%TEXT:".length).trim());
  if (markerLines.length > 0) return { text: markerLines.join("\n"), requiresOcr: false };
  const strings = [...raw.matchAll(/\(([^()]*)\)\s*Tj/g)].map((match) =>
    unescapePdfText(match[1] ?? "")
  );
  return { text: strings.join("\n"), requiresOcr: strings.length === 0 };
}

async function pushMarkdownSource(
  sources: RecruitmentSourceDocument[],
  inputDir: string,
  fileName: string,
  kind: RecruitmentSourceKind
): Promise<void> {
  const filePath = path.join(inputDir, fileName);
  if (!existsSync(filePath)) return;
  sources.push(
    createSourceDocument(
      path.dirname(inputDir),
      filePath,
      kind,
      await readFile(filePath, "utf8"),
      "markdown"
    )
  );
}

async function runMockOcr(pdfPath: string): Promise<string> {
  const mockPath = path.join(path.dirname(pdfPath), "cv.ocr.txt");
  if (!existsSync(mockPath)) return "";
  return readFile(mockPath, "utf8");
}

function createSourceDocument(
  candidateDir: string,
  filePath: string,
  kind: RecruitmentSourceKind,
  text: string,
  extraction: RecruitmentSourceDocument["extraction"]
): RecruitmentSourceDocument {
  const relativePath = path.relative(candidateDir, filePath).replace(/\\/g, "/");
  const id = `${kind}:${relativePath}`;
  return {
    id,
    kind,
    relativePath,
    text,
    extraction,
    references: createLineReferences(id, kind, relativePath, text)
  };
}

function createLineReferences(
  id: string,
  kind: RecruitmentSourceKind,
  relativePath: string,
  text: string
): SourceReference[] {
  const lines = text.split(/\r?\n/);
  let offset = 0;
  return lines
    .map((line, index) => {
      const start = offset;
      offset += line.length + 1;
      return { line, index, start };
    })
    .filter(({ line }) => line.trim())
    .map(({ line, index, start }) => ({
      type: "file" as const,
      id: `${id}:L${index + 1}`,
      path: relativePath,
      quote: line.trim(),
      span: { start, end: start + line.length },
      speaker: kind === "offer-md" ? "Human1" : "Human2"
    }));
}

function createRecruitmentProposal(
  candidateId: string,
  sources: RecruitmentSourceDocument[]
): RecruitmentProposal {
  const offerText = textOf(sources, "offer-md");
  const cvText = sources
    .filter((source) => source.kind !== "offer-md")
    .map((source) => source.text)
    .join("\n");
  const candidateName =
    cvText.match(/(?:#\s*CV:\s*|Imie i nazwisko:\s*)([^\n]+)/i)?.[1]?.trim() ?? candidateId;
  const role = offerText.match(/Stanowisko:\s*([^\n]+)/i)?.[1]?.trim() ?? null;
  const salaryText = offerText.match(/Wynagrodzenie:\s*(\d[\d ]*)\s*PLN/i);
  const startDate = offerText.match(/Start:\s*([^\n]+)/i)?.[1]?.trim() ?? null;
  const skills = unique([
    ...extractListValues(offerText, "Wymagania"),
    ...extractListValues(cvText, "Umiejetnosci")
  ]);
  const proposalWithoutHash = {
    candidateId,
    candidateName,
    role,
    salary: salaryText
      ? { amount: Number(salaryText[1]!.replace(/\s/g, "")), currency: "PLN" }
      : null,
    startDate,
    skills,
    sourceIds: sources.flatMap((source) => source.references.map((reference) => reference.id))
  };
  const hash = sha256(stableJson(proposalWithoutHash));
  return { ...proposalWithoutHash, hash };
}

function createRecruitmentIntentContractDsl(
  candidateId: string,
  sources: RecruitmentSourceDocument[],
  proposal: RecruitmentProposal
): IntentContractDsl {
  const offerRef = firstReference(sources, "offer-md");
  const cvRef = firstCvReference(sources);
  const dsl: IntentContractDsl = {
    version: INTENT_CONTRACT_DSL_VERSION,
    document: {
      id: `${candidateId}:employment-proposal`,
      type: createField("document.type", "EMPLOYMENT_AGREEMENT", "CONFIRMED", true, offerRef),
      title: createField(
        "document.title",
        proposal.role ? `Recruitment proposal for ${proposal.role}` : null,
        proposal.role ? "CONFIRMED" : "MISSING",
        true,
        offerRef
      ),
      language: createField("document.language", "pl", "ASSUMED", false, offerRef)
    },
    contract: {
      id: `${candidateId}:contract`,
      title: createField("contract.title", "Employment proposal", "ASSUMED", false, offerRef),
      governingLaw: createField<string>("contract.governingLaw", null, "MISSING", true)
    },
    parties: [
      {
        id: "employer",
        name: createField("parties.employer.name", "WellManifest", "CONFIRMED", true, offerRef),
        role: createField("parties.employer.role", "Human1", "CONFIRMED", true, offerRef)
      },
      {
        id: candidateId,
        name: createField(
          "parties.candidate.name",
          proposal.candidateName,
          "CONFIRMED",
          true,
          cvRef
        ),
        role: createField("parties.candidate.role", "Human2", "CONFIRMED", true, cvRef)
      }
    ],
    roles: [
      {
        id: "candidate-role",
        partyId: createField("roles.candidate.partyId", candidateId, "CONFIRMED", true, cvRef),
        name: createField(
          "roles.candidate.name",
          proposal.role,
          proposal.role ? "CONFIRMED" : "MISSING",
          true,
          offerRef
        )
      }
    ],
    intents: [
      {
        id: "hire-candidate",
        requesterPartyId: createField(
          "intents.hire.requesterPartyId",
          "employer",
          "CONFIRMED",
          true,
          offerRef
        ),
        description: createField(
          "intents.hire.description",
          proposal.role ? `Hire ${proposal.candidateName} as ${proposal.role}` : null,
          proposal.role ? "CONFIRMED" : "MISSING",
          true,
          offerRef
        )
      }
    ],
    subjects: [
      {
        id: "candidate-profile",
        description: createField(
          "subjects.candidate.description",
          proposal.skills.join(", "),
          "INCOMPLETE",
          true,
          cvRef
        )
      }
    ],
    obligations: [],
    deliverables: [
      {
        id: "employment-start",
        description: createField(
          "deliverables.employment-start.description",
          proposal.startDate ? `Candidate starts on ${proposal.startDate}` : null,
          proposal.startDate ? "CONFIRMED" : "MISSING",
          true,
          offerRef
        ),
        ownerPartyId: createField(
          "deliverables.employment-start.ownerPartyId",
          candidateId,
          "CONFIRMED",
          true,
          cvRef
        )
      }
    ],
    deadlines: [],
    payments: proposal.salary
      ? [
          {
            id: "salary",
            payerPartyId: createField(
              "payments.salary.payerPartyId",
              "employer",
              "CONFIRMED",
              true,
              offerRef
            ),
            payeePartyId: createField(
              "payments.salary.payeePartyId",
              candidateId,
              "CONFIRMED",
              true,
              cvRef
            ),
            total: createField(
              "payments.salary.total",
              proposal.salary,
              "CONFIRMED",
              true,
              offerRef
            )
          }
        ]
      : [],
    conditions: [],
    dependencies: [],
    acceptanceCriteria: [],
    exclusions: [],
    assumptions: [
      {
        id: "document-ingestion-mock-safe",
        description: createField(
          "assumptions.document-ingestion.description",
          "Offer/CV text was extracted through deterministic local fixtures; OCR uses mock text unless a production provider is configured later.",
          "ASSUMED",
          false,
          offerRef
        )
      }
    ],
    risks: [],
    conflicts: [],
    questions: [
      {
        id: "governing-law",
        targetPartyId: createField(
          "questions.governing-law.targetPartyId",
          "human1",
          "ASSUMED",
          true,
          offerRef
        ),
        field: "contract.governingLaw",
        prompt: createField(
          "questions.governing-law.prompt",
          "Jakie prawo wlasciwe ma obowiazywac?",
          "MISSING",
          true,
          offerRef
        )
      }
    ],
    approvals: [],
    sourceReferences: sources.flatMap((source) => source.references),
    render: [],
    execution: []
  };
  const validation = validateIntentContractDsl(dsl);
  if (!validation.ok)
    throw new Error(validation.issues.map((issue) => `${issue.path}: ${issue.message}`).join("; "));
  return dsl;
}

function createRecruitmentSummary(
  id: string,
  results: CandidateRunContext[]
): RecruitmentRunSummary {
  const candidates = results.map((result) => {
    const accepted = result.chat.summary.outcome === "AGREED";
    return {
      id: result.id,
      outcome: accepted ? "ACCEPTED" : "REJECTED",
      chatOutcome: result.chat.summary.outcome,
      finalCreated: accepted,
      contractPath: accepted ? "out/contract.dsl.txt" : null,
      proposalHash: result.proposal.hash,
      sourceDocuments: result.sources.map((source) => ({
        id: source.id,
        kind: source.kind,
        extraction: source.extraction
      }))
    } satisfies RecruitmentCandidateSummary;
  });
  return {
    id,
    candidateCount: candidates.length,
    accepted: candidates
      .filter((candidate) => candidate.outcome === "ACCEPTED")
      .map((candidate) => candidate.id),
    rejected: candidates
      .filter((candidate) => candidate.outcome === "REJECTED")
      .map((candidate) => candidate.id),
    candidates
  };
}

async function discoverCandidateDirs(scenarioDir: string): Promise<string[]> {
  const entries = await readdir(scenarioDir, { withFileTypes: true });
  return entries
    .filter((entry) => entry.isDirectory())
    .filter((entry) => !["generated", "out"].includes(entry.name))
    .map((entry) => path.join(scenarioDir, entry.name))
    .filter(
      (candidateDir) =>
        existsSync(path.join(candidateDir, "in")) && existsSync(path.join(candidateDir, "chat.txt"))
    )
    .sort((a, b) => path.basename(a).localeCompare(path.basename(b)));
}

async function compareExpectedRecruitmentSummary(
  scenarioDir: string,
  manifest: RecruitmentScenarioManifest,
  actual: RecruitmentRunSummary
): Promise<string[]> {
  const expected = JSON.parse(
    await readFile(path.join(scenarioDir, manifest.expected.summary), "utf8")
  );
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
    for (const [key, value] of Object.entries(expected)) {
      compareSubset(
        failures,
        `${label}.${key}`,
        value,
        (actual as Record<string, unknown> | undefined)?.[key]
      );
    }
    return;
  }
  if (expected !== actual)
    failures.push(`${label} expected ${String(expected)} but got ${String(actual)}`);
}

function renderSourcesDsl(candidateId: string, sources: RecruitmentSourceDocument[]): string {
  return block("document", "RECRUITMENT_SOURCES", [
    assign("candidate", candidateId),
    ...sources.map((source) =>
      block("source", source.id, [
        assign("kind", source.kind),
        assign("path", source.relativePath),
        assign("extraction", source.extraction),
        assign("line_count", source.references.length)
      ])
    )
  ]);
}

function renderRecruitmentIntentDsl(dsl: IntentContractDsl): string {
  const body = [
    assign("version", dsl.version),
    assign("document_type", dsl.document.type.value),
    assign("title", dsl.document.title.value),
    assign("source_count", dsl.sourceReferences.length)
  ];
  for (const question of dsl.questions)
    body.push(
      block("question", question.id, [
        assign("field", question.field),
        assign("prompt", question.prompt.value)
      ])
    );
  return block("document", "RECRUITMENT_INTENT_CONTRACT", body);
}

function renderProposalDsl(proposal: RecruitmentProposal): string {
  return block("document", "RECRUITMENT_PROPOSAL", [
    assign("candidate", proposal.candidateId),
    assign("candidate_name", proposal.candidateName),
    assign("role", proposal.role),
    assign(
      "salary",
      proposal.salary ? `${proposal.salary.amount} ${proposal.salary.currency}` : null
    ),
    assign("start_date", proposal.startDate),
    assign("skills", proposal.skills),
    assign("hash", proposal.hash)
  ]);
}

function renderContractDsl(proposal: RecruitmentProposal, chat: ChatRunResult): string {
  return block("document", "RECRUITMENT_FINAL_CONTRACT", [
    assign("candidate", proposal.candidateId),
    assign("candidate_name", proposal.candidateName),
    assign("role", proposal.role),
    assign(
      "salary",
      proposal.salary ? `${proposal.salary.amount} ${proposal.salary.currency}` : null
    ),
    assign("start_date", proposal.startDate),
    assign("chat_hash", chat.summary.finalHash),
    assign("proposal_hash", proposal.hash),
    assign(
      "approved_by",
      chat.summary.approvals
        .filter((approval) => approval.status === "ACTIVE")
        .map((approval) => approval.party)
    )
  ]);
}

function renderCandidateStatusDsl(
  candidateId: string,
  outcome: ChatOutcome,
  proposalHash: string
): string {
  return block("document", "RECRUITMENT_CANDIDATE_STATUS", [
    assign("candidate", candidateId),
    assign("chat_outcome", outcome),
    assign("proposal_hash", proposalHash)
  ]);
}

function renderRecruitmentSummaryDsl(summary: RecruitmentRunSummary): string {
  return block("document", "RECRUITMENT_SUMMARY", [
    assign("id", summary.id),
    assign("candidate_count", summary.candidateCount),
    assign("accepted", summary.accepted),
    assign("rejected", summary.rejected),
    ...summary.candidates.map((candidate) =>
      block("candidate", candidate.id, [
        assign("outcome", candidate.outcome),
        assign("final_created", candidate.finalCreated),
        assign("contract_path", candidate.contractPath),
        assign("proposal_hash", candidate.proposalHash)
      ])
    )
  ]);
}

function textOf(sources: RecruitmentSourceDocument[], kind: RecruitmentSourceKind): string {
  return sources.find((source) => source.kind === kind)?.text ?? "";
}

function firstReference(
  sources: RecruitmentSourceDocument[],
  kind: RecruitmentSourceKind
): SourceReference | null {
  return sources.find((source) => source.kind === kind)?.references[0] ?? null;
}

function firstCvReference(sources: RecruitmentSourceDocument[]): SourceReference | null {
  return sources.find((source) => source.kind !== "offer-md")?.references[0] ?? null;
}

function extractListValues(text: string, heading: string): string[] {
  const match = new RegExp(`${heading}:\\s*([^\\n]+)`, "i").exec(text);
  return (
    match?.[1]
      ?.split(/,|;/)
      .map((item) => item.trim())
      .filter(Boolean) ?? []
  );
}

function unique(values: string[]): string[] {
  return [...new Set(values.filter(Boolean))];
}

function unescapePdfText(value: string): string {
  return value.replace(/\\\)/g, ")").replace(/\\\(/g, "(").replace(/\\n/g, "\n");
}

function sha256(value: string): string {
  return createHash("sha256").update(value).digest("hex");
}

function stableJson(value: unknown): string {
  return JSON.stringify(sortValue(value));
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

function block(name: string, label: string, lines: string[]): string {
  return `${name} "${label}" {\n${lines.map((line) => `  ${line}`).join("\n")}\n}\n`;
}

function assign(name: string, value: unknown): string {
  if (Array.isArray(value))
    return `${name} = [${value.map((item) => quote(String(item))).join(", ")}]`;
  if (typeof value === "number" || typeof value === "boolean") return `${name} = ${String(value)}`;
  if (value === null || value === undefined) return `${name} = null`;
  return `${name} = ${quote(String(value))}`;
}

function quote(value: string): string {
  return JSON.stringify(value);
}
