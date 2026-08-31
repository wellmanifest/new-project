# Ticket 160: Resolve ticket content from terminal activity

- **ID**: ticket-160
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-30

## Cel i Zakres

Make ticket scaffold validation consume the same resolver-derived active set
as workstream, dependency and change-scope validation. A verified terminal
receipt must release both the reservation and active-only content requirements
without rewriting the historical Markdown carrier.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: A raw `IN_PROGRESS` ticket with a verified terminal receipt is
      not required to satisfy active-only ticket scaffold fields.
- [ ] AC-02: A genuinely active ticket with a missing required file still
      emits `GOV-TICKET-003`.
- [ ] AC-03: The complete deterministic standard suite passes and the fix is
      published as immutable version 0.19.14.

## Ryzyka i Uwagi
- Risk: skipping validation from raw status alone could hide a live ticket.
  Mitigation: only the existing fail-closed resolver can remove a ticket from
  the active set; missing or invalid receipts remain active.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-160/`.
