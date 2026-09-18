# Ticket 236: Autonomous merge, cdp fallback, and worktree pruning standard update

- **ID**: ticket-236
- **Owner**: antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-18

## Cel i Zakres
1. Zsynchronizowanie kanonicznego szablonu `template/files/AGENTS.template.md` oraz `AGENTS.md` ze standardem autonomous merge (`wellmanifest/merge@ticket-008`).
2. Dodanie do instrukcji agenta klauzul dotyczących:
   - Prymat Zielonych Testów i autonomiczne scalanie PR po przejściu testów.
   - Odporność na limity API GitHub (Browser CDP Fallback na porcie 9222).
   - Rebuild Pipeline dla PR z konfliktami po scaleniu innych gałęzi.
   - Obowiązkowe czyszczenie i usuwanie zmergowanych worktree (`prune_merged_worktrees`).
   - Link do standardu `wellmanifest/merge` w sekcji Managed standard sources.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `template/files/AGENTS.template.md` zawiera link do `wellmanifest/merge` i pełną sekcję `<!-- wellmanifest:autonomous-merge:start -->`.
- [x] AC-02: `AGENTS.md` w repozytorium hub zawiera zsynchronizowaną, kompletną sekcję standardu.
- [x] AC-03: Wszystkie testy `agent-hosts.test.sh`, `governance_check.py` oraz `adoption-lock.test.sh` przechodzą pomyślnie.

## Ryzyka i Uwagi
- Brak niekompatybilnych zmian w innych szablonach. Zgodność z istniejącymi asercjami w testach.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-236/`.
