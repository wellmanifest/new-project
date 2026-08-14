# Ticket 077: Bind agent reports to workspace identity

- **ID**: ticket-077
- **Owner**: unresolved:human
- **Status**: BLOCKED
- **Workflow state**: BLOCKED
- **Utworzono**: 2026-08-14

## Cel i zakres

Dodać kontrakt raportu agenta (`wellmanifest.agent/report/v1`) i regułę
tożsamości workspace (`pwd` + `git rev-parse --show-toplevel`), żeby koordynator
odrzucał raport z innego repozytorium niż to, w którym agent pisał pliki.
Słownik HOME vs ADOPT pozostaje ten sam; `placement` nie staje się wymagane na
starych ticketach.

Polecenie użytkownika, żeby zaimplementować bramki jakości, stanowi
`SESSION_EXECUTION_AUTHORIZATION`.

## Kryteria odbioru

- [x] AC-01: Zlecenie implementacji bramek jakości jest bounded authorization.
- [x] AC-02: `wellmanifest.agent/report/v1` wymaga `workspaceRoot`, `home`,
  `shape`, `filesTouched`, `ticketId`; brak `workspaceRoot` odrzuca dokument.
- [x] AC-03: `scripts/validate-agent-report.py --self-test` odrzuca drift
  `workspaceRoot`/`gitToplevel`, `runtime_service`+`home=wellmanifest` oraz
  `filesTouched` poza `allowedPaths`.
- [x] AC-04: `AGENTS.md` i szablon targetu nakazują cytować HOME git w raporcie
  i STOP, gdy ścieżka rozjeżdża się z zadaniem.
- [ ] AC-05: Publikacja na `main` pozostaje poza tym ticketem (no push / no PR).

## Ryzyka i uwagi

- Nie ruszać `governance/intent.schema.json` ani nie wymagać `placement` na
  istniejących ticketach (osobna, już trwająca zmiana).
- Nie rozszerzać zamkniętego `wellmanifest/agent` v1.
- Nie kontynuować prac produktowych hostguard / project-ssot / maskfleet.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-grok.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-077/`.

## Stan koordynacji

Ticket został przeniesiony do `BLOCKED`, ponieważ jego zatwierdzony intent
jawnie wyklucza push i pull request, a lokalna implementacja jest już
zapisana w zachowanym commicie. Zgodnie z `P-CORE-017` oczekiwanie na osobną
autoryzację publikacji nie może rezerwować jedynego workstreamu governance.
