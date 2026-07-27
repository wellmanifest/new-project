import { describe, expect, it } from "vitest";
import { buildExamplesArtifactsIndex } from "../packages/example-runner/src/examples-index.js";

const repoRoot = process.cwd();

describe("examples artifacts index", () => {
  it("merges office, chat, and recruitment example locations into one markdown file", async () => {
    const markdown = await buildExamplesArtifactsIndex(repoRoot);

    expect(markdown).toContain("## Office Examples");
    expect(markdown).toContain("## Chat Examples");
    expect(markdown).toContain("## Recruitment Examples");

    for (const scenario of [
      "01-read-only-report",
      "02-clarification",
      "03-email-drafts",
      "04-confirmed-send",
      "05-policy-denial",
      "06-log-analysis",
      "01-short-agreement",
      "02-long-negotiation-agreement",
      "03-short-conversation-cancelled",
      "04-long-negotiation-cancelled",
      "01-multi-candidate",
      "02-single-candidate-agreement",
      "03-negotiated-two-candidates",
      "04-ocr-candidate-cancelled"
    ]) {
      expect(markdown).toContain(scenario);
    }

    expect(markdown).toContain("[expected/](../examples/01-read-only-report/expected)");
    expect(markdown).toContain(
      "[001-anna-nowak](../examples-recruitment/01-multi-candidate/001-anna-nowak)"
    );
    expect(markdown).toContain("Candidates and document processes:");
  });
});
