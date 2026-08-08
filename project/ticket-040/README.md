# Ticket 040: Reduce managed Python complexity for downstream review

- **ID**: ticket-040
- **Owner**: unresolved:human
- **Status**: PLAN
- **Workflow state**: WAIT_FOR_APPROVAL
- **Utworzono**: 2026-08-08

## Cel i Zakres

Downstream adoption of immutable v0.13.0 is provenance-correct and passes the
target governance, host and Docker suites, but the target's protected Koru gate
reviews changed managed Python sources and rejects five pre-existing
cyclomatic-complexity findings:

- `scripts/governance_check.py`: `work_classification_error` (37),
  `package_strategies` (17), `adoption_lock` (18) and
  `atomic_standard_adoption_paths` (28);
- `scripts/decision_record.py`: `parse_dsl_record` (21).

This service-health ticket performs a behavior-preserving extraction of small,
named helpers so every listed function and its extracted helpers stay at
cyclomatic complexity 15 or lower under the pinned downstream Vallm/Koru
toolchain. Existing diagnostics, parsing, hashes, provenance rules and CLI
behavior remain byte-for-byte equivalent at their public boundaries.

The implementation is limited to the two Python sources and their existing
shell regression suites. Publishing the result is a separate immutable release
ticket after this change is merged; tags and version files are out of scope.

## Kryteria Odbioru (Acceptance Criteria)

- [ ] AC-01: The five named functions no longer exceed cyclomatic complexity
  15, and no extracted helper exceeds 15 under Vallm 0.1.94's lizard rule.
- [ ] AC-02: Classification validation returns the same stable messages and
  accepts/rejects the same valid and malformed contracts.
- [ ] AC-03: Decision DSL parsing preserves required fields, JSON values,
  canonical round trips and exact fail-closed diagnostics.
- [ ] AC-04: Atomic-adoption package/lock/hash verification preserves all
  positive and negative v0.13.0 regression cases.
- [ ] AC-05: The complete Linux governance contract, Windows governance test
  and Docker checks pass with no dependency, schema or public-interface change.
- [ ] AC-06: A downstream-style pinned Koru/Vallm scan of the two managed
  Python sources has zero deterministic findings; semantic findings remain
  advisory.

## Ryzyka i Uwagi

- Risk: helper extraction could change diagnostic ordering or exception
  boundaries. Mitigation: keep return values and call order stable and extend
  focused regression fixtures before running the complete contract.
- Risk: lowering only the five reported functions could move complexity into a
  new oversized helper. Mitigation: enforce the same absolute threshold across
  all helpers added or touched by this ticket.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-040/`.
