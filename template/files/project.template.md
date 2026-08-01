# Indeks Ticketów (`project/TICKETS.md`)

- **Dokumentacja Zarządcza Hub**: [Governance Hub (`wellmanifest/new-project`)](https://github.com/wellmanifest/new-project)
- **Status Projektu**: AKTYWNY
- **Ostatnia Aktualizacja**: {TIMESTAMP}

## Opis Katalogu

Katalog `project/` służy do zarządzania cyklem życia ticketów i procedurami
zarządczymi w repozytorium docelowym. Osobny `TICKETS.md` nie przejmuje
`project/README.md`, który może należeć do generatora analizy technicznej.

---

## Indeks Ticketów i Uczestników

<!-- AUTO:TICKET_INDEX:START -->
*(Tabela indeksu ticketów generowana automatycznie przez skrypt `./project/readme.sh`)*
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
