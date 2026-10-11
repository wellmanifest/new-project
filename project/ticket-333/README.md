# Ticket 333: Reject lease parent symlink races

- **ID**: ticket-333
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-10-11

## Goal and scope

SESSION_EXECUTION_AUTHORIZATION: the user requests continuation after the
tested allocator remediation was reported as necessary to unblock independent
review of OneDev PR 557. Fix the canonical generator, validate its lease
creation and publish immutable 0.20.94 through the declared protected process.
This maintenance ticket contains no application implementation or application
ticket records.

Create each lease through no-follow directory descriptors, including parent
creation. Reject unsupported descriptor APIs before reserving a ticket ID or
creating a branch. Keep the existing lease shape and exclusive creation.

## Acceptance criteria

- [x] AC-01: Existing allocation tests and deterministic parent-symlink race,
  overwrite, private-mode and missing-capability regressions pass.
- [ ] AC-02: All four release projections agree on 0.20.94; source governance,
  package and required platform checks pass.
- [ ] AC-03: Independent exact-head approval and protected merge precede
  immutable publication and adopter updates.

## Preservation and limits

The allocated branch was based on local main, then rebased with an empty
commit range onto the observed published main SHA
`3b5686a4cd4ac6537eb7845c9a7a71a7fb1706eb`. Unrelated local main commit
`7804598c426fbb29f2ce49655f1ab0930681c724` and other checkouts remain intact.
Unsupported hosts fail before allocation effects; this does not claim a new
Windows file-allocator implementation. Raw logs and continuity receipts stay
outside tracked source. Passing tests grants no review or merge authority.

## Validation

All 13 allocation regressions passed. Version-parity tests and source governance
passed. The installed-wheel suite and governance script suite (73 additional
cases) passed in a networkless container using the accepted executor image.
Remaining delivery requires the declared Goal checks, independent current-head
Linux/Windows verification, trusted approval, merge and immutable publication.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-333/`.
