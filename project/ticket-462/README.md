# Ticket 462: Share registry validation and commit-graph ancestry across tickets in one activity batch

- **ID**: ticket-462
- **Owner**: agent:claude-opus-5-5
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-11-19

## Cel i Zakres

`wellman check` in paxlet-com/heyasa failed with GOV-WORKTREE-CHECK-002
because `.governance/worktree_overlap_check.py` exceeded its 480 s budget
(676 s measured on 2026-11-19, planfile PLF-28742). A profile of the same
checker on heyasa (61 checkouts, 8 pending, ~690 tickets, ~730 terminal
receipts) attributed 297 s of 323 s to `ticket_scopes`, not to pair
comparisons (12 s):

- `resolve` re-parsed and re-validated the whole receipt registry for every
  ticket: 5 522 validations, 4.0 M receipt checks, ~70 s.
- every receipt asked `git merge-base --is-ancestor` twice with a distinct
  terminal commit, and the batch exit re-asked each relation: ~22 000
  processes, ~175 s.

Inside one `ActivityReadBatch` only, the registry text is now parsed,
validated and grouped by ticket once. From the second ancestry question about
the same full commit ID (the target branch), its history is read once with
`git rev-list --topo-order --parents`, and every question whose newer commit is
in that history is answered in memory, using topological-order pruning. Exit revalidation
re-reads the same graph once and re-answers every observed relation. Outside a
batch, and for non-SHA operands, behaviour is unchanged.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Batched and standalone resolutions are identical, including an
  unintegrated head and a terminal off the target; registry validation runs
  once per batch (`test_distinct_terminal_receipts_share_one_graph_and_one_registry_validation`;
  40 validations and fails on the previous code).
- [x] AC-02: Graph answers equal `git merge-base --is-ancestor` on every pair
  of a merge/criss-cross history, unknown and unreadable commits included
  (`test_graph_ancestry_matches_merge_base_on_every_commit_pair`); a
  differential run on heyasa (821 pairs, 1 926 commits) found 0 mismatches.
- [x] AC-03: Subprocesses per batch no longer grow with receipts: 283 → 28 for
  40 distinct-terminal receipts. On heyasa under load 39–47 the full checker
  took 77 s against 216 s for the installed version, with an identical passing
  report (status, findings).
- [x] AC-04: All existing invalidation tests (target ref, registry, policy,
  projection, inventory, checkout, worktree registration) still fail closed.

## Ryzyka i Uwagi
- Risk 1: The graph is an in-memory reimplementation of ancestry. Mitigation:
  it is only used for full 40-hex IDs inside a commit graph Git produced, is
  checked differentially against `merge-base`, and falls back to `merge-base`
  in every other case.
- Risk 2: A very large history makes one `rev-list` costlier than a few
  probes. It is built only after a second question about the same commit and
  has a 60 s bound; an unreadable result answers `False` exactly as
  `merge-base` does.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-462/`.

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
