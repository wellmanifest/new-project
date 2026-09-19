# Ticket 256: Restore protected review boundary in managed host guidance

- **ID**: ticket-256
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-09-19

## Cel i Zakres
Remove contradictory review-bypass instructions from the hub and managed
AGENTS template. Preserve the independent protected review boundary, add a
regression guard and publish an immutable correction for Wellman ticket-002.

SESSION_EXECUTION_AUTHORIZATION: the user requested continuing the Wellman
repair and adoption. This bounded source correction resolves the independently
observed Wellman PR #3 finding; it grants no review, policy-bypass or direct
merge authority. Publication uses only the declared protected delivery route.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Hub and managed guidance require independent exact-head approval
  and reject the known review-bypass, forced-cleanup and WIP-waiver instructions.
- [x] AC-02: Host regression tests and the managed gate pass with consistent
  release metadata; no adopter or protected-policy files change in this ticket.

## Ryzyka i Uwagi
- Risk: restoring only one projection would leave adopters vulnerable. Test
  both projections and their identical protected-delivery section.
- Downstream: Wellman PR #3 remains blocked until this correction is published
  and adopted through its immutable standard updater.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-256/`.
