# Standard Nazewnictwa i Notacji Plików Uczestników (LLM / IDE Provider Notation Standards)

[![Purpose: Standard](https://img.shields.io/badge/Purpose-Notation_Standard-blue.svg)](#)
[![Status: Approved](https://img.shields.io/badge/Status-Approved-success.svg)](#)

Dokument określa znormalizowany standard nazewnictwa plików, struktur metadanych oraz logowania dla ludzi i agentów AI w oparciu o identyfikator **LLM / IDE Provider**.

---

## 1. Konwencja Nazewnictwa Plików (File Naming Notation)

Zamiast generycznego szablonu `{NAME}` stosujemy ścisłą konwencję **kebab-case** opartą o identyfikator środowiska wykonawczego **`{PROVIDER}`**:

```text
ai-{PROVIDER}.md           <-- Mózg Agenta AI (Rozumienie intencji, plan, AC)
ai-{PROVIDER}-logs.txt     <-- Dedykowane surowe logi komend CLI i testów
user-{NAME}.md             <-- Notatki człowieka / stały kontekst zapytania
```

### Znormalizowane identyfikatory `{PROVIDER}`:
* `antigravity` (Google Antigravity IDE)
* `cursor` (Cursor IDE)
* `claude` (Claude Code / Anthropic CLI)
* `copilot` (GitHub Copilot)
* `codex` (OpenAI Codex)
* `gemini` (Google Gemini CLI)

---

## 2. Standard Struktury Mózgu Agenta (`ai-{PROVIDER}.md`)

Plik intencji agenta wykorzystuje nagłówek **YAML Frontmatter** oraz **GitHub Flavored Markdown (GFM)**:

```markdown
---
agent_provider: antigravity
model_version: gemini-2.5-pro
ticket_id: ticket-001
timestamp: 2026-07-29T12:23:31Z
status: WAIT_FOR_APPROVAL
---

# Intent Understanding & Execution Specification

## 1. Intention & Business Purpose
[Rozumienie intencji użytkownika i celu biznesowego]

## 2. System Architecture & Scope Boundaries
- **In Scope:** [Zakres prac]
- **Out of Scope:** [Elementy poza zakresem]

## 3. Acceptance Criteria (AC)
- [ ] AC-01: [Kryterium odbioru 1]
- [ ] AC-02: [Kryterium odbioru 2]
```

---

## 3. Standard Surowych Logów Wykonawczych (`ai-{PROVIDER}-logs.txt`)

Rejestracja logów wykonawczych bazuje na znacznika czasu **ISO 8601 (UTC)** oraz strukturze **RFC 5424**:

```text
[2026-08-01T12:23:31Z] [EXEC] [provider:antigravity] $ ./project.sh --actor agent
[2026-08-01T12:23:32Z] [STDOUT] GOV-PASS: passed (0 errors, 0 warnings)
[2026-08-01T12:23:33Z] [EXEC] [provider:antigravity] $ NEW_PROJECT_ANALYSIS_IMAGE=registry.example/analysis@sha256:<64-hex-digest> ./project.sh
[2026-08-01T12:23:35Z] [STDOUT] Analysis completed in the digest-pinned container.
[2026-08-01T12:23:36Z] [EXIT] Command exited with code 0
```

---

## 4. Macierz Ról i Odpowiedzialności Plików

| Plik | Typ | Rola i Odpowiedzialność |
| :--- | :--- | :--- |
| **`user-{NAME}.md`** | Kontekst | Ręczne notatki i instrukcje użytkownika (`user-mateusz.md`). |
| **`ai-{PROVIDER}.md`** | Specyfikacja | Mózg intencji i plan agenta (`ai-antigravity.md`, `ai-cursor.md`). |
| **`ai-{PROVIDER}-logs.txt`** | Logi | Surowe wyjścia terminala danego agenta (`ai-antigravity-logs.txt`). |
| **`preprompt.md`** | Workflow | Wytyczne ekstrakcji z notatek i schemat krokowy. |
| **`changelog.md`** | Rejestr | Granularny rejestr zmian dla danego ticketu. |
