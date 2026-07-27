import { spawn } from "node:child_process";
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";

export interface SemanticVerifierInput {
  original_nl?: string | null;
  approved_dsl?: Record<string, unknown> | null;
  rendered_document?: string | null;
  codegen_verifier_input?: Record<string, unknown> | null;
  testgen_verifier_input?: Record<string, unknown> | null;
}

export interface SemanticFinding {
  kind: string;
  path: string;
  message: string;
  severity: "info" | "warning" | "error";
}

export interface SemanticVerificationReport {
  version: "semantic-verifier.report.v1";
  verdict: "PASS" | "FAIL" | "NEEDS_REVIEW";
  score: number;
  findings: SemanticFinding[];
  missing_requirements: string[];
  contradictions: string[];
  unauthorized_assumptions: string[];
  document_mismatches: string[];
  code_mismatches: string[];
  uncovered_acceptance_criteria: string[];
  recommended_action: "ACCEPT" | "REGENERATE" | "ASK_USER" | "BLOCK";
  explanation: string;
}

export interface PythonSemanticVerifierOptions {
  python?: string;
  mode?: "mock" | "openrouter" | string;
  cwd?: string;
  env?: NodeJS.ProcessEnv;
}

export interface OfficeDslVerifierOptions extends PythonSemanticVerifierOptions {
  repoRoot: string;
  inputText: string;
  dslText: string;
  planText: string;
  generatedDir: string;
}

export async function runPythonSemanticVerifier(
  input: SemanticVerifierInput,
  options: PythonSemanticVerifierOptions = {}
): Promise<SemanticVerificationReport> {
  const cwd = options.cwd ?? process.cwd();
  const tempDir = await mkdtemp(path.join(os.tmpdir(), "office-dsl-semantic-verifier-"));
  try {
    const inputPath = path.join(tempDir, "semantic-input.json");
    await writeFile(
      inputPath,
      `${JSON.stringify(input, null, 2)}
`,
      "utf8"
    );
    const stdout = await runPython(
      options.python ?? "python",
      [
        "-m",
        "office_dsl_verifier",
        "--semantic-input",
        inputPath,
        "--mode",
        options.mode ?? "mock"
      ],
      cwd,
      withVerifierPythonPath(options.env ?? process.env, cwd)
    );
    return JSON.parse(stdout) as SemanticVerificationReport;
  } finally {
    await rm(tempDir, { recursive: true, force: true });
  }
}

export async function runOfficeDslVerifier(
  options: OfficeDslVerifierOptions
): Promise<Record<string, unknown>> {
  const dslFile = path.join(options.generatedDir, "verifier-input.dsl.hcl");
  const planFile = path.join(options.generatedDir, "verifier-input.plan.dsl.hcl");
  await writeFile(
    dslFile,
    `${options.dslText.trim()}
`,
    "utf8"
  );
  await writeFile(
    planFile,
    `${options.planText.trim()}
`,
    "utf8"
  );
  const stdout = await runPython(
    options.python ?? "python",
    [
      "-m",
      "office_dsl_verifier",
      "--nl",
      options.inputText.trim(),
      "--dsl",
      dslFile,
      "--plan",
      planFile,
      "--mode",
      options.mode ?? "mock"
    ],
    options.repoRoot,
    withVerifierPythonPath(options.env ?? process.env, options.repoRoot)
  );
  return JSON.parse(stdout) as Record<string, unknown>;
}

export function withVerifierPythonPath(
  env: NodeJS.ProcessEnv,
  cwd = process.cwd()
): NodeJS.ProcessEnv {
  const verifierPath = path.join(cwd, "verifier");
  return {
    ...env,
    PYTHONPATH: env.PYTHONPATH ? `${verifierPath}${path.delimiter}${env.PYTHONPATH}` : verifierPath
  };
}

async function runPython(
  command: string,
  args: string[],
  cwd: string,
  env: NodeJS.ProcessEnv
): Promise<string> {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { cwd, env, windowsHide: true });
    const stdout: Buffer[] = [];
    const stderr: Buffer[] = [];
    child.stdout.on("data", (chunk: Buffer) => stdout.push(chunk));
    child.stderr.on("data", (chunk: Buffer) => stderr.push(chunk));
    child.on("error", reject);
    child.on("exit", (code) => {
      const errorOutput = Buffer.concat(stderr).toString("utf8").trim();
      if (code === 0) resolve(Buffer.concat(stdout).toString("utf8"));
      else reject(new Error(errorOutput || `Python verifier failed with exit code ${code}`));
    });
  });
}
