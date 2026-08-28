# Ticket 135: Ignore integrated authorization snapshots on clean main

- **ID**: ticket-135
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-28

## Cel i Zakres

Prevent a clean, integrated default branch from treating tracked
`IN_PROGRESS` authorization snapshots as concurrent live writers. Coordination
must evaluate only tickets selected by the current change; the ordinary change
gate remains responsible for rejecting an implementation delta without one
unambiguous active ticket.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: A clean default-branch snapshot with multiple integrated
  `IN_PROGRESS` ticket records passes workstream coordination.
- [x] AC-02: A real change claimed by multiple active tickets still fails with
  `GOV-WORKSTREAM-002` and `GOV-WORKSTREAM-004` as applicable.
- [x] AC-03: A real implementation change without an active owning ticket
  remains rejected by the change gate.
- [ ] AC-04: The full Linux and Windows governance contracts pass.

## Ryzyka i Uwagi

- The filter is derived only from the current diff. It does not mark tracked
  ticket prose terminal and does not trust an unverified local receipt.
- Material changes remain fail-closed in `check_change_gate`; this correction
  removes a false coordination lease only when no work is being proposed.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-135/`.
