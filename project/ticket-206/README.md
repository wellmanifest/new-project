# Ticket 206: Seed adopter required-checks from a template, not from the hub instance

- **ID**: ticket-206
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Owner**: founder

## Goal and scope

Every other adopter seed comes from `template/files/*.template.*`. Only
`.governance/required-checks.json` was sourced from
`governance/required-checks.json` — the hub's own live instance. An adopter that
never rewrote it therefore declares `wellmanifest/new-project`, points at the
hub's `ci.yml`, and requires the hub's job names `test` and
`windows-governance`, which no adopter workflow publishes.

Measured 2026-09-09 across 88 governed checkouts in three organisations: 30
carry a foreign identity and 22 require a check no local workflow can publish.
Zero managed files drifted — content distribution was never the problem.

A required check no workflow publishes blocks every pull request in that
repository, permanently, while looking configured.

## What already existed, and why it did not fire

`create_adoption_lock.py` already repairs this during adoption: when the target
declaration says `wellmanifest/new-project`, it regenerates the declaration from
the target's own workflows and identity through `generate_required_checks.py`.

That repair is keyed on the literal hub identity, and it only runs during an
adoption. A repository that adopted before the repair existed, or has not
adopted since, keeps the wrong instance indefinitely and nothing reports it.

This ticket connects the two halves rather than adding a third mechanism.

## Changes

1. `template/files/required-checks.template.json` — the adopter seed, declaring
   `unresolved/adopter` and the two check names the adopter workflow template
   actually publishes. The marker satisfies the schema's `owner/name` pattern
   while being unmistakably unadapted.
2. `governance/package-manifest.json` — the seed source points at the template.
3. `create_adoption_lock.py` — the existing derivation now triggers on the
   template marker as well as the legacy hub identity, so both unadapted forms
   are projected from the target's real workflows.
4. `check_required_checks.py` — fails closed when the instance declares a
   repository other than this checkout's origin, or still carries the marker.
   Identity comes from `origin`, falling back to `GITHUB_REPOSITORY` in CI.
5. The extendable allowlists in `governance_check.py` and
   `create_adoption_lock.py` accept both the template and the legacy source, so
   a repository pinned before this change still validates while it upgrades.

The same allowlist exists in two scripts and the same expectation is pinned a
third time inside the validator test. Finding all three cost three separate test
failures; they are listed here so the next change to this seed does not repeat
that search.

## Non-goals

Does not rewrite the 30 affected instances. Each belongs to its own repository
and ticket, and a correct instance needs that repository's real job names. Once
they adopt this revision the derivation repairs them automatically, which is the
reason for wiring the marker into it rather than adding a new repair path.

## Acceptance criteria

- [x] AC-01: The adopter seed is a template, and the package manifest names it.
- [x] AC-02: A fresh adoption projects the declaration from the target's own
      workflows and identity, so the seed marker never survives adoption.
- [x] AC-03: An instance declaring a repository other than the checkout's origin
      fails the required-checks gate, naming both identities.
- [x] AC-04: An instance still carrying the unadapted marker fails the gate.
- [x] AC-05: The seed declares exactly the check names the adopter workflow
      template publishes, asserted against that template rather than restated.
- [x] AC-06: A repository pinned before this change still validates and still
      generates a lock.

Validation: `tests/required-checks.test.sh`, `tests/adoption-lock.test.sh`,
`tests/governance-validator.test.sh`; 18/18 CI suites pass.

## Tracking boundary

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-206/`.
