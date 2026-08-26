# Ticket 131: Enforce repository effect evidence without governance churn

- **ID**: ticket-131
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-26

## Cel i Zakres

Usunąć metadata-only re-pin commity powodowane przez każdy ruch `main`.
`acceptedBaseSha` pozostaje zaakceptowanym przodkiem, a bramka porównuje
interweniujący diff z komponentami zadeklarowanymi w intencji. Kolizja lub
nieliniowa historia nadal wymaga świeżej akceptacji.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: Niepowiązana zmiana na target branch nie wymaga zmiany
  `acceptedBaseSha` i przechodzi walidację.
- [ ] AC-02: Zmiana nachodząca na komponent ticketu oraz historia nieliniowa
  nadal kończą się stabilnym błędem governance.

## Ryzyka i Uwagi
- Ryzyko: zbyt szerokie wzorce komponentów mogą wymusić ponowną akceptację;
  jest to bezpieczny fail-closed wynik, nie automatyczne dopuszczenie.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-131/`.
