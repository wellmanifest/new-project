import { existsSync } from "node:fs";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import {
  discoverRecruitmentScenarios,
  loadRecruitmentSources,
  runRecruitmentDocumentProcesses,
  runRecruitmentScenario
} from "../packages/example-runner/src/index.js";
import { extractPdfText } from "../packages/pdf-generator/src/index.js";

const repoRoot = process.cwd();
const scenarioDir = path.join(repoRoot, "examples-recruitment", "01-multi-candidate");

describe("examples-recruitment runner", () => {
  it("discovers recruitment scenarios", async () => {
    const scenarios = await discoverRecruitmentScenarios(repoRoot);
    expect(scenarios.map((scenario) => path.basename(scenario))).toEqual([
      "01-multi-candidate",
      "02-single-candidate-agreement",
      "03-negotiated-two-candidates",
      "04-ocr-candidate-cancelled"
    ]);
  });

  it("runs one-file document process fixtures for md2pdf and pdf2md", async () => {
    const results = await runRecruitmentDocumentProcesses(scenarioDir);
    expect(results).toEqual([
      expect.objectContaining({ id: "001-anna-nowak-md2pdf", process: "md2pdf", ok: true }),
      expect.objectContaining({ id: "002-bartek-lis-pdf2md", process: "pdf2md", ok: true })
    ]);

    const generatedPdf = await readFile(
      path.join(scenarioDir, "001-anna-nowak", "document-processes", "md2pdf", "out", "cv.pdf"),
      "latin1"
    );
    expect(generatedPdf).toMatch(/^%PDF-1\.4/);
    expect(generatedPdf).toContain("/Type /Page");
    expect(generatedPdf).toContain("xref");
    expect(generatedPdf).toContain("trailer");
    expect(generatedPdf).not.toContain("%TEXT:");

    const generatedMarkdown = await readFile(
      path.join(scenarioDir, "002-bartek-lis", "document-processes", "pdf2md", "out", "cv.md"),
      "utf8"
    );
    expect(generatedMarkdown).toContain("# CV: Bartek Lis");
    expect(generatedMarkdown).toContain("Umiejetnosci: PHP, podstawy JavaScript");
  });

  it("loads Markdown offers, Markdown CVs, text PDFs, and OCR fallback sources", async () => {
    const annaSources = await loadRecruitmentSources(path.join(scenarioDir, "001-anna-nowak"));
    expect(annaSources.map((source) => source.kind)).toEqual(["offer-md", "cv-md"]);
    expect(annaSources.find((source) => source.kind === "cv-md")?.text).toContain("Anna Nowak");
    expect(annaSources.every((source) => source.references.length > 0)).toBe(true);

    const scanned = await extractPdfText(path.join(scenarioDir, "002-bartek-lis", "in", "cv.pdf"));
    expect(scanned).toEqual({ text: "", requiresOcr: true });

    const bartekSources = await loadRecruitmentSources(path.join(scenarioDir, "002-bartek-lis"));
    expect(bartekSources.map((source) => source.kind)).toEqual(["offer-md", "cv-pdf-ocr"]);
    expect(bartekSources.find((source) => source.kind === "cv-pdf-ocr")?.text).toContain(
      "Bartek Lis"
    );
  });

  it("runs recruitment end to end and finalizes only accepted candidates", async () => {
    const generatedRoot = await mkdtemp(path.join(os.tmpdir(), "examples-recruitment-"));
    const result = await runRecruitmentScenario({ repoRoot, scenarioDir, generatedRoot });

    expect(result.ok).toBe(true);
    expect(result.summary).toMatchObject({
      id: "01-multi-candidate",
      candidateCount: 2,
      accepted: ["001-anna-nowak"],
      rejected: ["002-bartek-lis"],
      documentProcesses: [
        expect.objectContaining({
          id: "001-anna-nowak-md2pdf",
          process: "md2pdf",
          processDir: "001-anna-nowak/document-processes/md2pdf",
          ok: true
        }),
        expect.objectContaining({
          id: "002-bartek-lis-pdf2md",
          process: "pdf2md",
          processDir: "002-bartek-lis/document-processes/pdf2md",
          ok: true
        })
      ]
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
