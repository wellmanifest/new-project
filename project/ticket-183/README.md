# Ticket 183: Scope repository-gate activity errors to the gated identity

- **ID**: ticket-183
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-03

## Cel i Zakres

`overlap_findings()` w `scripts/worktree_overlap_check.py` emituje
`GOV-TICKET-ACTIVITY-001` dla **każdego** checkoutu odkrytego w workspace,
zanim filtr `--identity-of` zostanie zastosowany. Bramka repozytorium
(pre-commit) zatem pada na polityki driftu obcych repozytoriów — wbrew
własnej dokumentacji (`error/GOV-WORKTREE-OVERLAP.md`: *"konflikt w cudzym
repo nie blokuje tu commita"*), która już scope'uje grupy overlap do
bramkowanej tożsamości.

Incydent z życia: sąsiednie checkouty adoptowały terminal rule
`git-ancestry-or-rewritten-patch-series` (0.20.3), którego starszy resolver
(0.19.11) nie zna — 113 findings obcych repo zablokowało każdy commit w
niespokrewnionym repozytorium workspace.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Bramka repozytorium (`--identity-of`) przechodzi, gdy obce repo
      w workspace mają nierozwiązywalne polityki aktywności.
- [x] AC-02: Workspace scan (bez filtra tożsamości) raportuje nadal pełny
      drift `GOV-TICKET-ACTIVITY-001`.
- [x] AC-03: Zachowanie overlap-detection dla tej samej tożsamości jest
      bez zmian.

## Ryzyka i Uwagi

- Risk 1: Skan workspace musi pozostać kompletny — fix wyłącznie filtruje
  przy bramce repozytorium, nie wycisza raportowania.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
i transkrypcje pozostają poza Git.
