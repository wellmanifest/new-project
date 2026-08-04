# Ticket 013: Runbook Validator App i OpenRouter

- **ID**: ticket-013
- **Owner**: unresolved:human
- **Status**: BACKLOG
- **Workflow state**: BACKLOG
- **Utworzono**: 2026-08-04

## Cel i zakres

Opisać praktyczne działanie Validator App: położenie repozytorium aplikacji,
instalację GitHub App, przepływ PR/evidence, miejsce przechowywania sekretu
OpenRouter, rotację/revocation oraz granicę między deterministycznym gate'em a
advisory LLM. Dokument ma zawierać diagramy Mermaid.

## Kryteria odbioru

- [ ] Diagram pokazuje GitHub, App, runner, OpenRouter i governance gate.
- [ ] Dokument wskazuje lokalizację repo przez przenośną konwencję i komendy.
- [ ] Wyjaśnia, że token jest sekretem Actions/App, a nie plikiem repozytorium.
- [ ] Zawiera procedury instalacji, rotacji, incydentu i diagnostyki 401.
