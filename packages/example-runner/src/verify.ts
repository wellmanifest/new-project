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
  { label: "format", command: "corepack", args: ["pnpm", "run", "format"] },
  { label: "typescript tests", command: "corepack", args: ["pnpm", "test"] },
  {
    label: "python verifier tests",
    command: "python",
    args: ["-m", "pytest", "verifier/tests", "-q"],
    env: { ...process.env, PYTHONPATH: pythonPath }
  },
  { label: "example runner", command: "corepack", args: ["pnpm", "run", "examples:run"] },
  { label: "chat example runner", command: "corepack", args: ["pnpm", "run", "examples-chat:run"] },
  { label: "git diff whitespace", command: "git", args: ["diff", "--check"] }
];

async function main(argv: string[]): Promise<void> {
  if (argv[0] === "python-test") {
    await runStep(steps[4]);
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
