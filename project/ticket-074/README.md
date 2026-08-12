# Ticket 074: Align repository and delivery profiles

- **ID**: ticket-074
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-12

## Cel i Zakres

Uzgodnić normatywną politykę, domyślny manifest i deterministyczny walidator:
nowy system deklaruje osobne repozytorium albo komponent monorepo, Docker
pozostaje opt-in, a budżet jest wybierany z jawnych profili XS/S/M/L. Poprawić
projekcję workflow, która traktuje status ticketu `IN_PROGRESS` jak stan.

Polecenie kontynuacji zapisuje `SESSION_EXECUTION_AUTHORIZATION` dla ścieżek z
`intent.json`. Nie jest trusted merge approval.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Zakres jest zatwierdzony bieżącym poleceniem użytkownika.
- [x] AC-02: Nowe manifesty deklarują `standalone` lub `monorepo`; starsze v2
  zachowują deterministyczną kompatybilność `standalone`.
- [x] AC-03: Docker jest wymagany dokładnie dla `docker.required=true`, a
  istniejąca konfiguracja Docker nadal podlega walidacji.
- [x] AC-04: Profile XS/S/M/L są zamknięte, kompletne i egzekwowane dla
  wybranej złożoności ticketu.
- [x] AC-05: Przejścia workflow używają wyłącznie zadeklarowanych stanów.
- [x] AC-06: Metaschema, regresje i pełny kontrakt Linux przechodzą.

## Ryzyka i Uwagi

- Starsze manifesty nie mają nowych pól; walidator zachowuje jawny legacy
  fallback zamiast wymuszać niekontrolowaną migrację.
- Profil L nie może omijać review, timeboxu ani rozbijania niezależnych celów.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-074/`.
