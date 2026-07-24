import { mkdir, readFile, writeFile, readdir } from "node:fs/promises";
import path from "node:path";
import { TaskSession } from "./index.js";

export class FileTaskStore {
  constructor(private dir = process.env.OFFICE_DSL_TASK_DIR ?? ".office-dsl/tasks") {}

  async save(session: TaskSession): Promise<void> {
    await mkdir(this.dir, { recursive: true });
    await writeFile(
      path.join(this.dir, `${session.id}.json`),
      `${JSON.stringify(session, null, 2)}\n`,
      "utf8"
    );
    const auditDir = process.env.OFFICE_DSL_AUDIT_DIR ?? ".office-dsl/audit";
    await mkdir(auditDir, { recursive: true });
    await writeFile(
      path.join(auditDir, `${session.id}.json`),
      `${JSON.stringify(session.audit, null, 2)}\n`,
      "utf8"
    );
  }

  async load(id: string): Promise<TaskSession> {
    return JSON.parse(await readFile(path.join(this.dir, `${id}.json`), "utf8")) as TaskSession;
  }

  async list(): Promise<TaskSession[]> {
    await mkdir(this.dir, { recursive: true });
    const files = (await readdir(this.dir)).filter((file) => file.endsWith(".json"));
    return Promise.all(
      files.map((file) =>
        readFile(path.join(this.dir, file), "utf8").then((text) => JSON.parse(text) as TaskSession)
      )
    );
  }
}
