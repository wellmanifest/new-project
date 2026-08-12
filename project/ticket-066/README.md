# Ticket 066: Canonical diagnostic solutions and publication lifecycle

- **ID**: ticket-066
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-12

## Cel i Zakres

Usunąć dwie luki ujawnione przez równoległe utrzymanie standardu:

1. ticket może zostać ręcznie utworzony poza zarządzanym allocatorem, więc
   clone-wide high-water nie widzi rezerwacji i inna sesja ponownie przydziela
   ten sam numer;
2. procedura publikacji przechodzi do `DONE` po otwarciu PR, chociaż
   implementacyjny ticket musi pozostać `IN_PROGRESS / PUBLICATION` aż do
   trusted merge.

Jednocześnie zdefiniować kanoniczny zapis rozwiązań błędów. Stabilny kod,
krótki opis i bezpieczna remediacja należą do maszynowego katalogu
`governance/diagnostics.json`; dłuższe, ryzykowne procedury należą do
`error/*.md`. Ticket przechowuje historyczny powód i dowody, nie jest
reusable runbookiem.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Udokumentowana przyczyna kolizji ticketu 060 wskazuje konkretny
  bypass zarządzanego allocatora, a reguły zabraniają ręcznego przydzielania
  `project/ticket-{NNN}`.
- [x] AC-02: Lokalny audyt wykrywa ticket poza clone-wide high-water oraz dwa
  różne intenty roszczące ten sam numer; prawidłowa rezerwacja pozostaje
  dozwolona.
- [x] AC-03: `C-PUBLISH-003` utrzymuje implementacyjny ticket w
  `IN_PROGRESS / PUBLICATION` aż do trusted merge, a `DONE / DONE` powstaje
  dopiero w governance-only closure na zintegrowanej bazie.
- [x] AC-04: Każdy emitowany stabilny `GOV-*` ma wpis z komunikatem i
  remediacją w walidowanym katalogu; złożone rozwiązania mogą wskazywać
  sprawdzalny runbook `error/*.md` o jednolitej strukturze.
- [x] AC-05: Focused testy allocatora, workspace, katalogu diagnostyk i
  traceability oraz pełny Linux contract przechodzą; hosted CI i exact-head
  approval wiążą finalny PR.

## Ryzyka i Uwagi

- Audyt lokalnego filesystemu nie może działać w CI; pozostaje read-only i
  jest wykonywany przez workspace checker. CI waliduje katalog i fixture'y.
- Runbook nie może osłabiać reguły ani proponować pominięcia bramki. W razie
  konfliktu obowiązuje `POLICY.md`, potem `CONTRIBUTING.md`.
- Nie migrujemy historycznych ticketów ani logów do `error/`; zapisujemy tam
  wyłącznie rozwiązania wielokrotnego użytku.
- Ticket 065 pozostaje osobnym `BACKLOG / PLAN` i nie wchodzi w ten zakres.

## Dowody zakończenia

- Implementacyjny PR #94 przeszedł Linux i Windows dla exact head
  `acd08f202bf3ac6543ac796631531222566ec7c8`.
- Validator App run `31578853527` wystawił deterministyczne `APPROVED` jako
  `ifuri-validator-agent[bot]` dla tego samego HEAD i `ticket-066`.
- PR #94 został scalony jako
  `9b2ca5dc55350139520121df019b1e0e0f2a9e5c`; post-merge run `31579226383`
  przeszedł Linux i Windows, a zdalny branch implementacyjny został usunięty.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-066/`.
