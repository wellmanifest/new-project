# Ticket 469: Recover a mixed first bootstrap ticket

- **ID**: ticket-469
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-11-21

## Goal and scope

Planfile NP-059 and Wellmanifest issue #656 track an integration ticket that
committed both the published first bootstrap and new product files. Its
reservation overlaps the governance work needed to publish the bootstrap.
Recover the scope with its current live writer and keep independent review.

## Acceptance criteria

- [ ] AC-01: Rebind only the existing, live first-bootstrap reservation after
  verifying the original Git bundle, exact staged product removals and
  unchanged adopted files. Refuse stale and incomplete observations.
- [ ] AC-02: Preserve the original commit and owner, advance the fence and
  allow the governance commit and subsequent product ticket to use their
  normal independent review.

## Operation

Save a self-contained external Git bundle of the original ticket head and
target base. Stage only the product paths added by the original ticket.
Use `git rm -- <paths>` in the owned checkout. Supply an external
`new-project.bootstrap-adoption-split/v1` request with the ticket and
request ID, base and head SHAs, product paths, current lease revision and
fencing token, SHA-256 digests of the lease, committed intent and original
bootstrap receipt, and the external bundle path and SHA-256 digest.

Run `bootstrap_adoption_split.py --root <ticket-worktree> --request <file>
--actor <owner> --session <session>` from the reviewed standard. With the same
inputs and `--apply`, the command writes the fenced scope and returns the
writer environment for the next commit. Stage the revised intent and update
the ticket's acceptance criteria for the governance slice. Commit on the
existing branch, run the native gate and request independent publication.
After it lands, allocate the product ticket on the new target base and
restore the exact product paths from the preserved original commit or bundle.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-469/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 64/100 |
| Complexity | L |
| Estimated effort | 67 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->
