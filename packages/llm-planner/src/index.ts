import { randomUUID } from "node:crypto";
import { DSL_VERSION, TaskDsl } from "../../dsl-model/src/index.js";
import {
  INTENT_CONTRACT_DSL_VERSION,
  conversationToSourceReferences,
  createField,
  validateIntentContractDsl,
  type Conversation,
  type ConversationMessage,
  type ConversationSpeaker,
  type IntentContractDsl,
  type SourceReference
} from "../../intent-contract-model/src/index.js";

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
  if (text.includes("wyslij") || text.includes("wyĹ›lij")) {
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

export function mockPlanConversationHistory(conversation: Conversation): IntentContractDsl {
  const sourceReferences = conversationToSourceReferences(conversation);
  const systemSource: SourceReference = {
    type: "system",
    id: `${conversation.id}:mock-conversation-planner`,
    quote: "Deterministic mock planner for intent-contract.conversation.v1"
  };
  const human1 = firstMessageBy(conversation, "Human1");
  const human2 = firstMessageBy(conversation, "Human2");
  const payment = findPayment(conversation.messages);
  const deadline = findDeadline(conversation.messages);
  const revisionMessage = conversation.messages.find((message) =>
    /poprawek|revision/i.test(message.text)
  );

  const dsl: IntentContractDsl = {
    version: INTENT_CONTRACT_DSL_VERSION,
    document: {
      id: `${conversation.id}:document`,
      type: createField("document.type", "SERVICE_AGREEMENT", "CONFIRMED", true, sourceFor(human1)),
      title: createField(
        "document.title",
        "Conversation service agreement draft",
        "ASSUMED",
        false,
        systemSource
      ),
      language: createField("document.language", "pl", "ASSUMED", false, systemSource)
    },
    contract: {
      id: `${conversation.id}:contract`,
      title: createField("contract.title", "Service agreement", "ASSUMED", false, systemSource),
      governingLaw: createField<string>("contract.governingLaw", null, "MISSING", true)
    },
    parties: [
      {
        id: "human1",
        name: createField("parties.human1.name", "Human1", "CONFIRMED", true, sourceFor(human1)),
        role: createField("parties.human1.role", "Human1", "CONFIRMED", true, systemSource)
      },
      {
        id: "human2",
        name: createField("parties.human2.name", "Human2", "CONFIRMED", true, sourceFor(human2)),
        role: createField("parties.human2.role", "Human2", "CONFIRMED", true, systemSource)
      }
    ],
    roles: [
      {
        id: "requester",
        partyId: createField("roles.requester.partyId", "human1", "CONFIRMED", true, systemSource),
        name: createField("roles.requester.name", "requester", "ASSUMED", false, systemSource)
      },
      {
        id: "provider",
        partyId: createField("roles.provider.partyId", "human2", "CONFIRMED", true, systemSource),
        name: createField("roles.provider.name", "provider", "ASSUMED", false, systemSource)
      }
    ],
    intents: [
      {
        id: "conversation-intent",
        requesterPartyId: createField(
          "intents.conversation-intent.requesterPartyId",
          "human1",
          "CONFIRMED",
          true,
          sourceFor(human1)
        ),
        description: createField(
          "intents.conversation-intent.description",
          human1?.text ?? "Conversation started by Human1.",
          human1 ? "CONFIRMED" : "MISSING",
          true,
          sourceFor(human1)
        )
      }
    ],
    subjects: [
      {
        id: "conversation-subject",
        description: createField(
          "subjects.conversation-subject.description",
          human1?.text ?? null,
          human1 ? "INCOMPLETE" : "MISSING",
          true,
          sourceFor(human1)
        )
      }
    ],
    obligations: human2
      ? [
          {
            id: "human2-proposal",
            partyId: createField(
              "obligations.human2-proposal.partyId",
              "human2",
              "CONFIRMED",
              true,
              sourceFor(human2)
            ),
            description: createField(
              "obligations.human2-proposal.description",
              human2.text,
              "INCOMPLETE",
              true,
              sourceFor(human2)
            )
          }
        ]
      : [],
    deliverables: [
      {
        id: "conversation-deliverable",
        description: createField(
          "deliverables.conversation-deliverable.description",
          human1?.text ?? null,
          human1 ? "INCOMPLETE" : "MISSING",
          true,
          sourceFor(human1)
        ),
        ownerPartyId: createField(
          "deliverables.conversation-deliverable.ownerPartyId",
          "human2",
          "ASSUMED",
          false,
          systemSource
        )
      }
    ],
    deadlines: deadline
      ? [
          {
            id: "conversation-deadline",
            forId: createField(
              "deadlines.conversation-deadline.forId",
              "conversation-deliverable",
              "ASSUMED",
              false,
              systemSource
            ),
            dueAt: createField(
              "deadlines.conversation-deadline.dueAt",
              deadline.value,
              "CONFIRMED",
              true,
              sourceFor(deadline.message)
            )
          }
        ]
      : [],
    payments: payment
      ? [
          {
            id: "conversation-payment",
            payerPartyId: createField(
              "payments.conversation-payment.payerPartyId",
              "human1",
              "ASSUMED",
              false,
              systemSource
            ),
            payeePartyId: createField(
              "payments.conversation-payment.payeePartyId",
              "human2",
              "ASSUMED",
              false,
              systemSource
            ),
            total: createField(
              "payments.conversation-payment.total",
              { amount: payment.amount, currency: payment.currency },
              "CONFIRMED",
              true,
              sourceFor(payment.message)
            )
          }
        ]
      : [],
    conditions: [],
    dependencies: [],
    acceptanceCriteria: revisionMessage
      ? [
          {
            id: "revision-rounds",
            description: createField(
              "acceptanceCriteria.revision-rounds.description",
              revisionMessage.text,
              "CONFIRMED",
              true,
              sourceFor(revisionMessage)
            ),
            appliesToId: createField(
              "acceptanceCriteria.revision-rounds.appliesToId",
              "conversation-deliverable",
              "ASSUMED",
              false,
              systemSource
            )
          }
        ]
      : [],
    exclusions: [],
    assumptions: [
      {
        id: "mock-conversation-planner",
        description: createField(
          "assumptions.mock-conversation-planner.description",
          "Conversation history was converted by deterministic mock rules; unresolved legal and semantic details remain explicit questions.",
          "ASSUMED",
          false,
          systemSource
        )
      }
    ],
    risks: [],
    conflicts: [],
    questions: [
      {
        id: "governing-law",
        targetPartyId: createField(
          "questions.governing-law.targetPartyId",
          "human1",
          "ASSUMED",
          true,
          systemSource
        ),
        field: "contract.governingLaw",
        prompt: createField(
          "questions.governing-law.prompt",
          "Jakie prawo wlasciwe ma obowiazywac dla umowy?",
          "MISSING",
          true,
          systemSource
        )
      },
      ...(revisionMessage
        ? [
            {
              id: "human2-revision-approval",
              targetPartyId: createField(
                "questions.human2-revision-approval.targetPartyId",
                "human2",
                "ASSUMED",
                true,
                sourceFor(revisionMessage)
              ),
              field: "acceptanceCriteria.revision-rounds.description",
              prompt: createField(
                "questions.human2-revision-approval.prompt",
                "Czy Human2 akceptuje warunek rund poprawek zaproponowany przez Human1?",
                "MISSING",
                true,
                sourceFor(revisionMessage)
              )
            }
          ]
        : [])
    ],
    approvals: [],
    sourceReferences: [...sourceReferences, systemSource],
    render: [
      {
        id: "service-agreement-draft",
        target: createField(
          "render.service-agreement-draft.target",
          "formal_document",
          "ASSUMED",
          false,
          systemSource
        )
      }
    ],
    execution: []
  };

  const validation = validateIntentContractDsl(dsl);
  if (!validation.ok) {
    throw new PlannerError(
      validation.issues.map((issue) => `${issue.path}: ${issue.message}`).join("; ")
    );
  }
  return dsl;
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

function firstMessageBy(
  conversation: Conversation,
  speaker: Exclude<ConversationSpeaker, "system">
): ConversationMessage | undefined {
  return conversation.messages.find((message) => message.speaker === speaker);
}

function sourceFor(message: ConversationMessage | undefined): SourceReference | null {
  return message
    ? {
        type: "message",
        id: message.id,
        speaker: message.speaker,
        quote: message.text
      }
    : null;
}

function findPayment(
  messages: ConversationMessage[]
): { amount: number; currency: "PLN"; message: ConversationMessage } | null {
  for (const message of messages) {
    const match = /(?<amount>\d+(?:[ .]\d+)*)\s*PLN/i.exec(message.text);
    if (match?.groups?.amount) {
      return {
        amount: Number(match.groups.amount.replace(/[ .]/g, "")),
        currency: "PLN",
        message
      };
    }
  }
  return null;
}

function findDeadline(
  messages: ConversationMessage[]
): { value: string; message: ConversationMessage } | null {
  for (const message of messages) {
    const match = /\b\d{4}-\d{2}-\d{2}\b/.exec(message.text);
    if (match) return { value: match[0], message };
  }
  return null;
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
