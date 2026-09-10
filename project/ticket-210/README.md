# Ticket 210: Bound default validation to the published integration

- **ID**: ticket-210
- **Owner**: agent:openai
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-09-10

## Cel i Zakres
SESSION_EXECUTION_AUTHORIZATION: user continuation on 2026-09-10 authorizes
the upstream fix, tests and protected publication, followed by target adoption
in its own repository. It does not grant trusted merge approval.

The no-base gate can select a historical adoption ticket's accepted base on a
clean published commit. Resolve only that narrow case to the integration's
first parent using the existing clean-published observation.

## Kryteria Odbioru (Acceptance Criteria)
- AC-01: Real Git tests reproduce the broad historical range and verify clean
  published branch/detached scope; explicit bases and uncertain states stay safe.
- AC-02: Governance/adoption suites and protected Linux/Windows CI pass with
  an atomic 0.20.21 release projection and independent approval.

## Ryzyka i Uwagi
A falsely narrowed range could hide live work. Require exact origin target HEAD,
a resolvable parent and a clean tree; retain the prior fallback otherwise.
This observation never closes tickets or grants publication authority.
Existing PRs 313 and 316 have distinct implementation scopes and stay untouched.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-210/`.
