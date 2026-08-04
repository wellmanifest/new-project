---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-003
---
# Participant: codex (AI agent)

## Understanding

Użytkownik zezwolił na zmianę polityki i strategii PR oraz chce, aby agent
Validator mógł bezpiecznie zatwierdzać PR. Obecny standard dopuszcza wyłącznie
review użytkownika z `trusted-reviewers`, a sam walidator dostaje tylko nazwę
źródła i ticket. Wymagane jest rozszerzenie kontraktu bez przyznania zaufania
dowolnym kontom typu `Bot`.

## Execution plan

1. Zdefiniować w DSL trzy rozłączne authority: chroniony human review,
   allowlistowany Validator GitHub App review i zweryfikowaną signed
   attestation.
2. Dodać wersjonowany, maszynowy kontrakt approval evidence przypięty do
   repozytorium, PR, HEAD, ticketu i wystawcy.
3. Rozszerzyć manifest oraz reusable workflow o osobną konfigurację Validator
   Apps, z pustą listą domyślną i bez interpolacji wejść w kodzie JavaScript.
4. Rozszerzyć deterministyczny walidator o weryfikację kompletności i
   świeżości evidence oraz stabilne diagnostyki.
5. Włączyć nowy kontrakt do generatora adopcji i instrukcji agentów.
6. Udokumentować minimalne uprawnienia aplikacji, ochronę CODEOWNERS/ruleset,
   tryb `validate-pr` oraz konfigurację modelu GLM 5.2.
7. Dodać regresje pozytywne i negatywne, uruchomić pełne testy governance i
   sprawdzić diff.

## Actual changes

- Użytkownik zatwierdził ticket 003; rozpoczęto implementację w stanie `EDIT`.
- Zatwierdzenie z czatu autoryzuje tę sesję, ale nie jest zaufanym merge
  approval.
- Dodano `new-project.approval-evidence/v1` wiążący approval z repozytorium,
  PR, HEAD, ticketem i aktorem.
- Manifest rozróżnia `github-review`, `github-app-review` i
  `signed-attestation`; generator adopcji zarządza nowym schematem.
- Reusable workflow rozdziela `trusted-reviewers` i
  `trusted-validator-apps`, testuje dokładny HEAD i tworzy evidence poza
  checkoutem.
- Walidator otrzymał diagnostyki `GOV-APPROVAL-003..005`, weryfikację bindingów
  i authority oraz bezpieczny resolver ticketu dla równoległych workstreamów.
- DSL, AGENTS, README, changelog i dokumentacja egzekwowania opisują nową
  strategię, migrację `validator-agent`/`todo2code` i model GLM 5.2.

## Acceptance evidence

- `bash tests/governance-validator.test.sh`: PASS.
- `bash tests/governance-scripts.test.sh`: PASS.
- `bash tests/adoption-lock.test.sh`: PASS.
- Python compile, JSON Schema Draft 2020-12 i YAML parse: PASS.
- `git diff --check`: PASS.

## Blockers

- Brak blockerów w zakresie ticketu 003.
- Pozostała operacja zewnętrzna: instalacja Validator GitHub App i wdrożenie
  standardu w `subactor/validator-agent` oraz `semcod/todo2code` wymagają ich
  własnych zatwierdzonych ticketów. Wcześniejsze zapytanie instalacyjne zwróciło
  HTTP 401 z powodu błędnego JWT.
