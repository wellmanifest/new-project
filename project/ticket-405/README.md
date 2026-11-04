# Ticket 405: Release verified current owner after published checkout removal

- **ID**: ticket-405
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-11-04

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: continue the user's authorized repairs,
tests, merge and bump. NP-026 / issue572 repairs the actual terminal-owner
failure exposed after independently merged source403 lost its checkout/ref.
The allocator's nonfrozen head is its accepted base, not the later published
source. Preserve the exact owner/session, fencing, CAS and verified merged
receipt. An absent publication ref may use the accepted-base ancestry only
when both the canonical checkout and its registration are absent. This
releases that explicit owner's reservation only; it grants no writer,
takeover, cleanup, approval or restoration authority.

Join patch0.20.135 and its producer projections to this material fix. The
new immutable release will also include source403's already approved history
repair. Existing v0.20.134 is immutable and will not be retargeted. Consumer
adoption and preserved legacy data remain separate stages.

## Acceptance criteria

- [x] AC-01: Actual Git removal of the merged checkout/ref reproduces the old refusal; explicit current-owner plan/apply/idempotent retry succeed after the repair without changing Git or creating a writer grant.
- [x] AC-02: Wrong owner/CAS/receipt/base, remaining registration/path/symlink, frozen-head mismatch and Git failures remain refused; existing interruption and filesystem safeguards pass.
- [ ] AC-03: All required source checks, full Goal pytest, exact-head protected CI and independent Validator publication pass; publish immutable v0.20.135 before consumer adoption.

## Risks and boundaries

The terminal registry is verified against real target ancestry, not treated
as merge approval. Existing independently protected publication remains the
approval boundary. Preserve a remaining checkout, registration or source
ref; never infer takeover from timeout. Scope seven implementation files:
controller, regressions, version/package/manifest projections and the existing
upgrade reference. No runtime dependency or public request-schema change.

## Validation

The actual-Git regression suite reproduced four `terminal_head_mismatch`
errors on the original controller. After the repair, all22 controller tests
pass, including nine new test methods and the existing interrupted-write,
foreign-owner and filesystem safeguards. Required complete qualification and
independent publication remain external stages; these local results grant
no trusted approval or cleanup authority.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-405/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 68/100 |
| Complexity | L |
| Estimated effort | 76 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->
