# Ticket 071: Detect orphaned local branches in terminal workspace audits

- **ID**: ticket-071
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
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
- [x] AC-05: Focused oraz pełny Linux/Windows contract przechodzą przed
      publikacją kolejnej immutable wersji standardu.

## Ryzyka i Uwagi

- Aktywna gałąź nie może być błędnie uznana za śmieć; wyjątek wymaga dokładnej
  ścieżki `--allow`, nie wzorca ani automatycznego zgadywania.
- Ref z unikalnym commitem musi zostać zachowany przed cleanupem; validator
  wyłącznie raportuje i nigdy nie wykonuje `branch -D` ani `update-ref -d`.
- Governance-only closure aktywnego wcześniej `ticket-070` została scalona jako
  `f5c2dcb754b01b97f1fee8ca00a569f4c884db6a`; workstream jest zwolniony i
  implementacja 071 może rozpocząć się na tej dokładnej bazie.
- Source-hub Linux contract, hosted Windows i bounded Goal candidate adoption
  przeszły, a exact-head Validator zatwierdził niezmieniony payload przed
  merge'em. Wersja 0.16.2 będzie osobnym, zależnym ticketem wydaniowym, aby
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

## Zintegrowana dostawa

- PR #104 miał head `d43e44c4e760299c0581b3e58281eb773cb15406`;
  oba uruchomienia `test` i `windows-governance` zakończyły się sukcesem.
- `ifuri-validator-agent[bot]` zatwierdził dokładnie ten head w runie
  `31617357073`; advisory GLM również nie zgłosił findings, ale nie był trust
  rootem.
- Payload został scalony bez zmiany drzewa jako
  `7a2dd94194e67567b7c9c2ffbae91951c673e102`; post-merge run `31617559613`
  zakończył się sukcesem, a gałąź implementacyjna zniknęła lokalnie i zdalnie.
- Immutable publikacja 0.16.2 pozostaje następnym, zależnym ticketem; 071
  kończy się na zweryfikowanym source-hub payloadzie i nie udaje wydania.
