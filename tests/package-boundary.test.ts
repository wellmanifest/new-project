import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { readdir } from "node:fs/promises";
import path from "node:path";

const repoRoot = process.cwd();
const requiredPackages = [
  "@office-dsl/chat-negotiation",
  "@office-dsl/document-ingestion",
  "@office-dsl/dsl-artifact-renderer",
  "@office-dsl/regression-runner",
  "@office-dsl/recruitment-workflow",
  "@office-dsl/verifier-bridge",
  "@office-dsl/verifier-mock"
];

async function listFiles(dir: string): Promise<string[]> {
  const entries = await readdir(dir, { withFileTypes: true });
  const files: string[] = [];
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) files.push(...(await listFiles(full)));
    else files.push(full);
  }
  return files;
}

function readJson(file: string): Record<string, unknown> {
  return JSON.parse(readFileSync(file, "utf8")) as Record<string, unknown>;
}

describe("package boundaries", () => {
  it("keeps extracted workflow and shared utility packages present", async () => {
    const packageFiles = await listFiles(path.join(repoRoot, "packages"));
    const names = packageFiles
      .filter((file) => file.endsWith("package.json"))
      .map((file) => readJson(file).name);

    for (const required of requiredPackages) expect(names).toContain(required);
  });

  it("does not bypass package boundaries with source-relative package imports", async () => {
    const sourceFiles = [
      ...(await listFiles(path.join(repoRoot, "packages"))),
      ...(await listFiles(path.join(repoRoot, "apps")))
    ].filter((file) => file.endsWith(".ts"));

    const offenders = sourceFiles.filter((file) => {
      const text = readFileSync(file, "utf8");
      return /from\s+["'](?:\.\.\/){2,}.*src\/(?:index|store)\.js["']/.test(text);
    });

    expect(offenders.map((file) => path.relative(repoRoot, file))).toEqual([]);
  });

  it("declares workspace dependencies for every internal package import", async () => {
    const workspacePackageFiles = (await listFiles(path.join(repoRoot, "packages"))).filter(
      (file) => file.endsWith("package.json")
    );
    const workspaceNames = new Set(
      workspacePackageFiles.map((file) => String(readJson(file).name))
    );
    const sourceFiles = (await listFiles(path.join(repoRoot, "packages"))).filter((file) =>
      file.endsWith(".ts")
    );
    const missing: string[] = [];

    for (const file of sourceFiles) {
      const packageDir = file.slice(0, file.indexOf(`${path.sep}src${path.sep}`));
      const packageJson = readJson(path.join(packageDir, "package.json"));
      const ownName = String(packageJson.name);
      const deps = packageJson.dependencies as Record<string, string> | undefined;
      const text = readFileSync(file, "utf8");
      for (const match of text.matchAll(/from\s+["'](@office-dsl\/[^"'/]+)(?:\/[^"']*)?["']/g)) {
        const imported = match[1]!;
        if (imported === ownName || !workspaceNames.has(imported)) continue;
        if (deps?.[imported] !== "workspace:*") {
          missing.push(`${path.relative(repoRoot, file)} imports ${imported}`);
        }
      }
    }

    expect(missing).toEqual([]);
  });

  it("keeps workspace package versions in lockstep", async () => {
    const packageFiles = [
      ...(await listFiles(path.join(repoRoot, "packages"))),
      ...(await listFiles(path.join(repoRoot, "apps")))
    ].filter((file) => file.endsWith("package.json"));
    const versions = packageFiles.map((file) => [
      path.relative(repoRoot, file),
      readJson(file).version
    ]);

    expect(versions).toEqual(versions.map(([file]) => [file, "0.12.0"]));
  });
});
