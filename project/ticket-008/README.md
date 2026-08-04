# Ticket 008: Pilotaż adopcji w pojedynczym workstreamie

- **ID**: ticket-008
- **Owner**: unresolved:human
- **Status**: BACKLOG
- **Workflow state**: BACKLOG
- **Utworzono**: 2026-08-04

## Cel i zakres

Przeprowadzić kontrolowany pilot `goal governance adopt` w jednym istniejącym
repozytorium z pojedynczym workstreamem. Ticket i dowody implementacyjne
powstają w repozytorium pilota, a hub przechowuje tylko zanonimizowane wnioski
dotyczące standardu.

## Kryteria odbioru

- [ ] Pilot używa pełnego SHA wydania i zaczyna od `--check`.
- [ ] Scenariusz pozytywny przechodzi bez ręcznego obejścia gate'a.
- [ ] Drift, obcy reviewer, nieznany status i zmiana poza zakresem są odrzucone.
- [ ] Lokalna konfiguracja pilota nie trafia do huba.
