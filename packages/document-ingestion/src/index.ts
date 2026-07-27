import { existsSync } from "node:fs";
import { mkdir, readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import {
  extractPdfText,
  normalizePdfTextMarkdown,
  renderMarkdownAsPdfTextFixture
} from "@office-dsl/pdf-generator";

export const DOCUMENT_PROCESS_TEST_VERSION = "example-recruitment.document-process-test.v1";
export type DocumentProcess = "md2pdf" | "pdf2md";

export interface DocumentProcessTest {
  version: typeof DOCUMENT_PROCESS_TEST_VERSION;
  id: string;
  process: DocumentProcess;
  input: string;
  output: string;
  expect?: {
    contains?: string[];
    notContains?: string[];
    pdfStructure?: boolean;
  };
}

export interface DocumentProcessResult {
  id: string;
  process: DocumentProcess;
  input: string;
  output: string;
  ok: boolean;
  failures: string[];
}

export async function runDocumentProcesses(scenarioDir: string): Promise<DocumentProcessResult[]> {
  const processDirs = await discoverDocumentProcessDirs(scenarioDir);
  const results: DocumentProcessResult[] = [];
  for (const processDir of processDirs) results.push(await runDocumentProcess(processDir));
  return results;
}

export async function runDocumentProcess(processDir: string): Promise<DocumentProcessResult> {
  const test = JSON.parse(
    (await readFile(path.join(processDir, "test.json"), "utf8")).replace(/^\uFEFF/, "")
  ) as DocumentProcessTest;
  validateDocumentProcessTest(test, processDir);
  const inputPath = path.join(processDir, test.input);
  const outputPath = path.join(processDir, test.output);
  await mkdir(path.dirname(outputPath), { recursive: true });
  const failures: string[] = [];

  if (test.process === "md2pdf") {
    const markdown = await readFile(inputPath, "utf8");
    await writeFile(outputPath, renderMarkdownAsPdfTextFixture(markdown), "latin1");
  } else {
    await writeFile(outputPath, await ocrPdfToMarkdownFixture(inputPath), "utf8");
  }

  const outputText = await readFile(outputPath, test.process === "md2pdf" ? "latin1" : "utf8");
  if (test.expect?.pdfStructure) validateGeneratedPdfStructure(outputText, failures);
  for (const expected of test.expect?.contains ?? []) {
    if (!outputText.includes(expected))
      failures.push(`output does not contain ${JSON.stringify(expected)}`);
  }
  for (const forbidden of test.expect?.notContains ?? []) {
    if (outputText.includes(forbidden))
      failures.push(`output unexpectedly contains ${JSON.stringify(forbidden)}`);
  }
  if (test.process === "pdf2md") {
    const extracted = await ocrPdfToMarkdownFixture(inputPath);
    if (extracted !== outputText) failures.push("pdf2md output is not deterministic");
  }
  return {
    id: test.id,
    process: test.process,
    input: test.input,
    output: test.output,
    ok: failures.length === 0,
    failures
  };
}

export async function discoverDocumentProcessDirs(scenarioDir: string): Promise<string[]> {
  const entries = await readdir(scenarioDir, { withFileTypes: true });
  return entries
    .filter(
      (entry) => entry.isDirectory() && existsSync(path.join(scenarioDir, entry.name, "test.json"))
    )
    .map((entry) => path.join(scenarioDir, entry.name))
    .sort((a, b) => path.basename(a).localeCompare(path.basename(b)));
}

export async function ocrPdfToMarkdownFixture(pdfPath: string): Promise<string> {
  const pdf = await extractPdfText(pdfPath);
  if (pdf.text.trim()) return normalizePdfTextMarkdown(pdf.text);
  return normalizePdfTextMarkdown(await runMockOcr(pdfPath));
}

export async function runMockOcr(pdfPath: string): Promise<string> {
  const mockPath = path.join(path.dirname(pdfPath), "cv.ocr.txt");
  if (!existsSync(mockPath)) return "";
  return readFile(mockPath, "utf8");
}

function validateDocumentProcessTest(test: DocumentProcessTest, processDir: string): void {
  if (test.version !== DOCUMENT_PROCESS_TEST_VERSION) {
    throw new Error(
      `${processDir}: document process test version must be ${DOCUMENT_PROCESS_TEST_VERSION}`
    );
  }
  if (!test.id) throw new Error(`${processDir}: id is required`);
  if (test.process !== "md2pdf" && test.process !== "pdf2md") {
    throw new Error(`${processDir}: process must be md2pdf or pdf2md`);
  }
  if (!test.input || !test.output) throw new Error(`${processDir}: input and output are required`);
}

function validateGeneratedPdfStructure(pdfText: string, failures: string[]): void {
  for (const token of ["%PDF-1.4", "1 0 obj", "/Type /Page", "xref", "trailer", "startxref"]) {
    if (!pdfText.includes(token)) failures.push(`PDF output is missing ${token}`);
  }
  if (pdfText.includes("%TEXT:"))
    failures.push("PDF output still uses marker-only pseudo PDF syntax");
}
