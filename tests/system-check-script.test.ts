import { readFile } from "node:fs/promises";
import path from "node:path";
import { describe, expect, it } from "vitest";

async function readRoot(file: string): Promise<string> {
  return readFile(path.join(process.cwd(), file), "utf8");
}

describe("functional system check scripts", () => {
  it("exposes a single package script for the full functional check", async () => {
    const packageJson = JSON.parse(await readRoot("package.json")) as {
      scripts: Record<string, string>;
    };

    expect(packageJson.scripts["system:check"]).toBe("tsx packages/example-runner/src/verify.ts");
    expect(packageJson.scripts.verify).toBe(packageJson.scripts["system:check"]);
  });

  it("runs all functional system surfaces from the TypeScript verifier script", async () => {
    const verifyScript = await readRoot("packages/example-runner/src/verify.ts");

    for (const expected of [
      "typecheck",
      "lint",
      "format",
      "typescript tests",
      "python verifier tests",
      "example runner",
      "chat example runner",
      "recruitment example runner",
      "git diff whitespace"
    ]) {
      expect(verifyScript).toContain(expected);
    }

    expect(verifyScript).toContain("examples:run");
    expect(verifyScript).toContain("examples-chat:run");
    expect(verifyScript).toContain("examples-recruitment:run");
    expect(verifyScript).toContain("pytest");
  });

  it("keeps project.sh and project.bat wired to the same functional check", async () => {
    const projectSh = await readRoot("project.sh");
    const projectBat = await readRoot("project.bat");

    expect(projectSh).toContain("system-check|functional-test|functional-tests");
    expect(projectSh).toContain("pnpm_run system:check");
    expect(projectSh).toContain("pnpm_run verify");

    expect(projectBat).toContain("call corepack pnpm run verify");
    expect(projectBat).toContain(":system-check");
    expect(projectBat).toContain("call corepack pnpm run system:check");
    expect(projectBat).toContain("call corepack pnpm run dev:backend");
  });
});
