# Wzorzec Projektowy: Frontend React + Vite (`react-frontend`)

Manifest jednoplikowy opisujący aplikację SPA w React z Vite i TailwindCSS.

## Zmienne wejściowe

| Zmienna | Opis | Przykład |
| :--- | :--- | :--- |
| `project_name` | Nazwa projektu | `my-web` |
| `app_title` | Tytuł aplikacji | `My Web App` |

## Manifest

```yaml
variables:
  project_name: my-web
  app_title: My Web App

directories:
  - "{{ project_name }}"
  - "{{ project_name }}/src"
  - "{{ project_name }}/public"

files:
  - path: "{{ project_name }}/package.json"
    type: config
    contents: |
      {
        "name": "{{ project_name }}",
        "version": "0.1.0",
        "private": true,
        "type": "module",
        "scripts": {
          "dev": "vite",
          "build": "vite build",
          "preview": "vite preview"
        },
        "dependencies": {
          "react": "^18.3.1",
          "react-dom": "^18.3.1"
        },
        "devDependencies": {
          "@vitejs/plugin-react": "^4.3.1",
          "vite": "^5.4.0",
          "tailwindcss": "^3.4.10",
          "autoprefixer": "^10.4.20",
          "postcss": "^8.4.41"
        }
      }

  - path: "{{ project_name }}/index.html"
    type: source
    contents: |
      <!doctype html>
      <html lang="pl">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <title>{{ app_title }}</title>
        </head>
        <body>
          <div id="root"></div>
          <script type="module" src="/src/main.jsx"></script>
        </body>
      </html>

  - path: "{{ project_name }}/vite.config.js"
    type: config
    contents: |
      import { defineConfig } from "vite";
      import react from "@vitejs/plugin-react";

      export default defineConfig({ plugins: [react()] });

  - path: "{{ project_name }}/tailwind.config.js"
    type: config
    contents: |
      export default {
        content: ["./index.html", "./src/**/*.{js,jsx}"],
        theme: { extend: {} },
        plugins: [],
      };

  - path: "{{ project_name }}/postcss.config.js"
    type: config
    contents: |
      export default { plugins: { tailwindcss: {}, autoprefixer: {} } };

  - path: "{{ project_name }}/src/index.css"
    type: source
    contents: |
      @tailwind base;
      @tailwind components;
      @tailwind utilities;

  - path: "{{ project_name }}/src/main.jsx"
    type: source
    contents: |
      import React from "react";
      import ReactDOM from "react-dom/client";
      import App from "./App.jsx";
      import "./index.css";

      ReactDOM.createRoot(document.getElementById("root")).render(
        <React.StrictMode>
          <App />
        </React.StrictMode>
      );

  - path: "{{ project_name }}/src/App.jsx"
    type: source
    contents: |
      export default function App() {
        return (
          <main className="min-h-screen flex items-center justify-center bg-slate-900 text-white">
            <h1 className="text-3xl font-bold">{{ app_title }}</h1>
          </main>
        );
      }

  - path: "{{ project_name }}/.gitignore"
    type: config
    contents: |
      node_modules/
      dist/
      .env
```

## Jak wygenerować

1. Renderuj zmienne, utwórz strukturę z manifestu.
2. `npm install && npm run dev`.
