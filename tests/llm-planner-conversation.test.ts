import { readFile } from "node:fs/promises";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { mockPlanConversationHistory } from "../packages/llm-planner/src/index.js";
import {
  diagnoseIntentContractDsl,
  parseConversation,
  validateIntentContractDsl
} from "../packages/intent-contract-model/src/index.js";

const fixturePath = path.join(
  process.cwd(),
  "packages",
  "intent-contract-model",
  "fixtures",
  "human1-human2.conversation.json"
);

describe("conversation-history mock planner", () => {
  it("plans a two-party conversation into a valid partial Intent/Contract DSL", async () => {
    const conversation = parseConversation(await readFile(fixturePath, "utf8"));
    const dsl = mockPlanConversationHistory(conversation);

    expect(validateIntentContractDsl(dsl).ok).toBe(true);
    expect(dsl.version).toBe("intent-contract.dsl.v1");
    expect(dsl.document.type.value).toBe("SERVICE_AGREEMENT");
    expect(dsl.parties.map((party) => party.role.value)).toEqual(["Human1", "Human2"]);
    expect(dsl.intents[0]?.description.source?.id).toBe("msg-001");
  });

  it("preserves every conversation line as a source reference", async () => {
    const conversation = parseConversation(await readFile(fixturePath, "utf8"));
    const dsl = mockPlanConversationHistory(conversation);

    expect(dsl.sourceReferences.map((reference) => reference.id)).toEqual(
      expect.arrayContaining(["msg-001", "msg-002", "msg-003", "msg-004"])
    );
    expect(dsl.sourceReferences.filter((reference) => reference.type === "message")).toHaveLength(
      4
    );
    expect(dsl.payments[0]?.total.value).toEqual({ amount: 4200, currency: "PLN" });
    expect(dsl.payments[0]?.total.source?.id).toBe("msg-002");
    expect(dsl.deadlines[0]?.dueAt.value).toBe("2026-08-14");
    expect(dsl.deadlines[0]?.dueAt.source?.id).toBe("msg-002");
  });

  it("keeps unresolved fields and generated questions instead of guessing completion", async () => {
    const conversation = parseConversation(await readFile(fixturePath, "utf8"));
    const dsl = mockPlanConversationHistory(conversation);
    const diagnosis = diagnoseIntentContractDsl(dsl);

    expect(dsl.contract?.governingLaw.status).toBe("MISSING");
    expect(dsl.questions.map((question) => question.id)).toEqual([
      "governing-law",
      "human2-revision-approval"
    ]);
    expect(diagnosis.finalizationReady).toBe(false);
    expect(diagnosis.blockingReasons).toEqual(
      expect.arrayContaining([
        "contract.governingLaw is MISSING but required for completion.",
        "questions[0].prompt is MISSING but required for completion.",
        "questions[1].prompt is MISSING but required for completion."
      ])
    );
  });
});
