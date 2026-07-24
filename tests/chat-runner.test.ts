import { existsSync } from "node:fs";
import { mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import {
  discoverChatScenarios,
  parseChat,
  runChatScenario,
  validateChatDslText
} from "../packages/example-runner/src/index.js";

const repoRoot = process.cwd();

async function runChat(
  id: string
): Promise<{ generatedRoot: string; result: Awaited<ReturnType<typeof runChatScenario>> }> {
  const generatedRoot = await mkdtemp(path.join(os.tmpdir(), `examples-chat-${id}-`));
  const result = await runChatScenario({
    repoRoot,
    scenarioDir: path.join(repoRoot, "examples-chat", id),
    generatedRoot
  });
  return { generatedRoot, result };
}

describe("examples-chat runner", () => {
  it("parses chat authors, line numbers, and event order", () => {
    const parsed = parseChat("@user1 Hello\n\n@user2 Zgoda.\n");
    expect(parsed).toEqual([
      { event: 1, line: 1, author: "user1", text: "Hello", raw: "@user1 Hello" },
      { event: 2, line: 3, author: "user2", text: "Zgoda.", raw: "@user2 Zgoda." }
    ]);
  });

  it("discovers the four chat scenarios", async () => {
    const scenarios = await discoverChatScenarios(repoRoot);
    expect(scenarios.map((scenario) => path.basename(scenario))).toEqual([
      "01-short-agreement",
      "02-long-negotiation-agreement",
      "03-short-conversation-cancelled",
      "04-long-negotiation-cancelled"
    ]);
  });

  it("updates the speaking party contract and merges compatible values", async () => {
    const { generatedRoot, result } = await runChat("01-short-agreement");
    expect(result.ok).toBe(true);
    const partyContract = await readFile(
      path.join(generatedRoot, "001-user1.party-contract.dsl.hcl"),
      "utf8"
    );
    validateChatDslText(partyContract);
    expect(partyContract).toContain('document "PARTY_CONTRACT" {');
    expect(partyContract).toContain('field "PRICE" {');
    expect(partyContract).toContain('value = "5000 PLN"');

    const merged = await readFile(
      path.join(generatedRoot, "007-user1.merged-contract.dsl.hcl"),
      "utf8"
    );
    validateChatDslText(merged);
    expect(merged).toContain('document "MERGED_CONTRACT" {');
    expect(merged).toContain('accepted_by = ["USER1", "USER2"]');
    expect(merged).not.toContain('conflict "PRICE"');
    await rm(generatedRoot, { recursive: true, force: true });
  });

  it("detects conflicts before the parties converge", async () => {
    const { generatedRoot, result } = await runChat("02-long-negotiation-agreement");
    expect(result.ok).toBe(true);
    const status = JSON.parse(
      await readFile(path.join(generatedRoot, "002-user2.status.json"), "utf8")
    ) as { conflicts: Array<{ field: string; values: string[] }> };
    expect(status.conflicts.some((conflict) => conflict.field === "price")).toBe(true);
    await rm(generatedRoot, { recursive: true, force: true });
  });

  it("writes a readable diff when a party changes position", async () => {
    const { generatedRoot, result } = await runChat("02-long-negotiation-agreement");
    expect(result.ok).toBe(true);
    const diff = await readFile(path.join(generatedRoot, "003-user1.diff.md"), "utf8");
    expect(diff).toContain("Changed price: 4000 PLN -> 5000 PLN");
    await rm(generatedRoot, { recursive: true, force: true });
  });

  it("does not create final artifacts after approval from only one side", async () => {
    const tmp = await mkdtemp(path.join(os.tmpdir(), "one-sided-approval-"));
    const scenarioDir = path.join(tmp, "scenario");
    await mkdir(path.join(scenarioDir, "out"), { recursive: true });
    const chat = (
      await readFile(path.join(repoRoot, "examples-chat", "01-short-agreement", "chat.txt"), "utf8")
    )
      .split(/\r?\n/)
      .filter(Boolean)
      .slice(0, 6)
      .join("\n");
    await writeFile(path.join(scenarioDir, "chat.txt"), `${chat}\n`, "utf8");
    await writeFile(
      path.join(scenarioDir, "scenario.json"),
      JSON.stringify(
        {
          version: "example-chat.scenario.v1",
          id: "one-sided-approval",
          title: "One sided approval",
          input: { chat: "chat.txt" },
          expected: { summary: "out/expected.summary.json" }
        },
        null,
        2
      ),
      "utf8"
    );
    await writeFile(
      path.join(scenarioDir, "out", "expected.summary.json"),
      JSON.stringify(
        { id: "one-sided-approval", outcome: "NEGOTIATING", eventCount: 6, finalCreated: false },
        null,
        2
      ),
      "utf8"
    );
    const result = await runChatScenario({
      repoRoot,
      scenarioDir,
      generatedRoot: path.join(tmp, "generated")
    });
    expect(result.ok).toBe(true);
    expect(existsSync(path.join(tmp, "generated", "final", "final-contract.dsl.hcl"))).toBe(false);
    expect(existsSync(path.join(tmp, "generated", "final", "contract.pdf"))).toBe(false);
    await rm(tmp, { recursive: true, force: true });
  });

  it("invalidates approval after a merged contract change", async () => {
    const { generatedRoot, result } = await runChat("02-long-negotiation-agreement");
    expect(result.ok).toBe(true);
    expect(result.summary.approvals.some((approval) => approval.status === "INVALIDATED")).toBe(
      true
    );
    const status = JSON.parse(
      await readFile(path.join(generatedRoot, "013-user2.status.json"), "utf8")
    ) as { approvals: Array<{ status: string; invalidatedByLine?: number }> };
    expect(
      status.approvals.some(
        (approval) => approval.status === "INVALIDATED" && approval.invalidatedByLine === 13
      )
    ).toBe(true);
    await rm(generatedRoot, { recursive: true, force: true });
  });

  it("finalizes only after both parties approve the same current hash", async () => {
    const { generatedRoot, result } = await runChat("01-short-agreement");
    expect(result.summary.outcome).toBe("AGREED");
    expect(result.summary.finalCreated).toBe(true);
    const approvals = JSON.parse(
      await readFile(path.join(generatedRoot, "final", "approvals.json"), "utf8")
    ) as { hash: string; approvals: Array<{ party: string; approvedHash: string }> };
    expect(new Set(approvals.approvals.map((approval) => approval.party))).toEqual(
      new Set(["user1", "user2"])
    );
    expect(approvals.approvals.every((approval) => approval.approvedHash === approvals.hash)).toBe(
      true
    );
    const finalDsl = await readFile(
      path.join(generatedRoot, "final", "final-contract.dsl.hcl"),
      "utf8"
    );
    validateChatDslText(finalDsl);
    expect(finalDsl).toContain('document "FINAL_CONTRACT" {');
    expect(finalDsl.trim().startsWith("{")).toBe(false);
    expect(existsSync(path.join(generatedRoot, "final", "contract.pdf"))).toBe(true);
    await rm(generatedRoot, { recursive: true, force: true });
  });

  it("does not create final contract or PDF for cancelled scenarios", async () => {
    for (const id of ["03-short-conversation-cancelled", "04-long-negotiation-cancelled"]) {
      const { generatedRoot, result } = await runChat(id);
      expect(result.summary.outcome).toBe("CANCELLED");
      expect(result.summary.finalCreated).toBe(false);
      expect(existsSync(path.join(generatedRoot, "final", "final-contract.dsl.hcl"))).toBe(false);
      expect(existsSync(path.join(generatedRoot, "final", "contract.pdf"))).toBe(false);
      await rm(generatedRoot, { recursive: true, force: true });
    }
  });

  it("validates generated .dsl.hcl artifacts as HCL-highlighted DSL, not JSON", async () => {
    const { generatedRoot, result } = await runChat("01-short-agreement");
    expect(result.ok).toBe(true);
    for (const file of [
      path.join(generatedRoot, "001-user1.intent-contract.dsl.hcl"),
      path.join(generatedRoot, "001-user1.party-contract.dsl.hcl"),
      path.join(generatedRoot, "007-user1.merged-contract.dsl.hcl"),
      path.join(generatedRoot, "final", "final-contract.dsl.hcl"),
      path.join(generatedRoot, "final", "annex.dsl.hcl")
    ]) {
      const dsl = await readFile(file, "utf8");
      expect(() => JSON.parse(dsl)).toThrow();
      expect(dsl).toMatch(/^document /);
      validateChatDslText(dsl);
    }
    await rm(generatedRoot, { recursive: true, force: true });
  });
  it("writes default generated outputs beside the chat scenario", async () => {
    const scenarioDir = path.join(repoRoot, "examples-chat", "01-short-agreement");
    const generatedRoot = path.join(scenarioDir, "generated");
    await rm(generatedRoot, { recursive: true, force: true });

    const result = await runChatScenario({ repoRoot, scenarioDir });

    expect(result.generatedDir).toBe(generatedRoot);
    expect(existsSync(path.join(generatedRoot, "001-user1.intent-contract.dsl.hcl"))).toBe(true);
    expect(existsSync(path.join(generatedRoot, "001-user1.party-contract.dsl.hcl"))).toBe(true);
    expect(existsSync(path.join(generatedRoot, "final", "final-contract.dsl.hcl"))).toBe(true);
    await rm(generatedRoot, { recursive: true, force: true });
  });
  it("executes all four scenarios with expected outcomes", async () => {
    const expected = new Map([
      ["01-short-agreement", "AGREED"],
      ["02-long-negotiation-agreement", "AGREED"],
      ["03-short-conversation-cancelled", "CANCELLED"],
      ["04-long-negotiation-cancelled", "CANCELLED"]
    ]);
    for (const [id, outcome] of expected) {
      const { generatedRoot, result } = await runChat(id);
      expect(result.ok).toBe(true);
      expect(result.summary.outcome).toBe(outcome);
      await rm(generatedRoot, { recursive: true, force: true });
    }
  });
});
