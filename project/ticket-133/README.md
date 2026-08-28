# Ticket 133: Make material delivery atomic and receipt-closed

- **ID**: ticket-133
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-28

## Cel i Zakres

Remove the standard rules that turn one material delivery into a plan-only
commit, a ticket-heavy implementation commit and a post-merge closure PR.
Preserve bounded authorization and exact-head evidence by treating the tracked
ticket as an intent snapshot and the protected merge receipt as terminal truth.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Intent may be introduced atomically with the first material change.
- [x] AC-02: Ticket-carrier-only changes fail with a stable diagnostic.
- [x] AC-03: A protected external merge receipt closes the lifecycle without a
  repository closure commit or PR.
- [x] AC-04: New tickets require only `README.md` and `intent.json`; tracked raw
  logs and participant prose are optional.
- [x] AC-05: Deterministic tests cover the atomic-intent and material-delivery
  rules.

## Ryzyka i Uwagi

- Existing adopters remain compatible; optional historical files are preserved.
- Protected review and merge evidence remain mandatory and external to the
  author checkout.

## Authorization

The user's request to investigate and repair the Subactor ticket loop records
`SESSION_EXECUTION_AUTHORIZATION` for this bounded standard maintenance.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent execution is bound by this README and the machine-readable
  `intent.json`; no raw transcript is tracked.

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-133/`.
