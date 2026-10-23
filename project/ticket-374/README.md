# Ticket 374: Idle ticket takeover after 15 minutes with autonomy state board

- **ID**: ticket-374
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-10-23

## Cel i Zakres
Decyzja użytkownika (2026-10-23): agent może przejąć ticket innego piszącego po
`coordination.idleTakeover.idleMinutes` (15 min w manifeście domyślnym i hubu)
bez zaobserwowanej aktywności, a każde wykrycie odświeża tablicę stanu z linkami
do projektu, gałęzi, README, PR i listy issues oraz ścieżką worktree. Zgodnie z
`wellmanifest/worktrees` v5, `nohardcode` i `ssot`: polityka tylko w manifeście,
układ katalogów i fazy z kontraktu lease, wynik przejęcia jako JSON z
`worktreePath`/`leasePath`. Hub dopuszcza 2 aktywne tickety governance.

SESSION_EXECUTION_AUTHORIZATION: user request 2026-10-23; slot freed by the
accepted handoff of ticket-373 (BLOCKED, PR #531 unchanged).

## Kryteria Odbioru (Acceptance Criteria)
Wycinek 1 z 3 (374 → 375 runtime `idle_takeover.py` i tablica → 376 `work_start_check` i instrukcje AGENTS), zgodnie z limitem XS/S hubu.

- [x] AC-01: schemat i walidator przyjmują zamkniętą politykę `coordination.idleTakeover` i odrzucają złe granice, typy i pola; manifesty domyślny i hubu: włączona, 15 min, lease 120 min; hub: 2 aktywne tickety governance. `change_lease_check.py` eksportuje `WORKTREES_ROOT`, `LEASE_ROOT`, `MAX_LEASE_BYTES`, kopia w pakiecie identyczna. `tests/idle_takeover_test.py`, `change_lease_safety_test.py`, `wellman-package.test.sh` przechodzą.
- [ ] AC-02: governance-check i niezależna walidacja PR.

## Ryzyka i Uwagi
- Polityka nie działa, dopóki ticket-375 nie dostarczy `idle_takeover.py`.
- Pełna implementacja (wszystkie 3 wycinki) jest przetestowana w odizolowanym klonie: 16 testów runtime oraz zestawy agent-hosts, rule-enforcement, reusable_checks, governance-validator, wellman-package.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-374/`.
