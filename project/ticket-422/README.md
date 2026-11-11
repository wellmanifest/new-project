# Ticket 422: Deduplicate per-checkout git status and disjoint merge-tree probes in worktree_overlap_check

- **ID**: ticket-422
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-11-11

## Cel i Zakres
Usunięcie nadmiarowych wywołań `git status` (z 3 do 1 na badany checkout) w `inspect_checkout` / `changed_paths` oraz pominięcie kosztownych wywołań `git merge-tree` O(N^2) w `contested_paths`, gdy dwie gałęzie dzielą wspólny punkt odniesienia `origin/<default>` i nie mają wspólnych zmienionych ścieżek (`shared_default and not (first_changes & second_changes)`).

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `inspect_checkout` wykonuje pojedynczy odczyt `git status --porcelain=v1 -z --untracked-files=all` przez `unignored_dirty_paths` i przekazuje przefiltrowaną krotkę do `changed_paths(..., dirty=filtered_dirty)`.
- [x] AC-02: `contested_paths` pomija `merge_tree_conflicts` dla rozłącznych par ze wspólnym `shared_default`, zachowując pełne wykrywanie konfliktów dla par z nakładającymi się zmianami lub renamami.
- [x] AC-03: Pełny zestaw testów `tests/worktree-overlap.test.sh` oraz bramki governance przechodzą bez regresji.

## Ryzyka i Uwagi
- Risk 1: Konflikty rename/directory-rename przy rozłącznych nazwach docelowych — mitygacja: `changes_against_shared_default` ustawia `shared_default = True` wyłącznie wtedy, gdy po obu stronach brak operacji rename (`not first_renames and not second_renames`).

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-422/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 52/100 |
| Complexity | M |
| Estimated effort | 51 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->
