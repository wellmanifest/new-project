import http from "node:http";
import { readFile } from "node:fs/promises";
import { createDefaultRegistry, Runtime, type RuntimeApprovalParty } from "@office-dsl/dsl-runtime";
import { FileTaskStore } from "@office-dsl/dsl-runtime/store";
import { planFromNaturalLanguage } from "@office-dsl/llm-planner";
import {
  diagnoseIntentContractDsl,
  questionsForParty,
  validateIntentContractDsl,
  type IntentContractDsl
} from "@office-dsl/intent-contract-model";

const runtime = new Runtime();
const store = new FileTaskStore();
const port = Number(process.env.PORT ?? 3000);

export const server = http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url ?? "/", `http://${req.headers.host}`);
    if (req.method === "GET" && url.pathname === "/")
      return send(res, await readFile("apps/web/public/index.html", "utf8"), "text/html");
    if (req.method === "GET" && url.pathname === "/openapi.json") return sendJson(res, openApi());
    if (req.method === "GET" && url.pathname === "/api/actions") {
      return sendJson(
        res,
        createDefaultRegistry()
          .list()
          .map(({ name, risk, capability, requiresConfirmation }) => ({
            name,
            risk,
            capability,
            requiresConfirmation
          }))
      );
    }
    if (req.method === "GET" && url.pathname === "/api/connectors") {
      return sendJson(res, [
        {
          id: "mock",
          sources: [
            "mock.customers",
            "mock.invoices",
            "mock.employees",
            "mock.activity_logs",
            "mock.outbox"
          ]
        }
      ]);
    }
    if (req.method === "POST" && url.pathname === "/api/tasks") {
      const body = await readJson(req);
      const dsl = await planFromNaturalLanguage(String(body.input ?? ""), { mode: "mock" });
      const session = runtime.create(dsl, {
        verdict: "PASS",
        score: 0.95,
        recommended_action: "ACCEPT"
      });
      await store.save(session);
      return sendJson(res, session, 201);
    }
    const match = url.pathname.match(/^\/api\/tasks\/([^/]+)(?:\/([^/]+))?$/);
    if (match) {
      const session = await store.load(match[1]);
      const action = match[2];
      if (req.method === "GET" && !action) return sendJson(res, session);
      if (req.method === "GET" && action === "audit") return sendJson(res, session.audit);
      if (req.method === "POST" && action === "answers") {
        const body = await readJson(req);
        runtime.answer(session, String(body.questionId), String(body.answer));
      } else if (req.method === "POST" && action === "confirm") {
        const body = await readJson(req);
        runtime.confirm(
          session,
          String(body.confirmationId),
          String(body.planHash ?? session.planHash)
        );
      } else if (req.method === "POST" && action === "reject") runtime.reject(session);
      else if (req.method === "POST" && action === "cancel") runtime.cancel(session);
      else if (req.method === "POST" && action === "execute") {
        const body = await readJson(req);
        await runtime.execute(session, body.execute === true);
      } else if (req.method === "POST" && action === "approve") {
        const body = await readJson(req);
        const party = String(body.party ?? "");
        if (party !== "Human1" && party !== "Human2") {
          return sendJson(res, { error: "party must be Human1 or Human2" }, 400);
        }
        const hash = body.hash ? String(body.hash) : session.intentContractHash;
        runtime.approveIntentContract(session, party as RuntimeApprovalParty, hash);
      } else if (req.method === "POST" && action === "dsl") {
        const body = await readJson(req);
        const dsl = body.dsl as IntentContractDsl;
        const validation = validateIntentContractDsl(dsl);
        if (!validation.ok) {
          return sendJson(res, { error: "DSL validation failed", issues: validation.issues }, 400);
        }
        runtime.updateIntentContractDsl(
          session,
          dsl,
          typeof body.reason === "string" ? body.reason : "DSL updated via API"
        );
      } else if (req.method === "GET" && action === "events") {
        return sendJson(res, session.audit.history);
      } else if (req.method === "GET" && action === "approvals") {
        return sendJson(res, session.approvals);
      } else if (req.method === "GET" && action === "questions") {
        const diagnosis = diagnoseIntentContractDsl(session.intentContractDsl);
        const party = url.searchParams.get("party");
        const questions = party
          ? questionsForParty(diagnosis, party as RuntimeApprovalParty)
          : diagnosis.generatedQuestions;
        return sendJson(res, { finalizationReady: diagnosis.finalizationReady, questions });
      } else return sendJson(res, { error: "Not found" }, 404);
      await store.save(session);
      return sendJson(res, session);
    }
    return sendJson(res, { error: "Not found" }, 404);
  } catch (error) {
    return sendJson(res, { error: error instanceof Error ? error.message : String(error) }, 500);
  }
});

if (process.env.NODE_ENV !== "test") {
  server.listen(port, () =>
    console.log(`office-dsl backend listening on http://127.0.0.1:${port}`)
  );
}

async function readJson(req: http.IncomingMessage): Promise<Record<string, unknown>> {
  const chunks: Buffer[] = [];
  for await (const chunk of req) chunks.push(Buffer.from(chunk));
  return chunks.length
    ? (JSON.parse(Buffer.concat(chunks).toString("utf8")) as Record<string, unknown>)
    : {};
}

function sendJson(res: http.ServerResponse, value: unknown, status = 200): void {
  send(res, JSON.stringify(value, null, 2), "application/json", status);
}

function send(res: http.ServerResponse, body: string, type: string, status = 200): void {
  res.writeHead(status, { "content-type": `${type}; charset=utf-8` });
  res.end(body);
}

function openApi(): unknown {
  return {
    openapi: "3.1.0",
    info: { title: "Office DSL MVP API", version: "0.7.2" },
    paths: {
      "/api/tasks": { post: { summary: "Create task from natural language command" } },
      "/api/tasks/{id}": { get: { summary: "Inspect task" } },
      "/api/tasks/{id}/answers": { post: { summary: "Answer clarification" } },
      "/api/tasks/{id}/confirm": { post: { summary: "Confirm plan hash" } },
      "/api/tasks/{id}/reject": { post: { summary: "Reject task" } },
      "/api/tasks/{id}/execute": { post: { summary: "Execute task, dry-run by default" } },
      "/api/tasks/{id}/cancel": { post: { summary: "Cancel task" } },
      "/api/tasks/{id}/approve": {
        post: { summary: "Approve canonical Intent/Contract DSL hash" }
      },
      "/api/tasks/{id}/dsl": { post: { summary: "Update canonical Intent/Contract DSL snapshot" } },
      "/api/tasks/{id}/events": { get: { summary: "Read state-transition event stream" } },
      "/api/tasks/{id}/approvals": { get: { summary: "Read canonical approval records" } },
      "/api/tasks/{id}/questions": { get: { summary: "Read unresolved questions" } },
      "/api/tasks/{id}/audit": { get: { summary: "Read audit record" } },
      "/api/actions": { get: { summary: "List registered actions" } },
      "/api/connectors": { get: { summary: "List mock connectors" } }
    }
  };
}
