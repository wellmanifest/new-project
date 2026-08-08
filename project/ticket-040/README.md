# Ticket 040: Reduce managed Python complexity for downstream review

- **ID**: ticket-040
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
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

- [x] AC-01: The five named functions no longer exceed cyclomatic complexity
  15, and no extracted helper exceeds 15 under Vallm 0.1.94's lizard rule.
- [x] AC-02: Classification validation returns the same stable messages and
  accepts/rejects the same valid and malformed contracts.
- [x] AC-03: Decision DSL parsing preserves required fields, JSON values,
  canonical round trips and exact fail-closed diagnostics.
- [x] AC-04: Atomic-adoption package/lock/hash verification preserves all
  positive and negative v0.13.0 regression cases.
- [ ] AC-05: The complete Linux and Windows governance contracts pass with no
  dependency, schema or public-interface change. The hub has no Dockerfile or
  compose contract; downstream Docker already passes and must pass again after
  the dependent release adoption.
- [x] AC-06: A downstream-style pinned Koru/Vallm scan of the two managed
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

## Zatwierdzenie

Użytkownik zatwierdził dokładny czteroplikowy, behavior-preserving zakres
2026-08-08. Ticket przeszedł do `IN_PROGRESS / EDIT` przed zmianą źródeł lub
testów.

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-040/`.

## Dowody walidacji

- Refactor commit: `70ed004fda3d5da6e2dc456bb87f579907ef5b60`.
- Lizard 1.23.0 with threshold 15 reports zero exceeded functions across both
  files; the five original functions now have CC 10, 9, 10, 8 and 5.
- Pinned Vallm 0.1.94 with the same parser normalization as protected Koru
  reports 2/2 files passed and zero deterministic findings.
- All configured Linux CI commands pass, including decision-record,
  governance, atomic-adoption, branch lifecycle, environment and traceability
  suites.
- Local PowerShell is unavailable; the required Windows contract remains for
  protected CI before merge.
