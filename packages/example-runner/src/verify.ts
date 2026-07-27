#!/usr/bin/env node
import { spawn } from "node:child_process";

interface Step {
  label: string;
  command: string;
  args: string[];
  env?: NodeJS.ProcessEnv;
}

const pythonPath = process.env.PYTHONPATH
  ? `verifier${process.platform === "win32" ? ";" : ":"}${process.env.PYTHONPATH}`
  : "verifier";

const steps: Step[] = [
  { label: "typecheck", command: "corepack", args: ["pnpm", "run", "typecheck"] },
  { label: "lint", command: "corepack", args: ["pnpm", "run", "lint"] },
  {
    label: "documentation generation",
    command: "corepack",
    args: ["pnpm", "run", "docs:generate"]
  },
  { label: "format", command: "corepack", args: ["pnpm", "run", "format"] },
  {
    label: "documentation freshness",
    command: "git",
    args: [
      "diff",
      "--exit-code",
      "--",
      "README.md",
      "docs/documentation-index.md",
      "docs/examples-artifacts-index.md",
      "examples",
      "examples-chat",
      "examples-recruitment"
    ]
  },
  { label: "typescript tests", command: "corepack", args: ["pnpm", "test"] },
  {
    label: "python verifier tests",
    command: "python",
    args: ["-m", "pytest", "verifier/tests", "-q"],
    env: { ...process.env, PYTHONPATH: pythonPath }
  },
  { label: "example runner", command: "corepack", args: ["pnpm", "run", "examples:run"] },
  { label: "chat example runner", command: "corepack", args: ["pnpm", "run", "examples-chat:run"] },
  {
    label: "recruitment example runner",
    command: "corepack",
    args: ["pnpm", "run", "examples-recruitment:run"]
  },
  { label: "git diff whitespace", command: "git", args: ["diff", "--check"] }
];

async function main(argv: string[]): Promise<void> {
  if (argv[0] === "python-test") {
    const pythonStep = steps.find((step) => step.label === "python verifier tests");
    if (!pythonStep) throw new Error("python verifier tests step is missing");
    await runStep(pythonStep);
    return;
  }
  for (const step of steps) await runStep(step);
}

function resolveStep(step: Step): { command: string; args: string[] } {
  if (process.platform !== "win32") return { command: step.command, args: step.args };
  if (step.command === "corepack") {
    return { command: "cmd.exe", args: ["/d", "/s", "/c", "corepack", ...step.args] };
  }
  if (step.command === "git") return { command: "git.exe", args: step.args };
  if (step.command === "python") return { command: "python.exe", args: step.args };
  return { command: step.command, args: step.args };
}

async function runStep(step: Step): Promise<void> {
  console.log(`\n== ${step.label} ==`);
  await new Promise<void>((resolve, reject) => {
    const resolved = resolveStep(step);
    const child = spawn(resolved.command, resolved.args, {
      cwd: process.cwd(),
      env: step.env ?? process.env,

      stdio: "inherit",
      windowsHide: true
    });
    child.on("error", reject);
    child.on("exit", (code) => {
      if (code === 0) resolve();
      else reject(new Error(`${step.label} failed with exit code ${code}`));
    });
  });
}

main(process.argv.slice(2)).catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
});
