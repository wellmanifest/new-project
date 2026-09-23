# Ticket 268: Enforce standard pack baseline only for adopters in enforce mode

- **ID**: ticket-268
- **Owner**: claude
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-23

## Cel i Zakres
Ticket-257 (0.20.42) made the adopter workflow run `standard_pack_check.py
--strict`, which fails on every missing pack even when the adopter's
`.governance/standard-adoption.json` declares `mode: audit`. Adopters that
have not declared pack adoptions (e.g. `wellmanifest/wellman`) therefore fail
CI regardless of their chosen rollout mode. Let the declared mode decide:
`enforce` still fails, `audit` reports in CI without failing. The `--strict`
flag remains available in the checker. Released as standard 0.20.49.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: The adopter workflow invokes the pack check without `--strict`.
- [x] AC-02: `tests/standard-pack-check.test.sh` proves enforce mode still
      fails on missing packs and fails if the template forces `--strict` again.
- [ ] AC-03: Protected merge, standard `v0.20.49` and `wellman-v0.20.49`.

## Ryzyka i Uwagi
- Audit-mode adopters no longer fail CI on missing packs; the finding stays
  visible in the job output and adopters opt into failure with `enforce`.

## Delivery contract

- **Accepted base**: `7a8f8cac3676f66f37e3ea895508f1fcd5526d56`
- **Target**: `main`
- **Complexity**: S
- **Validation**: standard-pack test (with template negative), wellman
  package test, branch hygiene template test, governance gate, `git diff --check`.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-268/`.
