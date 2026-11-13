# Ticket 432: Honour declared terminal outcomes and skip ignored runtime trees

- **ID**: ticket-432
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-11-13

## Cel i Zakres

Dwa defekty standardu potwierdzone na realnym adopterze (`wellmanifest/polycell`):

1. `scripts/terminal_lease_release.py` akceptuje wyłącznie outcome `merged`, choć zarządzana
   polityka (`governance/ticket-activity.json`) deklaruje `no-change` z `releasesReservation: true`.
   Lease po dostawie `no-change` nigdy nie może zostać zwolniony, więc adopter zostaje
   z `claimed` lease bez pracy do kontynuowania.
2. `scripts/governance_check.py` (sekcja 5, `GOV-VERSION-001`) enumeruje `**/__init__.py` globem
   i pomija tylko statyczną listę katalogów. Lokalne runtime'y (`.run/…/site-packages`, venv,
   cache buildów) generują fałszywe błędy wersji, przez co bramka adoptera jest czerwona
   w każdym checkoucie z lokalnym środowiskiem.

Zakres: źródło walidatora (`scripts/`), jego kopia bundled (`packages/wellman/…/_bundled/`)
utrzymana bajt w bajt, testy oraz przeniesienie porzuconego hardenigu `ticket-418`
(checker lease ładowany z pakietu walidatora, nie z inspekcjonowanego repo).

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Lease w fazie `claimed` z zweryfikowanym receiptem `no-change` przechodzi `cancel → release`.
- [x] AC-02: Nieznany outcome, obcy ticket, brak `releasesReservation` lub zerwana ancestry nadal odmawiają.
- [x] AC-03: `GOV-VERSION-001` nie zgłasza gitignorowanych runtime'ów, a śledzony `__init__.py` z rozjazdem nadal zgłasza.
- [x] AC-04: Checker lease jest ładowany z pakietu walidatora (hardening `ticket-418`), kopia hub/bundled bajt w bajt.
- [x] AC-05: `tests/terminal_lease_release_test.py`, `tests/version-parity.test.sh`,
  `tests/change_lease_safety_test.py`, `tests/governance-validator.test.sh` i `./project/governance-check.sh` przechodzą.
- [x] AC-06: Alokator zapisuje kanoniczny `owner/name`, a `writer-check` akceptuje zarówno kanoniczny ref, jak i legacy `local/<sha256>`; obca tożsamość i obce repo nadal odrzucane.

## Ryzyka i Uwagi
- Risk 1: `git ls-files` w checkoutach bez Gita — zachowany fallback do poprzedniego globu (bez zmiany zachowania).


## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-432/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 68/100 |
| Complexity | L |
| Estimated effort | 70 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->
