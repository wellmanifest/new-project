# Ticket 224: Correct delivery diagnostics and add preservation-first recovery recipes

- **ID**: ticket-224
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-09-13

## Cel i Zakres
Poprawić zamienione znaczenia kodów branch lifecycle w katalogu diagnostyk
i dostarczyć wspólne, zachowujące pracę recepty odzyskiwania postępu. Zakres
obejmuje komunikaty, istniejący zarządzany runbook, testy i dokumentację.
Nie zmienia warunków merge, exit codes, schematów, danych innych ticketów ani
adopcji standardu w projektach docelowych.

Kanoniczny rezultat: [kontrolowane streamowanie](../../docs/information/controlled-change-streaming.md).
Rejestracja zdalna: [Issue #340](https://github.com/wellmanifest/new-project/issues/340).

## Autoryzacja sesji i uczestnik

Użytkownik zlecił optymalizację wellmanifest na podstawie trudności publikacji
Taskand. Agent `codex` realizuje ten ograniczony zakres i wcześniejsze zlecenie
publikacji przez chroniony proces. Nie jest to trusted merge approval ani
zgoda na usuwanie historycznych branchy lub wyłączanie bramek.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Kody 001/002/003 mają zgodne znaczenie w runtime, katalogu i runbooku; test wykrywa zamianę 002/003.
- [x] AC-02: Recepty rozróżniają obserwację, zachowanie pracy, autoryzowany skutek i weryfikację; zachowane są dotychczasowe odmowy dla niepoprawnych snapshotów.
- [x] AC-03: Dokumentacja oddziela dzisiejszą implementację od propozycji rozdzielenia checkpoint/push, merge, release i deploy, z kolejnością małych adopcji.

## Walidacja

Izolowany obraz `sha256:b856811ab56d71a80744e11e5204809fbdec50de1ba9d4b7d27d2ae98d0a3a0d`:
branch lifecycle, 25 testów reconciliation i rule-enforcement PASS. Na bazie
odtworzono zamianę obu kodów. Jawna kontrola wszystkich staged paths przez
manifest.hub, kontrola dokumentacji i diff-check PASS. Wyniki lokalne nie
stanowią trusted review; merge i adopcja wymagają osobnych dowodów.

## Ryzyka i Uwagi
- Ryzyko: porada mogłaby zostać uznana za authority. Runbook i instrukcje
  jawnie zachowują kontrolę efektów; PASS nie udziela zgody na cleanup.
- Nie dotykamy historycznych gałęzi 069/206, współdzielonego package-manifest
  ani POLICY/CONTRIBUTING. Ich zmiany wymagają osobnej uzgodnionej integracji.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-224/`.
