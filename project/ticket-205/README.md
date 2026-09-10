# Ticket 205: Detect fleet conformance defects in adopter governance instances

- **ID**: ticket-205
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Owner**: founder

## Goal and scope

`governance/required-checks.json` ships to adopters as an `extendable` seed. An
adopter that never rewrote it keeps the hub's own instance: the hub's repository
name, the hub's workflow path, and the hub's job names `test` and
`windows-governance`.

Measured across three organisations, 88 governed checkouts:

| finding | repositories |
| --- | --- |
| `FLEET-INSTANCE-001` instance declares another repository | 30 |
| `FLEET-CHECK-002` required check no workflow can publish | 22 |
| `FLEET-GATE-004` declared gate no workflow invokes | 24 |
| `FLEET-MANAGED-003` managed file drifted from its own pin | 0 |

The zero matters as much as the rest: content distribution works. What fails is
instance data and execution. Adopters match their managed digests exactly while
requiring checks that can never turn green.

The consequences are not cosmetic:

- A required check no workflow publishes blocks every pull request in that
  repository, permanently, and the branch ruleset has no way to know.
- The shipped `check_required_checks.py` — which already compares required
  names to published jobs — crashes in those adopters with `FileNotFoundError`
  on the hub path `governance/required-checks.json`, so the one gate that would
  have caught this never reports.
- `externalConsumers` inside the copied instance points `validator-agent` at
  `governance/required-checks.json#/requiredCheckNames`, which in an adopter is
  the wrong repository's list.

## What this adds

`scripts/fleet_conformance.py` audits many governed checkouts at once and asks
one question of each: do this repository's declarations describe this
repository, or something else? It is read-only — it opens files, never a
network connection, and never writes to what it inspects.

The rules live in `governance/fleet-conformance.rules.json`, so adding a check
is data rather than code. A test asserts the rule set and the implemented checks
are exactly the same set in both directions, because a rule naming a missing
check and a check no rule reaches are equally silent failures.

It composes with `subactor/diagit` rather than duplicating it: diagit discovers
and audits Git state across a fleet; this reads the governance instances inside
the checkouts diagit already knows about.

## Non-goals

This ticket does not rewrite the 30 affected instances. Each belongs to its own
repository and its own ticket, and a correct instance needs that repository's
real workflow job names — which is exactly what the audit now reports.

It also does not change how the seed is distributed. Whether
`required-checks.json` should ship as `extendable` at all is a separate decision
about the standard, and this audit is the evidence that decision needs.

## Acceptance criteria

- [x] AC-01: A checkout whose declarations describe itself produces no finding.
- [x] AC-02: An instance naming another repository is an error reporting both
      the declared identity and the origin identity.
- [x] AC-03: A required check name no workflow publishes is an error reporting
      what the repository does publish.
- [x] AC-04: Drift is judged against the repository's own pinned lock, so a
      matching digest is clean and a hand edit is not.
- [x] AC-05: Rule selection is honoured, and the rule set and implemented checks
      are proven to be the same set in both directions.

Validation: `bash tests/fleet-conformance.test.sh`, wired into CI.

## Tracking boundary

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-205/`.
