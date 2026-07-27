import { existsSync } from "node:fs";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { describe, expect, it } from "vitest";

async function readRoot(file: string): Promise<string> {
  return readFile(path.join(process.cwd(), file), "utf8");
}

describe("documentation alignment", () => {
  it("README.md separates the current MVP from the full target system", async () => {
    const readme = await readRoot("README.md");
    expect(readme).toMatch(/offline Office DSL MVP/);
    expect(readme).toMatch(/not the full target system/);
    expect(readme).toMatch(/Target Architecture/);
    expect(readme).toMatch(/docs\/system-purpose-and-runtime-flow\.md/);
  });

  it("describes system purpose, runtime flow, and current-vs-target state", async () => {
    const docPath = path.join(process.cwd(), "docs", "system-purpose-and-runtime-flow.md");
    expect(existsSync(docPath)).toBe(true);
    const doc = await readFile(docPath, "utf8");
    expect(doc).toMatch(/purpose/i);
    expect(doc).toMatch(/runtime flow/i);
    expect(doc).toMatch(/Current State Versus Target/i);
  });

  it("documents the Codex Windows sandbox Vitest limitation", async () => {
    const docPath = path.join(process.cwd(), "docs", "codex-sandbox-vitest.md");
    expect(existsSync(docPath)).toBe(true);
    const doc = await readFile(docPath, "utf8");
    expect(doc).toMatch(/Vitest|Vite|spawn|EPERM/i);
  });

  it("keeps version metadata consistent across VERSION and CHANGELOG.md", async () => {
    const version = await readRoot("VERSION");
    const changelog = await readRoot("CHANGELOG.md");
    expect(version).toMatch(/`0\.7\.7`/);
    expect(changelog).toMatch(/0\.7\.7/);
  });
});
