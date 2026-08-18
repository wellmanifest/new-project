# Ticket 090: Host-agnostic LLM standard: GEMINI.md, Cursor rules, fail-closed hook

- **ID**: ticket-090
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-18

## Cel i Zakres

Gemini, Antigravity, Claude i Cursor omijają `AGENTS.md`, gdy startują poza
Cursor. Standard ma być ten sam niezależnie od hosta: pliki instrukcji, które
dany host czyta sam, plus hook git, który odrzuca commit bez ticketu
`IN_PROGRESS`. Instalator kopiuje ten sam zestaw do innych clone'ów i do
katalogów użytkownika.

`--force-new` jest zapisane. ticket-089 (PR #140) jest leftover na `main` i
zostaje zamknięty tutaj, żeby workstream `governance` miał jednego właściciela.
Ten ticket nie edytuje `package-manifest.json` ani `governance_check.py`.

HOME `wellmanifest`, shape `domain_pack`.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: `./tests/agent-hosts.test.sh` — hook odrzuca commit bez ticketu; instalator materializuje pliki.
- [ ] AC-02: `./project/governance-check.sh --actor agent` przechodzi.

## Ryzyka i Uwagi
- Risk 1: ticket-089 nadal rezerwuje workstream governance. Mitigacja: `--force-new` na żądanie człowieka; brak nakładających się `allowedPaths`.
- Risk 2: adopcja managed files czeka na zamknięcie 089. Mitigacja: `install-agent-hosts.sh --target` działa od razu.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-grok.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-090/`.
