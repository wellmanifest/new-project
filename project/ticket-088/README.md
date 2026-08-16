# Ticket 088: Offer and brand commercial SSOT standards

- **ID**: ticket-088
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-16

## Cel i Zakres

Impose standards so commercial offer catalogs and brand kits HOME in product
packs (`subactor/offer`, `subactor/brand`). Portal facades must pin and drift-gate;
`wellmanifest/policy-dsl` owns promo only. Point adopters at
`wellmanifest/offer` and `wellmanifest/brand` standard pointers.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: AGENTS / GOVERNANCE_ENFORCEMENT / template AGENTS name product HOMEs
- [x] AC-02: Hub governance check passes for this ticket's allowedPaths

## Ryzyka i Uwagi

- Risk: parallel tickets still rewriting portal prices — mitigated by merge playbook + commercial-ssot gates in runtimes.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-composer.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-088/`.
