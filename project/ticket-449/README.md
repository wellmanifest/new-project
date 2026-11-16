# Ticket 449: Retire exact owner legacy leases after verified terminal delivery

- **ID**: ticket-449
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-11-16

## Cel i Zakres
SESSION_EXECUTION_AUTHORIZATION: the user requested continuation of verification,
repairs, overdue work and protected merging, including the reported legacy
terminal-controller incompatibility. This authorizes the bounded implementation
and declared independent publication process, never self-approval.

Provide a separate, explicit current-owner retirement adapter for expired legacy
leases whose bare repository label cannot pass the canonical controller. Require
the canonical origin, matching directory/repository label, exact owner session,
CAS, verified merged receipt and clean landed delivery. Archive the original
bytes durably before removing only that obsolete active lease slot. Never
normalize its identity or relax the ordinary release/write controllers.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Real Git fixtures verify read-only planning, exact-byte archival,
  explicit owner apply, and idempotent recovery; ordinary controllers still
  refuse bare identities.
- [x] AC-02: Foreign identity/owner, live/frozen/dirty/unmerged work, malformed
  leases, stale CAS, symlinks, hardlinks and interrupted writes fail safely.
- [ ] AC-03: Governance, package checks, fresh exact-head/base required CI and
  independent protected publication pass.

## Ryzyka i Uwagi
- maxActiveMinutes: 30. No new runtime dependencies.
- Retirement ends obsolete ownership; it grants no writing or publication
  authority. Checkout/ref removal remains a separate audited operation.
- Target-system requests, raw logs and operational receipts stay outside this
  governance hub. All original bytes remain in the owner-only journal.

## Local validation

17 retirement regressions and 34 existing terminal-controller regressions
pass. The installed governance wheel/package regression, bundled parity,
Ruff F/E9 and the deterministic governance gate pass. Fresh exact-head/base
CI and independent protected review remain required before operational use.

An additional ext4 regression exposed immediate inode reuse after retirement.
The journal now binds the file change timestamp as well as device/inode, and
replay refuses a recreated byte-identical slot. All 17 retirement regressions
pass on both tmpfs and ext4; the existing 34 controller regressions still pass.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-449/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 56/100 |
| Complexity | M |
| Estimated effort | 58 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->
