# Ticket 352: work_start_check: unreadable quarantined intents do not block allocation (#496)

- **ID**: ticket-352
- **Owner**: agent:claude
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-10-19

## Cel i Zakres

Naprawa wellmanifest/new-project#496. W subactor/core każda alokacja kończyła
się ogólnym `GOV-WORK-START-001`, bo worktree w kwarantannie
(`.worktrees/.quarantine/PLF-15569-…`) utknął w przerwanym merge'u, a jego
`project/ticket-362/intent.json` zawiera znaczniki konfliktu.

`scripts/work_start_check.py` zapisuje taki checkout jako
`QUARANTINED_UNREADABLE` (nieaktywny, bez deklarowanych ścieżek) zamiast
przerywać całą obserwację. Jego delta Git nadal jest porównywana jako praca
oczekująca, więc rzeczywiste nakładające się zmiany dalej blokują. Nieczytelny
intent poza `.quarantine` nadal zatrzymuje alokację (fail closed). Wersja
standardu 0.20.105.

Najpierw zlecone willman (`koru.develop_ticket`, zai/glm-5.3): przebieg zwrócił
NO-PATCH, bo 45 KB skrypt był ucięty w kontekście modelu, więc zmianę wykonano
tutaj według tej samej specyfikacji.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `test_unreadable_quarantined_intent_does_not_block_disjoint_work`
  nie przechodzi na poprzedniej wersji skryptu i przechodzi teraz.
- [x] AC-02: `test_unreadable_intent_outside_quarantine_still_fails_closed` i
  istniejące testy nieprawidłowego intentu przechodzą.

## Ryzyka i Uwagi
- Checkout w kwarantannie nie rezerwuje już zakresu przez swój intent; ochronę
  daje porównanie jego delty Git (`pending-delta`).

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-352/`.
