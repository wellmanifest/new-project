# Wzorzec Projektowy: Usługa Node.js/Express (`nodejs-service`)

Manifest jednoplikowy opisujący usługę HTTP w Node.js z Express, strukturą `src/` i testami.

## Zmienne wejściowe

| Zmienna | Opis | Przykład |
| :--- | :--- | :--- |
| `project_name` | Nazwa projektu | `my-service` |
| `port` | Port nasłuchu | `3000` |
| `author` | Autor / właściciel | `Jan Kowalski` |

## Manifest

```yaml
variables:
  project_name: my-service
  port: 3000
  author: Jan Kowalski

directories:
  - "{{ project_name }}"
  - "{{ project_name }}/src"
  - "{{ project_name }}/test"

files:
  - path: "{{ project_name }}/package.json"
    type: config
    contents: |
      {
        "name": "{{ project_name }}",
        "version": "0.1.0",
        "type": "module",
        "main": "src/server.js",
        "scripts": {
          "start": "node src/server.js",
          "dev": "node --watch src/server.js",
          "test": "node --test"
        },
        "author": "{{ author }}",
        "dependencies": {
          "express": "^4.19.2"
        }
      }

  - path: "{{ project_name }}/src/server.js"
    type: source
    contents: |
      import express from "express";

      const app = express();
      const PORT = process.env.PORT || {{ port }};

      app.get("/health", (req, res) => res.json({ status: "ok" }));

      app.listen(PORT, () => console.log(`{{ project_name }} on :${PORT}`));

      export default app;

  - path: "{{ project_name }}/test/health.test.js"
    type: test
    contents: |
      import { test } from "node:test";
      import assert from "node:assert";

      test("smoke", () => assert.ok(true));

  - path: "{{ project_name }}/.gitignore"
    type: config
    contents: |
      node_modules/
      dist/
      .env

  - path: "{{ project_name }}/README.md"
    type: docs
    contents: |
      # {{ project_name }}

      Usługa Node.js/Express wygenerowana z manifestu jednoplikowego.
```

## Jak wygenerować

1. Wczytaj blok `yaml`, renderuj zmienne (Jinja2/EJS).
2. Utwórz katalogi z `directories`, zapisz pliki z `files`.
3. `npm install && npm run dev`.
