import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import {
  extractPdfText,
  normalizePdfTextMarkdown,
  renderMarkdownAsPdfTextFixture,
  renderTextAsMinimalPdf
} from "../packages/pdf-generator/src/index.js";

describe("@office-dsl/pdf-generator", () => {
  it("renders contract text as a structurally valid minimal PDF", () => {
    const pdf = renderTextAsMinimalPdf("# Contract\nStatus: AGREED\nHash: abc");

    expect(pdf).toMatch(/^%PDF-1\.4/);
    expect(pdf).toContain("/Type /Page");
    expect(pdf).toContain("xref");
    expect(pdf).toContain("trailer");
    expect(pdf).toContain("startxref");
  });

  it("round-trips Markdown through a text PDF fixture and extracts editable Markdown", async () => {
    const generatedRoot = await mkdtemp(path.join(os.tmpdir(), "pdf-generator-"));
    try {
      const cvMarkdown = [
        "# CV: LLM Generated Candidate",
        "Imie i nazwisko: Julia Testowa",
        "Umiejetnosci:",
        "- TypeScript",
        "- PDF pipeline"
      ].join("\n");
      const pdfPath = path.join(generatedRoot, "cv.pdf");
      await writeFile(pdfPath, renderMarkdownAsPdfTextFixture(cvMarkdown), "latin1");

      const pdfText = await readFile(pdfPath, "latin1");
      expect(pdfText).toMatch(/^%PDF-1\.4/);
      expect(pdfText).not.toContain("%TEXT:");

      const extracted = await extractPdfText(pdfPath);
      expect(extracted.requiresOcr).toBe(false);
      expect(extracted.text).toContain("Julia Testowa");
      expect(normalizePdfTextMarkdown(extracted.text)).toContain("# CV: LLM Generated Candidate");
    } finally {
      await rm(generatedRoot, { recursive: true, force: true });
    }
  });

  it("flags scanned fixture PDFs as requiring OCR", async () => {
    const generatedRoot = await mkdtemp(path.join(os.tmpdir(), "pdf-scanned-"));
    try {
      const pdfPath = path.join(generatedRoot, "scan.pdf");
      await writeFile(pdfPath, "%PDF-1.4\nOFFICE_DSL_SCANNED_IMAGE_ONLY\n%%EOF\n", "latin1");
      await expect(extractPdfText(pdfPath)).resolves.toEqual({ text: "", requiresOcr: true });
    } finally {
      await rm(generatedRoot, { recursive: true, force: true });
    }
  });
});
