#!/usr/bin/env node
import { readFile } from "node:fs/promises";
import { parseTaskDsl, renderHumanDsl } from "../../dsl-model/src/index.js";
import { Runtime } from "../../dsl-runtime/src/index.js";
import { FileTaskStore } from "../../dsl-runtime/src/store.js";
import { planFromNaturalLanguage } from "../../llm-planner/src/index.js";

const runtime = new Runtime();
const store = new FileTaskStore();

async function main(argv: string[]): Promise<void> {
  const [command, ...rest] = argv;
  const json = rest.includes("--json");
  const executeFlag = rest.includes("--execute");
  const args = rest.filter((arg) => arg !== "--json" && arg !== "--execute");
  try {
    if (command === "plan" || command === "run") {
      const input = args.join(" ");
      const dsl = await planFromNaturalLanguage(input, { mode: "mock" });
      const session = runtime.create(dsl, mockVerification(input, dsl));
      await store.save(session);
      return output(json, { taskId: session.id, state: session.state, dsl, humanDsl: renderHumanDsl(dsl), plan: session.plan, planHash: session.planHash });
    }
    if (command === "validate") {
      const dsl = parseTaskDsl(await readFile(required(args[0], "DSL_FILE"), "utf8"));
      return output(json, { ok: true, dsl, humanDsl: renderHumanDsl(dsl) });
    }
    if (command === "inspect") return output(json, await store.load(required(args[0], "TASK_ID")));
    if (command === "answer") {
      const session = await store.load(required(args[0], "TASK_ID"));
      runtime.answer(session, required(args[1], "QUESTION_ID"), args.slice(2).join(" "));
      await store.save(session);
      return output(json, { taskId: session.id, state: session.state });
    }
    if (command === "confirm") {
      const session = await store.load(required(args[0], "TASK_ID"));
      runtime.confirm(session, required(args[1], "CONFIRMATION_ID"), args[2] ?? session.planHash);
      await store.save(session);
      return output(json, { taskId: session.id, state: session.state, planHash: session.planHash });
    }
    if (command === "reject") {
      const session = await store.load(required(args[0], "TASK_ID"));
      runtime.reject(session);
      await store.save(session);
      return output(json, { taskId: session.id, state: session.state });
    }
    if (command === "execute") {
      const session = await store.load(required(args[0], "TASK_ID"));
      const results = await runtime.execute(session, executeFlag);
      await store.save(session);
      return output(json, { taskId: session.id, state: session.state, dryRun: !executeFlag, results, audit: session.audit });
    }
    if (command === "history") {
      const items = (await store.list()).map((session) => ({ taskId: session.id, state: session.state, input: session.dsl.task.input }));
      return output(json, items);
    }
    help();
    process.exitCode = 2;
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    if (json) console.log(JSON.stringify({ error: message }, null, 2));
    else console.error(`Error: ${message}`);
    process.exitCode = 1;
  }
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
    explanation: unauthorized ? "DSL sends email although user requested drafts only." : "Mock verifier accepted DSL.",
    recommended_action: unauthorized ? "REGENERATE" : "ACCEPT"
  };
}

function output(json: boolean, value: unknown): void {
  console.log(json ? JSON.stringify(value, null, 2) : JSON.stringify(value, null, 2));
}

function required(value: string | undefined, name: string): string {
  if (!value) throw new Error(`${name} is required`);
  return value;
}

function help(): void {
  console.log(`office-dsl commands:
  plan "natural language command" [--json]
  run "natural language command" [--json]
  validate examples/01-read-only-report/expected.json
  inspect TASK_ID [--json]
  answer TASK_ID QUESTION_ID "answer"
  confirm TASK_ID CONFIRMATION_ID [PLAN_HASH]
  reject TASK_ID
  execute TASK_ID [--execute] [--json]
  history [--json]`);
}

await main(process.argv.slice(2));
