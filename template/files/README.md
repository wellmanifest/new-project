# Szablony Plików (`template/files/`)

Katalog ten zawiera znormalizowane szablony plików wykorzystywane podczas generowania struktury ticketu oraz menu w docelowych repozytoriach.

## Indeks Szablonów

| Plik Szablonu | Generowany Plik Docelowy | Przeznaczenie |
| :--- | :--- | :--- |
| **`project.template.md`** | `project/README.md` | Master Menu i spis ticketów w katalogu `project/`. |
| **`participant.template.md`** | `project/ticket-{NNN}/user-{github_username}.md` | Notatki człowieka, instrukcje i stały kontekst zapytania. |
| **`ticket.template.md`** | `project/ticket-{NNN}/preprompt.md` | Techniczne wytyczne ticketu i ramowy plan specyfikacji. |

## Zastosowanie

Skrypty automatyzujące (`new-ticket.sh`, `readme.sh`) odczytują niniejsze szablony i podstawiają zmienne (`{NAME}`, `{PROVIDER}`, `{NNN}`) podczas generowania plików w katalogu `project/`.
