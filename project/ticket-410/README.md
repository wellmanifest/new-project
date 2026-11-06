# Ticket 410: Constrain dirty snapshots and publish accepted handoff receipts

- **ID**: ticket-410
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-11-06

## Cel i Zakres
Repair four current138 defects in dirty cache digest, staged index paths, complete snapshot byte limits and idle-handoff success publication. Keep every ownership/policy/CI/default limit; tests affect synthetic fixtures only. Material139 belongs to this repair. Profiled validation overhead is addressed in the existing fixtures: check the report schema once per process and borrow immutable source Git objects while keeping every fixture index/ref/worktree independent. All test cases and the300-second stage budget remain unchanged.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Exact R/C pathname parsing and source/bundle dirty cache confinement; actual content changes invalidate.
- [x] AC-02: Full snapshot byte bound and recovery prepare state prevent false handoff success after lease/journal I/O failure.
- [x] AC-03: Staged regular index files survive unstaged links/missing paths; unsafe syntax/staged links remain refused in source/bundle.
- [ ] AC-04: Native gate/full tests/default300 canonical/realCI/independentApp precede immutable139.

## Ryzyka i Uwagi
- Recoverable ignored prepared records are proposals only; no production takeover or owner transfer is executed in this task. Existing success records, caps and gates stay compatible.
- Concrete13material files/3components/S25, no runtime dependency. Initial allocator radar without final AC is advisory.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-410/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 68/100 |
| Complexity | L |
| Estimated effort | 92 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->
