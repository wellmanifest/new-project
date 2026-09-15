# Ticket 233: Surface stale carriers and selected-checkout writes in work admission; discover host contract from registered checkouts

- **ID**: ticket-233
- **Owner**: claude-work-admission
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-15

## Cel i Zakres

Trzy defekty zaobserwowane 2026-09-15 podczas równoległej pracy agentów:

1. Brudna kopia carriera już scalonego ticketu (ticket-232, PR #359) w
   głównym checkoutcie zajmowała jedyny slot WIP. `work_start_check` zwracał
   `SERIALIZE` bez żadnego blokera, więc nie było wiadomo, co uzgodnić.
   Domyślna polityka `status-projection` pozostaje bez zmian (PR #322); kopia
   staje się jawnym blokerem `integrated-ticket-carrier` z trasą `RECONCILE`.
2. Przy `REUSE_EXISTING` wybrany checkout był pomijany: świeże, niezacommitowane
   zmiany innego agenta w tym samym worktree nie dawały sygnału. Raport pokazuje
   najnowszy czas modyfikacji brudnych ścieżek i ich nakładanie z zakresem, a
   opcjonalne `--expect-dirty-digest` blokuje po zmianie od ostatniej obserwacji.
3. Użytkowy wskaźnik kontraktu hosta działał tylko, gdy bieżący checkout ma
   `project/new-ticket.sh`; główny checkout z nieadoptowanym jeszcze `main` go
   nie ma, choć zarejestrowany worktree ticketu go ma. Wskaźnik obejmuje teraz
   zarejestrowane checkouty i leasy, a instalator aktualizuje starszy akapit.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Brudny carrier ticketu obecnego na obserwowanym targecie, bez
  nieintegrowanej gałęzi, daje bloker `integrated-ticket-carrier` i trasę
  `RECONCILE`; aktywność i domyślna polityka pozostają bez zmian.
- [x] AC-02: Raport zawiera `dirtyNewestModifiedAt`; nakładanie z brudnym
  wybranym checkoutem dodaje wymaganie przed zapisem, a niezgodne
  `--expect-dirty-digest` daje bloker `selected-checkout-changed`.
- [x] AC-03: `install-agent-hosts.sh --user` instaluje wskaźnik obejmujący
  zarejestrowane checkouty i leasy oraz idempotentnie zastępuje starszy akapit.

## Ryzyka i Uwagi

- Czas modyfikacji jest obserwacją, nie tożsamością piszącego; nie przyznaje
  ani nie odbiera autorytetu. CAS digestu jest opt-in, więc istniejące wywołania
  kontynuacji zachowują trasę.
- Snapshot zachowanych carrierów głównego checkoutu przed synchronizacją:
  `sha256:3a0746049f9e97671d0ad755ce5e4473e7e0c773a2ee9c49e4f488d51c2781b8`
  (lokalny receipt `primary-sync-20260915T0620Z`).

SESSION_EXECUTION_AUTHORIZATION: the user requested fixing the observed
concurrent-work standard defects, pushing, testing and merging after their own
trusted GitHub review; the user authorized preserving and synchronizing the
primary checkout. No self-approval or direct merge.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-233/`.
