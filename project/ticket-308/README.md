# Ticket 308: Bind continuity transaction locks to verified directory handles

- **ID**: ticket-308
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-10-04

## Cel i Zakres
SESSION_EXECUTION_AUTHORIZATION: the user requested continued testing, repair
and protected merges. Repair the confirmed ancestor-substitution locking race
at its standard owner, tracked by C2004 PLF-2961 / issue #451. Preserve unrelated
work, protected review and immutable consumer adoption.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Adversarial lock fixtures and existing continuity storage tests pass.
- [x] AC-02: Native governance and package checks pass; platform verification is
  reported separately and is not inferred from Linux results.
- [ ] AC-03: Independent exact-head verification, protected merge and immutable
  release precede official DisplayNet adoption.

## Ryzyka i Uwagi
- Linux tests cannot replace the required independent Windows matrix. Local
  allocation and checkpoint receipts grant no review or publication authority.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-308/`.
