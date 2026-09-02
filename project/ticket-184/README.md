# Ticket 184: Prepare pinned standard updates during pre-commit

- **ID**: ticket-184
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-09-02

## Cel i Zakres
Rozszerzyć zarządzany pre-commit adopterów o automatyczny kontroler świeżości
przypiętego standardu. Hook najpierw weryfikuje lokalny staged pin, a następnie
deleguje wykrycie najnowszego finalnego release i przygotowanie atomowej adopcji
do Goal. Standard nie implementuje drugiego klienta GitHub ani nie wykonuje
`git fetch` bezpośrednio. Aktualizacja może powstać wyłącznie w aktywnym
tickecie adopcyjnym; zwykły ticket otrzymuje stabilną odmowę i remediację.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Żądanie użytkownika stanowi `SESSION_EXECUTION_AUTHORIZATION` dla
      bezpiecznego automatycznego przygotowania aktualizacji pre-commit.
- [x] AC-02: Zarządzany hook uruchamia kontroler po lokalnej walidacji pina i
      przed worktree guard, przekazując dokładny root oraz ticket brancha.
- [x] AC-03: Kontroler nie używa shella ani sieci samodzielnie; wywołuje
      `goal governance adopt --latest --pre-commit` i propaguje jego wynik.
- [x] AC-04: Brak kompatybilnego Goal lub odmowa aktualizacji emituje
      `GOV-STANDARD-UPDATE-001` z kanonicznym runbookiem.
- [x] AC-05: Package manifest instaluje kontroler jako zarządzany plik, a
      deterministyczne testy, jawny krok CI i governance przechodzą.
- [x] AC-06: `standard-adoption.json` może wyłączyć kontrolę albo wybrać
      wykonawcę `goal` lub `koru-goal`; brak i błędy konfiguracji zachowują
      kompatybilność albo kończą się fail-closed zgodnie ze schematem.
- [x] AC-07: Materialna zmiana i wszystkie projekcje wersji publikują razem
      niezmienny standard `new-project 0.20.4` po chronionym merge.

## Walidacja

- `bash tests/precommit-standard-update.test.sh`: PASS.
- `bash tests/adoption-lock.test.sh`: PASS.
- `bash tests/governance-scripts.test.sh`: PASS.
- `bash tests/agent-hosts.test.sh`: PASS.
- `python3 scripts/audit_diagnostics.py --format json`: 92 kody, 0 ustaleń.
- `./project/governance-check.sh --actor agent --base bca7d4c...`: GOV-PASS.
- Test konfiguracji potwierdza kompatybilny brak sekcji, wyłączenie wykonania,
  dokładne wywołanie `koru goal -- ...` i fail-closed dla błędnego JSON.

## Ryzyka i Uwagi
- Ryzyko: cicha zmiana zaufanego upstreamu w zwykłym tickecie. Mitygacja:
  Goal weryfikuje release i ticket adopcyjny; hook nigdy sam nie stage'uje ani
  nie zatwierdza zmian i zatrzymuje bieżący commit po przygotowaniu upgrade'u.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-184/`.
