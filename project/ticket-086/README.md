# Ticket 086: GOV-INTENT runbook and post-merge derive rules

- **ID**: ticket-086
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-15

## Cel i Zakres

Dodać kanoniczny runbook `error/GOV-INTENT.md` dla rodziny `GOV-INTENT-001`–
`GOV-INTENT-003` oraz dwie normatywne reguły huba:

1. Zdrowie repozytorium ocenia się na zintegrowanym `main` po merge; zielony
   przebieg na gałęzi PR nie jest sygnałem zdrowia kombinacji.
2. Zbiory, które muszą pozostać spójne, nie są duplikowane ręcznie — jeden jest
   źródłem, drugi jest z niego wyprowadzany.

Zakres nie obejmuje publikacji na `main` (branch protection wymaga PR, a
założyciel zabronił otwierania nowych PR), merge ticketu 077 ani zmiany
semantyki istniejących kodów `GOV-INTENT-*`.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: `error/GOV-INTENT.md` ma wymagane sekcje runbooka, a katalog
      diagnostyczny wskazuje go dla `GOV-INTENT-001`–`003`.
- [ ] AC-02: `POLICY.md` i `CONTRIBUTING.md` zawierają regułę post-merge
      inspekcji `main` oraz zakaz wnioskowania zdrowia z samego zielonego PR.
- [ ] AC-03: `POLICY.md` i `CONTRIBUTING.md` zawierają regułę wyprowadzania
      spójnych zbiorów z jednego źródła zamiast ręcznej duplikacji.
- [ ] AC-04: `audit_diagnostics` pozostaje kompletny (0 findings), mapowanie
      rule-enforcement jest kompletne, a hub gate w trybie zakresowym przechodzi.

## Ryzyka i Uwagi
- `origin/main` nadal ma ticket-085 jako `IN_PROGRESS`; ten ticket stoi na
  governance-only closure 085 (`2e1c679`), ale `acceptedBaseSha` pozostaje
  SHA `origin/main`, żeby nie fałszować `GOV-BASE-001`.
- Merge na `main` wymaga PR i exact-head approval; ten ticket tylko wypycha
  gałąź roboczą.
- Ticket-077 pozostaje `BLOCKED` (AC-05: no push / no PR).

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-grok.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-086/`.
