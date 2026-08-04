# Ticket 006: Synchronizacja roadmapy po wydaniu 0.10.0

- **ID**: ticket-006
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-04

## Cel i zakres

Uzgodnić dokumentację z bieżącym stanem `main`: wersją `0.10.0`, scalonymi
PR-ami #1-#4, brakiem immutable tagu/GitHub Release oraz niedomkniętymi
ticketami 002 i 005. Zastąpić nieaktualny plan po 0.9.0 kolejnością prac
opartą na jawnych zależnościach i utworzyć nieaktywne tickety backlogu.

## Kryteria odbioru

- [x] AC-01: Roadmapa rozróżnia fakty zakończone, pracę zablokowaną i backlog.
- [x] AC-02: `TODO.md` i `project/TICKETS.md` wskazują te same statusy i zależności.
- [x] AC-03: Każdy dalszy zakres ma osobny ticket `BACKLOG` klasy `XS` lub `S`.
- [x] AC-04: Dokumentacja nie przedstawia 0.9.0 jako bieżącej wersji standardu.

## Dowody walidacji

- `git diff --check` — PASS.
- Walidacja wszystkich `intent.json` — PASS.
- `tests/governance-scripts.test.sh` — PASS.
- `tests/governance-validator.test.sh` — PASS.
- `tests/adoption-lock.test.sh` — PASS.
- Kontrola niedozwolonych ścieżek lokalnych i unsafe markerów — PASS.

## Ryzyka i uwagi

- Zmiana jest planistyczna; nie publikuje tagu ani nie modyfikuje systemów
  docelowych.
- Tickety 007-013 nie rezerwują zakresów, dopóki pozostają w `BACKLOG`.

## Uczestnicy

- Human participant: unresolved; plik `user-*` nie jest tworzony przez agenta.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ticket przechowuje wyłącznie decyzje, plan i dowody governance.
