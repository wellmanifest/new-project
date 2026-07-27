#!/usr/bin/env node
import readline from "node:readline";
import { Runtime } from "../../dsl-runtime/src/index.js";
import { FileTaskStore } from "../../dsl-runtime/src/store.js";
import { planFromNaturalLanguage } from "../../llm-planner/src/index.js";

const runtime = new Runtime();
const store = new FileTaskStore();

interface ShellContext {
  lastTaskId?: string;
}

function mockVerification(input: string, dsl: unknown): unknown {
  const combined = `${input} ${JSON.stringify(dsl)}`.toLowerCase();
  const unauthorized = input.toLowerCase().includes("nie wysy") && combined.includes("email.send");
  return {
    verdict: unauthorized ? "FAIL" : "PASS",
    score: unauthorized ? 0.2 : 0.95,
    intent_coverage: unauthorized ? 0.7 : 0.95,
    missing_requirements: [],
    unauthorized_actions: unauthorized ? ["email.send"] : [],
    contradictions: [],
    policy_violations: [],
    requires_confirmation: combined.includes("email.send") ? ["email.send"] : [],
    explanation: unauthorized
      ? "DSL sends email although user requested drafts only."
      : "Mock verifier accepted DSL.",
    recommended_action: unauthorized ? "REGENERATE" : "ACCEPT"
  };
}

function out(value: unknown): void {
  console.log(JSON.stringify(value, null, 2));
}

function usage(): void {
  console.log(`office-dsl shell commands:
  create "natural language command"
  get <taskId>
  plan <taskId>
  list
  answer <taskId> <questionId> <answer>
  confirm <taskId> <confirmationId> [planHash]
  approve <taskId> <Human1|Human2> [hash]
  reject <taskId>
  cancel <taskId>
  execute <taskId> [--execute]
  audit <taskId>
  help
  exit`);
}

function shiftQuoted(args: string[]): string {
  if (args.length === 0) return "";
  if (args[0]!.startsWith('"')) {
    const parts: string[] = [];
    let i = 0;
    while (i < args.length) {
      parts.push(args[i]!);
      if (args[i]!.endsWith('"')) break;
      i++;
    }
    return parts.join(" ").slice(1, -1);
  }
  return args[0]!;
}

const commands: Record<string, (args: string[], ctx: ShellContext) => Promise<void>> = {
  create: async (args, ctx) => {
    const input = shiftQuoted(args);
    const dsl = await planFromNaturalLanguage(input, { mode: "mock" });
    const session = runtime.create(dsl, mockVerification(input, dsl));
    await store.save(session);
    ctx.lastTaskId = session.id;
    out({
      taskId: session.id,
      state: session.state,
      planHash: session.planHash,
      intentContractHash: session.intentContractHash
    });
  },
  get: async (args) => {
    const id = required(args[0], "TASK_ID");
    const session = await store.load(id);
    out({
      taskId: session.id,
      state: session.state,
      dsl: session.dsl,
      plan: session.plan,
      planHash: session.planHash,
      intentContractHash: session.intentContractHash,
      approvals: session.approvals,
      answers: session.answers,
      confirmations: session.confirmations
    });
  },
  plan: async (args) => {
    const id = required(args[0], "TASK_ID");
    const session = await store.load(id);
    out({ taskId: session.id, plan: session.plan, planHash: session.planHash });
  },
  list: async () => {
    const sessions = await store.list();
    out(sessions.map((s) => ({ taskId: s.id, state: s.state, input: s.dsl.task.input })));
  },
  answer: async (args) => {
    const id = required(args[0], "TASK_ID");
    const questionId = required(args[1], "QUESTION_ID");
    const answer = args.slice(2).join(" ");
    const session = await store.load(id);
    runtime.answer(session, questionId, answer);
    await store.save(session);
    out({ taskId: session.id, state: session.state, answers: session.answers });
  },
  confirm: async (args) => {
    const id = required(args[0], "TASK_ID");
    const confirmationId = required(args[1], "CONFIRMATION_ID");
    const planHash = args[2];
    const session = await store.load(id);
    runtime.confirm(session, confirmationId, planHash ?? session.planHash);
    await store.save(session);
    out({ taskId: session.id, state: session.state, confirmations: session.confirmations });
  },
  approve: async (args) => {
    const id = required(args[0], "TASK_ID");
    const party = required(args[1], "PARTY") as "Human1" | "Human2";
    const session = await store.load(id);
    const hash = args[2] ?? session.intentContractHash;
    const record = runtime.approveIntentContract(session, party, hash);
    await store.save(session);
    out({
      taskId: session.id,
      approval: record,
      bilateral: runtime.hasBilateralIntentContractApproval(session)
    });
  },
  reject: async (args) => {
    const id = required(args[0], "TASK_ID");
    const session = await store.load(id);
    runtime.reject(session);
    await store.save(session);
    out({ taskId: session.id, state: session.state });
  },
  cancel: async (args) => {
    const id = required(args[0], "TASK_ID");
    const session = await store.load(id);
    runtime.cancel(session);
    await store.save(session);
    out({ taskId: session.id, state: session.state });
  },
  execute: async (args) => {
    const id = required(args[0], "TASK_ID");
    const executeFlag = args.includes("--execute");
    const session = await store.load(id);
    const results = await runtime.execute(session, executeFlag);
    await store.save(session);
    out({ taskId: session.id, state: session.state, dryRun: !executeFlag, results });
  },
  audit: async (args) => {
    const id = required(args[0], "TASK_ID");
    const session = await store.load(id);
    out(session.audit);
  }
};

function required(value: string | undefined, name: string): string {
  if (!value) throw new Error(`${name} is required`);
  return value;
}

async function runCommand(line: string, ctx: ShellContext): Promise<boolean> {
  const trimmed = line.trim();
  if (!trimmed) return true;
  const [command, ...args] = trimmed.split(/\s+/);
  if (command === "exit" || command === "quit") return false;
  if (command === "help") {
    usage();
    return true;
  }
  const handler = commands[command];
  if (!handler) {
    console.error(`Unknown command: ${command}`);
    usage();
    return true;
  }
  await handler(args, ctx);
  return true;
}

function main(): void {
  const args = process.argv.slice(2);
  const ctx: ShellContext = {};

  if (args.length > 0) {
    const command = args[0];
    const rest = args.slice(1);
    const handler = commands[command ?? ""];
    if (!handler) {
      console.error(`Unknown command: ${command}`);
      usage();
      process.exitCode = 2;
      return;
    }
    handler(rest, ctx)
      .then(() => process.exit(0))
      .catch((error) => {
        console.error(error instanceof Error ? error.message : String(error));
        process.exitCode = 1;
      });
    return;
  }

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    prompt: "office-dsl> "
  });

  usage();
  rl.prompt();

  rl.on("line", async (line) => {
    try {
      const continueLoop = await runCommand(line, ctx);
      if (!continueLoop) {
        rl.close();
        return;
      }
    } catch (error) {
      console.error(error instanceof Error ? error.message : String(error));
    }
    rl.prompt();
  });

  rl.on("close", () => {
    console.log("Bye");
    process.exit(0);
  });
}

main();
