# Ticket 177: Align complex delivery documentation with runtime

- **ID**: ticket-177
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-01

## Cel i Zakres

Usunąć dwie sprzeczności pozostawione po scaleniu ticketu 149: dokumentacja
nie może przedstawiać planowanej merge queue jako aktywnego runtime ani
przypisywać chronionemu kontrolerowi fizycznego usuwania lokalnego worktree.
Opis ma odpowiadać działającemu `direct-pr`, terminalnemu resolverowi ticketu i
lokalnemu workspace lifecycle.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: aktywna integracja jest opisana jako serializacja na chronionym
      `main`, a merge queue pozostaje wyraźnie przyszłą warstwą runtime.
- [x] AC-02: terminalny receipt zwalnia rezerwację ticketu, natomiast lokalny
      worktree usuwa osobny operator dopiero po audycie dirty/process/HEAD.
- [x] AC-03: dokumentacja, governance i pełna suita pozostają zielone na
      exact-head PR.

## Ryzyka i Uwagi

- Korekta nie zmienia zachowania runtime ani formatu receiptu; usuwa wyłącznie
  obietnice niepoparte bieżącą implementacją.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-177/`.
