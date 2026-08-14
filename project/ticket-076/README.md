# Ticket 076: Authorize protected Validator delivery without redundant prompts

- **ID**: ticket-076
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PLAN
- **Utworzono**: 2026-08-14

## Cel i Zakres

Usunąć zbędne pytania o zgodę podczas publikacji już autoryzowanego,
ograniczonego ticketu. Standard ma rozdzielić autoryzację uruchomienia
chronionego procesu dostawy od wytwarzanego przez ten proces zaufanego dowodu
approval. `SESSION_EXECUTION_AUTHORIZATION` pozwala przekazać pracę do
zadeklarowanego Validatora i pozwolić temu procesowi wykonać merge po wszystkich
bramkach; nie jest natomiast samo w sobie approval ani dowodem merge.

## Kryteria Odbioru (Acceptance Criteria)

- [ ] AC-01: Policy i ticket-lifecycle odróżniają process invocation authority
      od exact-head trusted merge evidence.
- [ ] AC-02: Agent pyta ponownie tylko o destrukcję, sekrety, nową koordynację
      zewnętrzną lub materialne rozszerzenie celu, a nie o sam chroniony merge.
- [ ] AC-03: Wszystkie generowane instrukcje i fallbacki `new-ticket.sh`
      przekazują tę samą semantykę bez starszego, sprzecznego sformułowania.
- [ ] AC-04: Testy regresyjne wykrywają ponowne dodanie redundantnego promptu,
      zachowując wymaganie niezależnego exact-head approval.
- [ ] AC-05: Pełny kontrakt governance oraz testy szablonów przechodzą.

## Ryzyka i Uwagi

- Autoryzacja sesji nie może stać się samopotwierdzeniem autora. Mitygacja:
  merge nadal wymaga zewnętrznego, chronionego i związanego z HEAD dowodu.
- Niechroniony merge lub bezpośredni bypass pozostają niedozwolone. Standard
  zezwala wyłącznie na zadeklarowany proces, który ponownie weryfikuje bramki.
- Równoległe, niezacommitowane zmiany w głównym worktree są cudzą pracą i nie
  wchodzą do tego ticketu.

## Autoryzacja

Polecenie użytkownika „wykonaj potrzebne zmiany w wellmanifest i subactor”
stanowi `SESSION_EXECUTION_AUTHORIZATION` dla tego ograniczonego zakresu,
łącznie z publikacją przez chroniony Validator. Nie stanowi trusted approval;
ten dowód musi wytworzyć niezależny proces dla dokładnego HEAD.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-076/`.
