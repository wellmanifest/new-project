# Ticket 376: Idle takeover slice 3/3: work-start board refresh and agent worktree rules

- **ID**: ticket-376
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-10-23

## Cel i Zakres
Wycinek 3 z 3 mechanizmu przejmowania po bezczynności (ticket-374 PR #533,
ticket-375 PR #535 scalone). `work_start_check.py` przy każdym uruchomieniu
odświeża tablicę autonomii `.subactor/cache/autonomy-board.md` i wypisuje na
stderr kandydatów do przejęcia, nie zmieniając trasy. AGENTS (reguła 10b hubu i
szablon adoptera) każe każdemu agentowi czytać tablicę, przejmować tylko przez
`idle_takeover.py takeover` przy `IDLE_TAKEOVER_ELIGIBLE` i brać ścieżki
worktree, lease oraz środowisko pisarza wyłącznie z wyniku JSON, w kanonicznym
`<primaryCheckout>/.worktrees/<ticket>--<slug>` (wellmanifest/worktrees v5).
Runbooki GOV-WORK-START, GOV-ARCHITECTURE-001 i STANDARD_UPGRADE opisują ten
jedyny mierzony wyjątek od zaakceptowanego przekazania.

SESSION_EXECUTION_AUTHORIZATION: user request 2026-10-23 („kontynuuj, scalaj, testuj”).

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `tests/idle_takeover_test.py` (25 testów, w tym odświeżenie tablicy przez work-start), agent-hosts, rule-enforcement, governance-validator przechodzą.
- [ ] AC-02: governance-check i niezależna walidacja PR.

## Ryzyka i Uwagi
- Odświeżenie tablicy jest best-effort: błąd obserwacji nie zmienia trasy work-start.
- Adoptery dostaną mechanizm dopiero przy aktualizacji standardu.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-376/`.
