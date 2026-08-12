# Ticket 071: Detect orphaned local branches in terminal workspace audits

- **ID**: ticket-071
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-12

## Cel i Zakres

Naprawić regresję audytu terminalnego workspace: checker wykrywa dodatkowe
worktree i klony, ale pomija lokalne gałęzie pozostawione po usunięciu
worktree. Implementacja ma być read-only, chronić unikalne commity i odróżniać
aktywną, jawnie allowlistowaną pracę od osieroconego refa.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Audyt zgłasza każdą nie-defaultową lokalną gałąź, która nie jest
      przypisana do jawnie allowlistowanego aktywnego checkoutu.
- [x] AC-02: Usunięcie worktree bez usunięcia jego zwolnionej gałęzi pozostawia
      deterministyczny błąd; po bezpiecznym usunięciu dokładnego refa audyt
      przechodzi.
- [x] AC-03: Finding zawiera branch, HEAD, default branch i dokładny primary
      checkout, ale checker nigdy sam niczego nie usuwa.
- [x] AC-04: Katalog diagnostyk, runbook, policy-as-code i instrukcje agentów
      opisują ten sam kontrakt.
- [ ] AC-05: Focused oraz pełny Linux/Windows contract przechodzą przed
      publikacją kolejnej immutable wersji standardu.

## Ryzyka i Uwagi

- Aktywna gałąź nie może być błędnie uznana za śmieć; wyjątek wymaga dokładnej
  ścieżki `--allow`, nie wzorca ani automatycznego zgadywania.
- Ref z unikalnym commitem musi zostać zachowany przed cleanupem; validator
  wyłącznie raportuje i nigdy nie wykonuje `branch -D` ani `update-ref -d`.
- Governance-only closure aktywnego wcześniej `ticket-070` została scalona jako
  `f5c2dcb754b01b97f1fee8ca00a569f4c884db6a`; workstream jest zwolniony i
  implementacja 071 może rozpocząć się na tej dokładnej bazie.
- Source-hub Linux contract i bounded Goal candidate adoption przechodzą;
  hosted Windows, exact-head Validator review i merge pozostają bramą
  publikacji. Wersja 0.16.2 będzie osobnym, zależnym ticketem wydaniowym, aby
  7-plikiowa poprawka nie przekroczyła limitu 9 po dodaniu sześciu nośników
  wydania.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-071/`.
