# Ticket 375: Idle takeover slice 2/3: idle_takeover runtime and autonomy board

- **ID**: ticket-375
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-10-23

## Cel i Zakres
Wycinek 2 z 3 mechanizmu przejmowania po bezczynności (decyzja użytkownika
2026-10-23, ticket-374 scalony w PR #533). `scripts/idle_takeover.py`:

- `observe` klasyfikuje każdy lease (`ACTIVE`, `IDLE_TAKEOVER_ELIGIBLE`,
  `IDLE_FROZEN`, `IDLE_INTEGRATED`, `IDLE_NO_WORKTREE`, `IDLE_NOT_TAKEABLE`,
  `POLICY_DISABLED`, `NONCANONICAL_LAYOUT`, `INVALID_LEASE`) i zapisuje tablicę
  autonomii `.subactor/cache/autonomy-board.{json,md}` ze ścieżkami worktree i
  lease oraz linkami do repozytorium, PR i listy issues;
- `takeover` przejmuje tylko `IDLE_TAKEOVER_ELIGIBLE`: snapshot brudnej pracy,
  CAS expire/release/claim przez przypięty `change_lease_check.py`, receipt,
  wynik JSON z `worktreePath`, `leasePath` i `writerEnvironment`.

Polityka wyłącznie z manifestu, układ i fazy wyłącznie z kontraktu lease
(`nohardcode`, `ssot`, `worktrees` v5). Pakowane jako `.governance/idle_takeover.py`
z diagnostyką `GOV-IDLE-TAKEOVER-001/002` i runbookiem.

SESSION_EXECUTION_AUTHORIZATION: user request 2026-10-23 („kontynuuj, scalaj, testuj”).

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `tests/idle_takeover_test.py` (24 testy: polityka, klasyfikacja, tablica, snapshot, CAS pod blokadą, odmowy; regresje uwag validatora: zła polityka, nieaktualny origin, rename w porcelain -z, zajęta blokada), agent-hosts, rule-enforcement, governance-validator przechodzą.
- [ ] AC-02: governance-check i niezależna walidacja PR.

## Ryzyka i Uwagi
- `work_start_check.py` odświeży tablicę i AGENTS opisze regułę dopiero w ticket-376.
- Przejęcie nie daje prawa do review, zatwierdzenia ani scalenia; validator pozostaje wymagany.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-375/`.
