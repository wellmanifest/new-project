import { existsSync } from "node:fs";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import {
  discoverRecruitmentScenarios,
  extractPdfText,
  loadRecruitmentSources,
  ocrPdfToMarkdownFixture,
  renderMarkdownAsPdfTextFixture,
  runRecruitmentScenario
} from "../packages/example-runner/src/index.js";

const repoRoot = process.cwd();
const scenarioDir = path.join(repoRoot, "examples-recruitment", "01-multi-candidate");

describe("examples-recruitment runner", () => {
  it("discovers recruitment scenarios", async () => {
    const scenarios = await discoverRecruitmentScenarios(repoRoot);
    expect(scenarios.map((scenario) => path.basename(scenario))).toEqual(["01-multi-candidate"]);
  });

  it("keeps Anna's text CV PDF as a valid PDF file, not a marker-only pseudo PDF", async () => {
    const pdfText = await readFile(
      path.join(scenarioDir, "001-anna-nowak", "in", "cv.pdf"),
      "latin1"
    );
    expect(pdfText).toMatch(/^%PDF-1\.4/);
    expect(pdfText).toContain("1 0 obj");
    expect(pdfText).toContain("/Type /Page");
    expect(pdfText).toContain("xref");
    expect(pdfText).toContain("trailer");
    expect(pdfText).toContain("startxref");
    expect(pdfText).not.toContain("%TEXT:");
  });

  it("loads Markdown offers, Markdown CVs, text PDFs, and OCR fallback sources", async () => {
    const annaSources = await loadRecruitmentSources(path.join(scenarioDir, "001-anna-nowak"));
    expect(annaSources.map((source) => source.kind)).toEqual(["offer-md", "cv-md", "cv-pdf-text"]);
    expect(annaSources.find((source) => source.kind === "cv-pdf-text")?.text).toContain(
      "Anna Nowak"
    );
    expect(annaSources.every((source) => source.references.length > 0)).toBe(true);

    const scanned = await extractPdfText(path.join(scenarioDir, "002-bartek-lis", "in", "cv.pdf"));
    expect(scanned).toEqual({ text: "", requiresOcr: true });

    const bartekSources = await loadRecruitmentSources(path.join(scenarioDir, "002-bartek-lis"));
    expect(bartekSources.map((source) => source.kind)).toEqual(["offer-md", "cv-pdf-ocr"]);
    expect(bartekSources.find((source) => source.kind === "cv-pdf-ocr")?.text).toContain(
      "Bartek Lis"
    );
  });

  it("round-trips a generated sample CV through Markdown -> PDF fixture -> OCR Markdown", async () => {
    const generatedRoot = await mkdtemp(path.join(os.tmpdir(), "cv-md-pdf-ocr-"));
    const cvMarkdown = [
      "# CV: LLM Generated Candidate",
      "Imie i nazwisko: Julia Testowa",
      "Umiejetnosci:",
      "- TypeScript",
      "- OCR validation",
      "Doswiadczenie: 5 lat w automatyzacji dokumentow"
    ].join("\n");
    const pdfPath = path.join(generatedRoot, "cv.pdf");
    await writeFile(pdfPath, renderMarkdownAsPdfTextFixture(cvMarkdown), "latin1");

    const extracted = await extractPdfText(pdfPath);
    const ocrMarkdown = await ocrPdfToMarkdownFixture(pdfPath);

    expect(extracted.requiresOcr).toBe(false);
    expect(ocrMarkdown).toContain("# CV: LLM Generated Candidate");
    expect(ocrMarkdown).toContain("Umiejetnosci:");
    expect(ocrMarkdown).toContain("- OCR validation");
    await rm(generatedRoot, { recursive: true, force: true });
  });
  it("runs recruitment end to end and finalizes only accepted candidates", async () => {
    const generatedRoot = await mkdtemp(path.join(os.tmpdir(), "examples-recruitment-"));
    const result = await runRecruitmentScenario({ repoRoot, scenarioDir, generatedRoot });

    expect(result.ok).toBe(true);
    expect(result.summary).toMatchObject({
      id: "01-multi-candidate",
      candidateCount: 2,
      accepted: ["001-anna-nowak"],
      rejected: ["002-bartek-lis"]
    });
    expect(result.summary.candidates[0]).toMatchObject({
      id: "001-anna-nowak",
      outcome: "ACCEPTED",
      chatOutcome: "AGREED",
      finalCreated: true,
      contractPath: "out/contract.dsl.txt"
    });
    expect(result.summary.candidates[1]).toMatchObject({
      id: "002-bartek-lis",
      outcome: "REJECTED",
      chatOutcome: "CANCELLED",
      finalCreated: false,
      contractPath: null
    });

    const acceptedContract = path.join(scenarioDir, "001-anna-nowak", "out", "contract.dsl.txt");
    const rejectedContract = path.join(scenarioDir, "002-bartek-lis", "out", "contract.dsl.txt");
    expect(existsSync(acceptedContract)).toBe(true);
    expect(existsSync(rejectedContract)).toBe(false);
    const contract = await readFile(acceptedContract, "utf8");
    expect(contract).toContain('document "RECRUITMENT_FINAL_CONTRACT"');
    expect(() => JSON.parse(contract)).toThrow();
    expect(
      existsSync(path.join(generatedRoot, "001-anna-nowak", "chat", "final", "contract.pdf"))
    ).toBe(true);
    expect(
      existsSync(path.join(generatedRoot, "002-bartek-lis", "chat", "final", "contract.pdf"))
    ).toBe(false);
    await rm(acceptedContract, { force: true });
    await rm(path.join(scenarioDir, "001-anna-nowak", "out", "proposal.dsl.txt"), { force: true });
    await rm(path.join(scenarioDir, "001-anna-nowak", "out", "status.dsl.txt"), { force: true });
    await rm(path.join(scenarioDir, "002-bartek-lis", "out", "proposal.dsl.txt"), { force: true });
    await rm(path.join(scenarioDir, "002-bartek-lis", "out", "status.dsl.txt"), { force: true });
    await rm(generatedRoot, { recursive: true, force: true });
  });
});
