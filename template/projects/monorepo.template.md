# Wzorzec Projektowy: Monorepo (`monorepo`)

Manifest jednoplikowy opisujący strukturę monorepo (workspaces npm) z podziałem na `apps/` i `packages/`.

## Zmienne wejściowe

| Zmienna | Opis | Przykład |
| :--- | :--- | :--- |
| `project_name` | Nazwa monorepo | `platform` |
| `app_name` | Nazwa pierwszej aplikacji | `web` |
| `package_name` | Nazwa współdzielonego pakietu | `shared` |

## Manifest

```yaml
variables:
  project_name: platform
  app_name: web
  package_name: shared

directories:
  - "{{ project_name }}"
  - "{{ project_name }}/apps/{{ app_name }}"
  - "{{ project_name }}/packages/{{ package_name }}"

files:
  - path: "{{ project_name }}/package.json"
    type: config
    contents: |
      {
        "name": "{{ project_name }}",
        "private": true,
        "version": "0.1.0",
        "workspaces": ["apps/*", "packages/*"],
        "scripts": {
          "test": "echo \"run per-workspace tests\""
        }
      }

  - path: "{{ project_name }}/apps/{{ app_name }}/package.json"
    type: config
    contents: |
      {
        "name": "@{{ project_name }}/{{ app_name }}",
        "version": "0.1.0",
        "type": "module",
        "dependencies": {
          "@{{ project_name }}/{{ package_name }}": "*"
        }
      }

  - path: "{{ project_name }}/apps/{{ app_name }}/index.js"
    type: source
    contents: |
      import { greeting } from "@{{ project_name }}/{{ package_name }}";

      console.log(greeting("{{ app_name }}"));

  - path: "{{ project_name }}/packages/{{ package_name }}/package.json"
    type: config
    contents: |
      {
        "name": "@{{ project_name }}/{{ package_name }}",
        "version": "0.1.0",
        "type": "module",
        "main": "index.js"
      }

  - path: "{{ project_name }}/packages/{{ package_name }}/index.js"
    type: source
    contents: |
      export function greeting(name) {
        return `Hello from ${name}`;
      }

  - path: "{{ project_name }}/.gitignore"
    type: config
    contents: |
      node_modules/
      dist/

  - path: "{{ project_name }}/README.md"
    type: docs
    contents: |
      # {{ project_name }}

      Monorepo (workspaces) wygenerowane z manifestu jednoplikowego.
```

## Jak wygenerować

1. Renderuj zmienne, utwórz strukturę z manifestu.
2. `npm install` w katalogu głównym (spina workspaces).
