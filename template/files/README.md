# Szablony Plików (`template/files/`)

Katalog ten zawiera znormalizowane szablony plików wykorzystywane podczas generowania struktury ticketu oraz menu w docelowych repozytoriach.

## Indeks Szablonów

| Plik Szablonu | Generowany Plik Docelowy | Przeznaczenie |
| :--- | :--- | :--- |
| **`project.template.md`** | `project/TICKETS.md` | Indeks ticketów bez przejmowania `project/README.md` generatora analizy. |
| **`human-participant.template.md`** | human-owned `project/ticket-{NNN}/user-{github_username}.md` | Jawnie typowane instrukcje i decyzje człowieka; agent nie generuje tego pliku. |
| **`agent-participant.template.md`** | `project/ticket-{NNN}/ai-{PROVIDER}.md` | Jawnie typowany plan, raport zmian i blokery agenta. |
| **`participant.template.md`** | nie jest generowany | Wskaźnik kompatybilności kierujący do szablonów zależnych od roli. |
| **`ticket.template.md`** | `project/ticket-{NNN}/README.md` | Ogólny szablon specyfikacji ticketu i zakresu prac. |
| **`preprompt.template.md`** | `project/ticket-{NNN}/preprompt.md` | Techniczne wytyczne ticketu, podlinkowane zasoby i ograniczenia inżynieryjne. |

## Zastosowanie

Skrypty automatyzujące (`new-ticket.sh`, `readme.sh`) odczytują niniejsze
szablony i podstawiają zmienne (`{PROVIDER}`, `{TICKET_ID}`, `{NNN}`,
`{TIMESTAMP}`) podczas generowania plików w katalogu `project/`. Generator nie
tworzy `user-*`; brak właściciela pozostaje jawny jako `unresolved:human`.
