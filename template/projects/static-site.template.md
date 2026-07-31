# Wzorzec Projektowy: Statyczna strona (`static-site`)

Manifest jednoplikowy opisujący prostą statyczną stronę HTML/CSS/JS bez build-stepu.

## Zmienne wejściowe

| Zmienna | Opis | Przykład |
| :--- | :--- | :--- |
| `project_name` | Nazwa projektu | `landing` |
| `site_title` | Tytuł strony | `Moja Strona` |

## Manifest

```yaml
variables:
  project_name: landing
  site_title: Moja Strona

directories:
  - "{{ project_name }}"
  - "{{ project_name }}/css"
  - "{{ project_name }}/js"

files:
  - path: "{{ project_name }}/index.html"
    type: source
    contents: |
      <!doctype html>
      <html lang="pl">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <title>{{ site_title }}</title>
          <link rel="stylesheet" href="css/style.css" />
        </head>
        <body>
          <main>
            <h1>{{ site_title }}</h1>
            <p>Strona wygenerowana z manifestu jednoplikowego.</p>
          </main>
          <script src="js/main.js"></script>
        </body>
      </html>

  - path: "{{ project_name }}/css/style.css"
    type: source
    contents: |
      :root { color-scheme: dark; }
      body {
        font-family: system-ui, sans-serif;
        margin: 0;
        min-height: 100vh;
        display: grid;
        place-items: center;
        background: #0f172a;
        color: #f8fafc;
      }

  - path: "{{ project_name }}/js/main.js"
    type: source
    contents: |
      console.log("{{ site_title }} loaded");

  - path: "{{ project_name }}/README.md"
    type: docs
    contents: |
      # {{ project_name }}

      Statyczna strona wygenerowana z manifestu jednoplikowego.
```

## Jak wygenerować

1. Renderuj zmienne, utwórz strukturę z manifestu.
2. Otwórz `index.html` lub serwuj przez dowolny statyczny serwer.
