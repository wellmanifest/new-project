# Ticket 043: Publish protected lifecycle acquisition fix

- **ID**: ticket-043
- **Owner**: agent:codex
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-08

## Cel i zakres

Publish ticket-042's merged protected-lifecycle acquisition repair as immutable
patch release v0.13.2. The release must bind exact metadata, pass clean Linux
and Windows validation, use a new annotated tag and GitHub Release, and give
todo2code an immutable source SHA for ticket-050.

The user approved the complete ticket-042 plan on 2026-08-08, including its
explicit final step to publish a separate immutable release before downstream
adoption. This ticket records that already-granted publication scope; it does
not broaden the implementation repair.

That approval is now applied to this exact bounded release intent. The ticket
transitioned to `IN_PROGRESS / EDIT` before any release metadata changed.

## Kryteria odbioru

- [x] AC-01: VERSION, default manifest, tests and changelog agree on 0.13.2.
- [x] AC-02: Full Linux and protected Windows contracts pass on exact PR head
  and clean merge commit.
- [x] AC-03: A new annotated `v0.13.2` tag and non-draft GitHub Release point
  to the exact validated release commit.
- [x] AC-04: todo2code can adopt that exact release SHA and pass protected
  lifecycle validation.

## Validation evidence

- Release preparation commit: `d8fb5f952416a12ce358c64f27c2d77fa149e9f6`.
- VERSION, default manifest, changelog and current-version assertions agree on
  0.13.2.
- Full Linux CI command contract passes, including lifecycle, governance,
  adoption-lock, decision, required-check and rule-enforcement suites.
- Protected PR #64 passed `test` and `windows-governance`; trusted Validator
  App approved exact head `b1d63fb5d60fdcdcb391ab0dc500b16e4df54f61`.
- PR #64 merged as `85631ea24d127f1f4797d2a67f3524a63cbbc95a`,
  and the full Linux contract passed in a clean detached checkout of that
  release commit.
- Annotated tag `v0.13.2` peels to exact commit `85631ea`; its GitHub Release
  is published, non-draft and not a prerelease.
- Downstream todo2code PR #70 adopted exact SHA `85631ea`, passed protected
  lifecycle governance at head `fee491aac475ecbe6ce843d5fdbba25471c1db0e`,
  and merged as `f60d3cc317995bc618fea1c25d9c4ec9bf09bc30`.

## Ryzyka i uwagi

- Never move or overwrite a tag or release.
- No further workflow or validator behavior change belongs in this ticket.
- Downstream adoption remains governed by todo2code ticket-050.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-043/`.
