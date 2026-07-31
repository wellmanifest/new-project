# Szablony Projektowe (`template/projects/`)

Katalog ten jest przeznaczony na wzorce całych projektów, szablonów architektonicznych oraz konfiguracji bazowych wykorzystywanych podczas bootstrapu nowych systemów.

## Przeznaczenie

O ile katalog `template/files/` odpowiada za szablony pojedynczych plików w ticketach, o tyle katalog `template/projects/` mieści kompletne wzorce architektoniczne gotowe do skopiowania przy tworzeniu nowych repozytoriów.

## Format Szablonu (Manifest Jednoplikowy)

Każdy szablon to **jeden plik** `{nazwa_architektury}.template.md` zawierający całą wiedzę o projekcie: strukturę katalogów oraz zawartość plików. Rdzeniem jest osadzony blok `yaml` z trzema sekcjami:

- **`variables`** — parametry wejściowe (np. `project_name`), używane jako kontekst renderowania.
- **`directories`** — lista katalogów do utworzenia (z placeholderami `{{ ... }}`).
- **`files`** — lista plików: `path`, `type` i `contents` (treść wielolinijkowa).

Renderowanie: silnik szablonów (Jinja2/EJS) podstawia zmienne `{{ ... }}`, następnie generator tworzy katalogi i zapisuje pliki. Model zgodny z podejściem manifest + własny generator.

## Indeks Wzorców Projektowych

| Wzorzec Projektowy | Typ Systemu | Opis |
| :--- | :--- | :--- |
| **`python-package.template.md`** | Pakiet Python | Layout `src/`, testy `pytest`, `pyproject.toml`. |
| **`nodejs-service.template.md`** | Usługa Node.js | HTTP API na Express, struktura `src/`. |
| **`react-frontend.template.md`** | Frontend SPA | React + Vite + TailwindCSS. |
| **`fastapi-microservice.template.md`** | Mikroserwis | FastAPI + Docker + testy. |
| **`java-springboot.template.md`** | Backend Java | Spring Boot budowany Mavenem. |
| **`go-cli.template.md`** | Narzędzie CLI | Aplikacja CLI w Go z modułem i testami. |
| **`rust-cli.template.md`** | Narzędzie CLI | Aplikacja CLI w Rust (Cargo). |
| **`docker-compose-stack.template.md`** | Stack | API + baza + reverse proxy (Compose). |
| **`static-site.template.md`** | Strona statyczna | HTML/CSS/JS bez build-stepu. |
| **`monorepo.template.md`** | Monorepo | Workspaces npm (`apps/` + `packages/`). |
