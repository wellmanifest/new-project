# Ticket 276: Add proprietary anti-AI mining license template and update owner

- **ID**: ticket-276
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Created**: 2026-09-26

## Goal and scope

1. Dodanie szablonu licencji komercyjnej z ochroną anty-mining (`template/files/LICENSE.proprietary.template`) z klauzulami TDM opt-out (Art. 4 ust. 3 Dyrektywy UE 2019/790) oraz bezwzględnym zakazem indeksowania i trenowania LLM.
2. Zaktualizowanie szablonu Apache 2.0 (`template/files/LICENSE.template`) o formalne oznaczenie podmiotu właścicielskiego: `Tomasz Sapletta Prototypowanie.pl NIP: 5881918662, REGON: 220665410`.

## Acceptance criteria

- [x] AC-01: Szablon `template/files/LICENSE.proprietary.template` istnieje i zawiera klauzule Proprietary, TDM opt-out oraz Tomasz Sapletta Prototypowanie.pl.
- [x] AC-02: Szablon `template/files/LICENSE.template` zawiera w appendix klauzulę własnościową Tomasz Sapletta Prototypowanie.pl.
- [x] AC-03: Weryfikacja governance check w worktree i repozytorium root zakończona statusem PASS.

## Tracking boundary

This directory contains the minimal reviewed intent. Optional participant prose
and raw command logs are not required delivery output.
