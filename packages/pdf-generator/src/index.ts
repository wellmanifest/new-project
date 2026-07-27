import { readFile } from "node:fs/promises";

export interface PdfTextExtractionResult {
  text: string;
  requiresOcr: boolean;
}

export function renderTextAsMinimalPdf(text: string): string {
  const textLines = text
    .split(/\r?\n/)
    .filter(Boolean)
    .slice(0, 24)
    .map((line) => line.replace(/[()\\]/g, ""));
  const content = `BT /F1 10 Tf 50 780 Td ${textLines
    .map((line, index) => `${index ? "0 -14 Td " : ""}(${line}) Tj`)
    .join(" ")} ET`;
  return renderPdfObjects([content], "binary");
}

export function renderMarkdownAsPdfTextFixture(markdown: string): string {
  const textLines = markdown.split(/\r?\n/).map((line) => line.replace(/\r/g, ""));
  const content = [
    "BT",
    "/F1 11 Tf",
    "72 760 Td",
    "14 TL",
    ...textLines.map((line, index) => `${index === 0 ? "" : "T* "}(${escapePdfString(line)}) Tj`),
    "ET"
  ].join("\n");
  return renderPdfObjects([content], "latin1");
}

export async function extractPdfText(pdfPath: string): Promise<PdfTextExtractionResult> {
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

export function normalizePdfTextMarkdown(text: string): string {
  const normalized = text
    .replace(/\r\n/g, "\n")
    .split("\n")
    .map((line) => line.trimEnd())
    .join("\n")
    .trim();
  return `${normalized.replace(/^(# .+)\n(?!\n)/, "$1\n\n")}\n`;
}

function renderPdfObjects(contents: string[], encoding: BufferEncoding): string {
  const pageContent = contents.join("\n");
  const objects = [
    "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
    "2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
    "3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n",
    "4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
    `5 0 obj\n<< /Length ${Buffer.byteLength(pageContent, encoding)} >>\nstream\n${pageContent}\nendstream\nendobj\n`
  ];
  let pdf = "%PDF-1.4\n";
  const offsets = [0];
  for (const object of objects) {
    offsets.push(Buffer.byteLength(pdf, encoding));
    pdf += object;
  }
  const xrefOffset = Buffer.byteLength(pdf, encoding);
  pdf += `xref\n0 ${objects.length + 1}\n`;
  pdf += "0000000000 65535 f \n";
  for (const offset of offsets.slice(1)) pdf += `${String(offset).padStart(10, "0")} 00000 n \n`;
  pdf += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF\n`;
  return pdf;
}

function escapePdfString(value: string): string {
  return value.replace(/\\/g, "\\\\").replace(/\(/g, "\\(").replace(/\)/g, "\\)");
}

function unescapePdfText(value: string): string {
  return value.replace(/\\\(/g, "(").replace(/\\\)/g, ")").replace(/\\\\/g, "\\");
}
