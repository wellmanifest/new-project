# Instrukcje dla agentów AI

Ten plik jest punktem wejścia. Szczegółowa, repozytoryjna instrukcja operacyjna znajduje się w `GPT56Luna/CONTRIBUTING.md`.

## Kolejność czytania

Przed zmianą agent MUSI przeczytać:

1. `GPT56Luna/CONTRIBUTING.md` — aktualny przepływ pracy i potwierdzone możliwości repozytorium,
2. `README.md` — ogólny standard pracy,
3. `POLICY.md` — polityki projektu,
4. `docs/README.md` — indeks dokumentacji,
5. `project.sh` — jeżeli zadanie dotyczy skryptu, instalacji lub narzędzi,
6. `TODO.md` — jeżeli plik istnieje.

## Najważniejsze zasady

- Najpierw sprawdź aktualne pliki, skrypty, workflow i historię Git; nie zakładaj istnienia funkcji na podstawie samej nazwy.
- Rozróżniaj komendy aktywne i zakomentowane w `project.sh`.
- Nie opisuj jako dostępnych testów, agentów, CI, Dockera ani aplikacji elementów, których nie potwierdzono w repozytorium.
- Dla większych zadań zapisz plan, ryzyka i kryteria akceptacji w `TODO.md`.
- Po zmianie sprawdź odwołania, diff i sekrety oraz opisz wykonane kontrole.
- Nie uruchamiaj destrukcyjnych ani nadpisujących operacji bez sprawdzenia skutków.

## Aktualny zakres repozytorium

Repozytorium zawiera standardy dokumentacyjne, polityki i skrypt analityczny. Aktualnie nie znaleziono aplikacji, `src/`, `tests/`, CI ani Dockera. Nie wolno przedstawiać ich jako gotowych elementów projektu.

## Źródła prawdy

- `GPT56Luna/CONTRIBUTING.md` — instrukcja operacyjna,
- `GPT56Luna/ANALIZA-DOKUMENTACJI.md` — analiza luk, decyzji i historii,
- `README.md` — ogólny standard,
- `POLICY.md` — polityki,
- `docs/README.md` — indeks,
- `project.sh` — rzeczywisty skrypt.

Jeżeli dokumentacja i aktualny plik są sprzeczne, agent zgłasza rozbieżność i opiera działanie na aktualnym, potwierdzonym stanie repozytorium.