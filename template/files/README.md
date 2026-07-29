# Szablony Plików (`template/files/`)

Katalog ten zawiera znormalizowane szablony plików wykorzystywane podczas generowania struktury ticketu w docelowych repozytoriach.

## Indeks Szablonów

| Plik Szablonu | Generowany Plik Docelowy | Przeznaczenie |
| :--- | :--- | :--- |
| **`participant.template.md`** | `user-{NAME}.md` | Notatki człowieka, instrukcje i stały kontekst zapytania. |
| **`ticket.template.md`** | `project/ticket-{NNN}/README.md` | Ogólny szablon specyfikacji ticketu i zakresu prac. |

## Zastosowanie

Skrypty automatyzujące (`new-ticket.sh` / `new-ticket.bat`) odczytują niniejsze szablony i podstawiają zmienne (`{NAME}`, `{PROVIDER}`, `{NNN}`) podczas generowania plików w katalogu `project/ticket-{NNN}/`.
