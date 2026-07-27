import { writeFile } from "node:fs/promises";
import path from "node:path";

export function quoteDsl(value: string): string {
  return JSON.stringify(value);
}

export function assign(key: string, value: unknown): string {
  if (Array.isArray(value)) {
    return `${key} = [${value.map((item) => quoteDsl(String(item))).join(", ")}]`;
  }
  if (typeof value === "number" || typeof value === "boolean") return `${key} = ${String(value)}`;
  if (value === null || value === undefined) return `${key} = null`;
  return `${key} = ${quoteDsl(String(value))}`;
}

export function block(kind: string, label: string, body: string[]): string {
  const lines = [`${kind} ${quoteDsl(label)} {`];
  for (const item of body) lines.push(indentDsl(item));
  lines.push("}");
  return `${lines.join("\n")}\n`;
}

export function indentDsl(value: string): string {
  return value
    .trimEnd()
    .split(/\r?\n/)
    .map((line) => `  ${line}`)
    .join("\n");
}

export async function writeDslHcl(dir: string, name: string, body: string): Promise<void> {
  await writeFile(path.join(dir, name), `${body.trim()}\n`, "utf8");
}
