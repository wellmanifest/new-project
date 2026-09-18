# Ticket 235: Ticket index merge driver and worktree pruning standard

- **ID**: ticket-235
- **Owner**: antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-18

## Cel i Zakres
1. Zapewnienie automatycznego rozwiązywania konfliktów w `project/TICKETS.md` i `TODO.md` za pomocą dedykowanego merge drivera Git (`wellmanifest-ticket-index`), eliminując paraliż równoległych PR-ów.
2. Narzędzie `scripts/prune_merged_worktrees.py` do bezpiecznego audytu i czyszczenia linked worktrees po scaleniu gałęzi z zachowaniem zasady `Prymat Niezapisanego Kodu` (blokada usuwania brudnych worktree).
3. Izolacja sprawdzania cyklu życia gałęzi w GitHub Actions PR za pomocą opcji `--focus-branch` w `scripts/branch_lifecycle_check.py`, zapobiegająca blokowaniu aktywnego PR przez obce osierocone gałęzie.
4. Integracja merge drivera w `scripts/install-agent-hosts.sh` i pakiecie `governance/package-manifest.json`.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `scripts/ticket_index_merge_driver.py` deduplikuje i sortuje sekcję indeksu numerycznie oraz przechodzi testy jednostkowe.
- [x] AC-02: `scripts/prune_merged_worktrees.py` bezpiecznie usuwa zmergowane worktree i nie usuwa unmerged / dirty.
- [x] AC-03: `scripts/branch_lifecycle_check.py` z flagą `--focus-branch` sprawdza wyłącznie cel danego PR.

## Ryzyka i Uwagi
- Brak zależności od pakietów zewnętrznych (brak `urllib`, `requests`, `subprocess` w testowanych skryptach audytowych zgodnie z kontraktem sandboxa).
