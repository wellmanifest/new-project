import { randomUUID } from "node:crypto";
import { DSL_VERSION, TaskDsl } from "../../dsl-model/src/index.js";

export type PlannerMode = "mock" | "openrouter";

export interface PlannerOptions {
  mode?: PlannerMode;
  model?: string;
  timeoutMs?: number;
}

export class PlannerError extends Error {}

export async function planFromNaturalLanguage(
  input: string,
  options: PlannerOptions = {}
): Promise<TaskDsl> {
  const mode =
    options.mode ?? (process.env.OFFICE_DSL_LLM_MODE as PlannerMode | undefined) ?? "mock";
  if (mode === "mock") return mockPlan(input);
  return openRouterPlan(input, options);
}

export function mockPlan(input: string): TaskDsl {
  const text = input.toLowerCase();
  if (text.includes("komend") || text.includes("usun")) {
    return base(
      input,
      "Policy denial",
      [
        {
          id: "blocked-shell",
          description: "Represent unsafe request so policy can deny it",
          action: "file.export",
          with: { path: "../outside.json", command: "rm -rf *" },
          saveAs: "blocked"
        }
      ],
      ["Deny unsafe shell and delete request"]
    );
  }
  if (text.includes("sprzeda")) {
    return base(
      input,
      "Sales report needs clarification",
      [
        {
          id: "ask-period",
          description: "Ask for reporting period",
          action: "user.ask",
          with: {},
          ask: {
            id: "period",
            prompt: "Jaki okres raportu sprzedazy mam przyjac?",
            saveAs: "period"
          }
        },
        {
          id: "query-sales",
          description: "Read mock invoices after clarification",
          action: "database.query",
          with: { dataset: "invoices", kind: "salesReport", periodVar: "period" },
          saveAs: "invoices"
        },
        {
          id: "report",
          description: "Generate sales report",
          action: "report.generate",
          with: { from: "invoices", title: "Sales report" },
          saveAs: "report"
        }
      ],
      ["Ask for period before reporting"]
    );
  }
  if (text.includes("wyslij") || text.includes("wyślij")) {
    return base(
      input,
      "Send prepared reminders",
      [
        overdueStep(),
        {
          id: "prepare",
          description: "Prepare reminder messages",
          action: "email.prepare",
          with: { from: "overdue" },
          saveAs: "messages"
        },
        {
          id: "send",
          description: "Write sent messages to mock outbox",
          action: "email.send",
          with: { from: "messages" },
          saveAs: "sendResult",
          confirm: {
            id: "send-reminders",
            prompt: "Confirm sending reminders to mock outbox",
            required: true
          }
        }
      ],
      ["Require confirmation before mock send"]
    );
  }
  if (text.includes("wiadom") || text.includes("przypominaj")) {
    return base(
      input,
      "Prepare reminder drafts",
      [
        overdueStep(),
        {
          id: "drafts",
          description: "Prepare reminder drafts without sending",
          action: "email.prepare",
          with: { from: "overdue" },
          saveAs: "drafts"
        }
      ],
      ["Create drafts only", "Do not send messages"]
    );
  }
  if (text.includes("log")) {
    return base(
      input,
      "Invoice log analysis",
      [
        {
          id: "search-logs",
          description: "Search failed invoice logs",
          action: "log.search",
          with: { contains: "invoice failed" },
          saveAs: "logs"
        },
        {
          id: "report",
          description: "Generate log summary",
          action: "report.generate",
          with: { from: "logs", title: "Failed invoice processing attempts" },
          saveAs: "report"
        }
      ],
      ["Read mock logs", "Prepare summary"]
    );
  }
  return base(
    input,
    "Unpaid invoices report",
    [
      overdueStep(),
      {
        id: "report",
        description: "Generate read-only report",
        action: "report.generate",
        with: { from: "overdue", title: "Unpaid invoices older than 30 days" },
        saveAs: "report"
      }
    ],
    ["Read-only report", "No data modification"]
  );
}

async function openRouterPlan(input: string, options: PlannerOptions): Promise<TaskDsl> {
  const apiKey = process.env.OPENROUTER_API_KEY;
  if (!apiKey) throw new PlannerError("OPENROUTER_API_KEY is required for openrouter mode");
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), options.timeoutMs ?? 30000);
  try {
    const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      signal: controller.signal,
      headers: { "content-type": "application/json", authorization: `Bearer ${apiKey}` },
      body: JSON.stringify({
        model: options.model ?? process.env.OPENROUTER_MODEL ?? "openai/gpt-4.1-mini",
        response_format: { type: "json_object" },
        messages: [
          {
            role: "system",
            content: "Return only valid Office DSL v1 JSON. Do not add actions not requested."
          },
          { role: "user", content: input }
        ]
      })
    });
    if (!response.ok) throw new PlannerError(`OpenRouter returned ${response.status}`);
    const body = (await response.json()) as { choices?: Array<{ message?: { content?: string } }> };
    const content = body.choices?.[0]?.message?.content;
    if (!content) throw new PlannerError("OpenRouter returned empty content");
    return JSON.parse(content) as TaskDsl;
  } finally {
    clearTimeout(timeout);
  }
}

function overdueStep(): TaskDsl["steps"][number] {
  return {
    id: "load-overdue",
    description: "Read unpaid invoices older than 30 days",
    action: "database.query",
    with: { dataset: "invoices", kind: "unpaidInvoicesOlderThanDays", days: 30 },
    saveAs: "overdue"
  };
}

function base(
  input: string,
  title: string,
  steps: TaskDsl["steps"],
  expectedResults: string[]
): TaskDsl {
  return {
    version: DSL_VERSION,
    task: { id: `task-${randomUUID()}`, title, input, createdBy: "mock-llm" },
    sources: [
      { id: "customers", connector: "mock", name: "mock.customers" },
      { id: "invoices", connector: "mock", name: "mock.invoices" },
      { id: "employees", connector: "mock", name: "mock.employees" },
      { id: "activity_logs", connector: "mock", name: "mock.activity_logs" }
    ],
    steps,
    output: { format: "json", saveAs: "result" },
    policies: [
      {
        decision: "DENY",
        subject: "shell.command",
        reason: "Arbitrary shell commands are forbidden"
      },
      {
        decision: "REQUIRE",
        subject: "email.send",
        reason: "Sending requires confirmation and mock outbox only"
      }
    ],
    expectedResults,
    errorHandling: { onFailure: "stop" }
  };
}
