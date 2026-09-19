# Ticket 254: Recover pre-adoption ticket identity with fenced allocator validation

- **ID**: ticket-254
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-09-19

## Cel i Zakres
Recover an existing pre-adoption ticket through the managed allocator, preserving
its branch and material work while requiring current controller ownership,
exact HEAD/dirty state, canonical layout, unused identity and bounded scope.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Recovery succeeds only for a matching fenced owner; invalid HEAD,
  scope, layout, identity, lease or peer admission is rejected without ticket writes.
- [ ] AC-02: Normal allocator tests and managed governance pass; package and
  release projections ship together through protected publication.

## Ryzyka i Uwagi
- Recovery must not convert local observations into merge approval or takeover
  authority. Keep controller locking through the bounded effect and reject
  stale or unknown evidence. Preserve the original checkout on failure.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-254/`.
