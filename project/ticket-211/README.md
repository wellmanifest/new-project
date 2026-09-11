# Ticket 211: Bound repeated published adoption validation

- **ID**: ticket-211
- **Owner**: agent:openai
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-09-10

## Cel i Zakres
SESSION_EXECUTION_AUTHORIZATION: continue the user-authorized upstream repair,
tests and independent publication. A fresh post-merge canary exposed the
successive-adoption variant after the first fix. Session authorization does not
replace protected exact-head approval.

Resolve the clean-published validation range before counting adoption tickets
when their target branch is unambiguous. A historical merged ticket must not
prevent validation of the latest merged adoption. Preserve terminal receipts
as lifecycle truth; do not rewrite historical ticket status.

## Kryteria Odbioru (Acceptance Criteria)
- AC-01: Two, three and many published same-target adoptions select the latest
  first-parent diff; dirty, unpublished or ambiguous targets remain fail-closed.
- AC-02: Standard tests and protected Linux/Windows checks pass with the atomic
  0.20.22 release projection and independent review.

## Ryzyka i Uwagi
Narrowing the diff for live concurrent adoptions would hide work. Only reuse the
existing exact origin/head, clean-tree and readable-parent observation. Missing
evidence keeps the prior cardinality rejection. Target canary logs stay outside
this standard repository.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-211/`.
