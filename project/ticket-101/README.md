# Ticket 101: Release generated receipt ownership as new-project 0.18.2

- **ID**: ticket-101
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-21

## Cel i Zakres

Opublikować zintegrowaną poprawkę własności generated artifact receipt z
ticket-100 jako immutable `new-project 0.18.2`. Wydanie zmienia wyłącznie
nośniki wersji, aktywne asercje i changelog; nie zmienia semantyki poprawki po
jej merge.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: `VERSION`, oba manifesty i aktywne asercje deklarują `0.18.2`.
- [x] AC-02: Changelog opisuje exact generated receipt ownership jako patch.
- [x] AC-03: Wszystkie suite'y, Ruff, secret scan i governance przechodzą.
- [ ] AC-04: PR otrzymuje trusted exact-head approval i merge bez zmiany drzewa.
- [ ] AC-05: Czysty `main`, tag i GitHub Release `v0.18.2` wskazują dokładny
  zintegrowany merge.

## Ryzyka i Uwagi

- Tag i release są niemutowalne; powstaną dopiero po trusted merge i reteście.
- Adopcja w Platform jest osobnym target-owned ticketem.
- Czysty base po ticket-099 zawiera nieużywany import `sys` wykrywany przez
  przypięty Ruff; release usuwa wyłącznie ten bezskutkowy import, aby nie
  publikować standardu z czerwoną bramką.

## Dowody przed publikacją

- 11/11 `tests/*.test.sh`: PASS.
- Ruff 0.15.21: PASS po usunięciu jednego nieużywanego importu z bazy.
- Exact-base governance: 0 błędów, 0 ostrzeżeń.
- Tag ani release `v0.18.2` nie istnieją przed publikacją.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-101/`.
