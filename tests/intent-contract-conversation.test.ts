import { readFile } from "node:fs/promises";
import path from "node:path";
import { describe, expect, it } from "vitest";
import {
  CONVERSATION_VERSION,
  conversationToSourceReferences,
  parseConversation,
  validateConversation,
  type Conversation
} from "../packages/intent-contract-model/src/index.js";

const fixturePath = path.join(
  process.cwd(),
  "packages",
  "intent-contract-model",
  "fixtures",
  "human1-human2.conversation.json"
);

async function loadFixture(): Promise<Conversation> {
  return parseConversation(await readFile(fixturePath, "utf8"));
}

describe("Intent/Contract conversation input model", () => {
  it("parses and validates Human1/Human2 conversation fixtures", async () => {
    const conversation = await loadFixture();
    const result = validateConversation(conversation);

    expect(result.ok).toBe(true);
    expect(conversation.version).toBe(CONVERSATION_VERSION);
    expect(conversation.messages.map((message) => message.speaker)).toEqual([
      "Human1",
      "Human2",
      "Human1",
      "system"
    ]);
  });

  it("rejects invalid versions, duplicate ids, speakers, timestamps, and text", async () => {
    const conversation = await loadFixture();
    const invalid = {
      ...conversation,
      version: "intent-contract.conversation.v0",
      messages: [
        conversation.messages[0],
        { ...conversation.messages[1], id: conversation.messages[0]!.id },
        {
          id: "m-invalid-speaker",
          speaker: "Client",
          timestamp: "2026-07-27T10:02:00.000Z",
          text: "x"
        },
        { id: "m-invalid-time", speaker: "Human1", timestamp: "not a date", text: "x" },
        { id: "m-empty-text", speaker: "Human2", timestamp: "2026-07-27T10:03:00.000Z", text: " " }
      ]
    };

    const result = validateConversation(invalid);
    expect(result.ok).toBe(false);
    expect(result.issues.map((issue) => issue.path)).toEqual(
      expect.arrayContaining([
        "version",
        "messages[1].id",
        "messages[2].speaker",
        "messages[3].timestamp",
        "messages[4].text"
      ])
    );
  });

  it("throws readable parse errors for invalid conversations", async () => {
    const conversation = await loadFixture();

    expect(() =>
      parseConversation(JSON.stringify({ ...conversation, messages: "Human1: hello" }))
    ).toThrow(/messages: must be an array/);
  });

  it("maps conversation messages into traceable source references", async () => {
    const conversation = await loadFixture();
    const references = conversationToSourceReferences(conversation);

    expect(references).toEqual([
      {
        type: "message",
        id: "msg-001",
        speaker: "Human1",
        quote: "Potrzebuje umowy serwisowej na konfiguracje panelu analitycznego."
      },
      {
        type: "message",
        id: "msg-002",
        speaker: "Human2",
        quote: "Moge to wykonac za 4200 PLN netto z terminem do 2026-08-14."
      },
      {
        type: "message",
        id: "msg-003",
        speaker: "Human1",
        quote: "Akceptuje kwote, ale prosze dodac dwie rundy poprawek po odbiorze."
      },
      {
        type: "message",
        id: "msg-004",
        speaker: "system",
        quote: "System oznaczyl warunek poprawek jako wymagajacy potwierdzenia Human2."
      }
    ]);
  });
});
