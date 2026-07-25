import { mkdir, readFile, readdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { TaskSession } from "./index.js";

export class FileTaskStore {
  constructor(private baseDir = process.env.OFFICE_DSL_TASK_DIR ?? ".office-dsl") {}

  private taskDir(session: TaskSession): string {
    return path.join(this.baseDir, session.dsl.task.createdBy, "tasks");
  }

  private auditDir(session: TaskSession): string {
    return path.join(this.baseDir, session.dsl.task.createdBy, "audit");
  }

  async save(session: TaskSession): Promise<void> {
    const taskDir = this.taskDir(session);
    const auditDir = this.auditDir(session);
    await mkdir(taskDir, { recursive: true });
    await mkdir(auditDir, { recursive: true });
    await writeFile(
      path.join(taskDir, `${session.id}.json`),
      `${JSON.stringify(session, null, 2)}\n`,
      "utf8"
    );
    await writeFile(
      path.join(auditDir, `${session.id}.json`),
      `${JSON.stringify(session.audit, null, 2)}\n`,
      "utf8"
    );
  }

  async load(id: string): Promise<TaskSession> {
    const file = await this.findFile(id, "tasks");
    return JSON.parse(await readFile(file, "utf8")) as TaskSession;
  }

  async list(): Promise<TaskSession[]> {
    const files = await this.collectFiles("tasks");
    return Promise.all(
      files.map((file) => readFile(file, "utf8").then((text) => JSON.parse(text) as TaskSession))
    );
  }

  private async findFile(id: string, subdir: string): Promise<string> {
    const files = await this.collectFiles(subdir);
    const match = files.find((file) => path.basename(file) === `${id}.json`);
    if (!match) throw new Error(`Task ${id} not found under ${this.baseDir}`);
    return match;
  }

  private async collectFiles(subdir: string): Promise<string[]> {
    const result: string[] = [];
    const entries = await this.safeReaddir(this.baseDir);
    for (const entry of entries) {
      const clientPath = path.join(this.baseDir, entry.name);
      if (!entry.isDirectory()) continue;
      const target = path.join(clientPath, subdir);
      const files = await this.safeReaddir(target);
      for (const file of files) {
        if (file.isFile() && file.name.endsWith(".json")) {
          result.push(path.join(target, file.name));
        }
      }
    }
    return result;
  }

  private async safeReaddir(dir: string) {
    try {
      return await readdir(dir, { withFileTypes: true });
    } catch {
      return [];
    }
  }
}
