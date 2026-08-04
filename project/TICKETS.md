# Indeks Ticketów (`project/TICKETS.md`)

- **Dokumentacja Zarządcza Hub**: [Governance Hub (`wellmanifest/new-project`)](https://github.com/wellmanifest/new-project)
- **Status Projektu**: AKTYWNY
- **Ostatnia Aktualizacja**: 2026-08-04T12:14:00Z

## Opis Katalogu

Katalog `project/` służy do zarządzania cyklem życia ticketów utrzymaniowych
standardu `wellmanifest/new-project`. Tickety systemów docelowych pozostają w
ich własnych repozytoriach. Osobny `TICKETS.md` nie przejmuje
`project/README.md`, który może należeć do generatora analizy technicznej.

---

## Indeks Ticketów i Uczestników

<!-- AUTO:TICKET_INDEX:START -->
| Ticket ID | Spec | Preprompt | Human input | Agent plans | Agent logs | Changelog |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ticket-001** | [`README.md`](./ticket-001/README.md) | [`preprompt.md`](./ticket-001/preprompt.md) | - |  [`ai-codex.md`](./ticket-001/ai-codex.md) |  [`ai-codex-logs.txt`](./ticket-001/ai-codex-logs.txt) | [`changelog.md`](./ticket-001/changelog.md) |
| **ticket-002** | [`README.md`](./ticket-002/README.md) | [`preprompt.md`](./ticket-002/preprompt.md) | - |  [`ai-codex.md`](./ticket-002/ai-codex.md) |  [`ai-codex-logs.txt`](./ticket-002/ai-codex-logs.txt) | [`changelog.md`](./ticket-002/changelog.md) |
<!-- AUTO:TICKET_INDEX:END -->

---

## Instrukcja Obsługi

- **Tworzenie nowego ticketu**:
  ```bash
  ./project/new-ticket.sh --title "Nazwa Zadania" --workstream "application"
  ```
- **Aktualizacja indeksu w project/TICKETS.md**:
  ```bash
  ./project/readme.sh
  ```
