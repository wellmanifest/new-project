# Preprompt & Wytyczne Techniczne (ticket-056)

- **Tytuł Zadania**: Report missing target prerequisites during adoption
- **Utworzono**: 2026-08-11T21:44:01Z

## Wymagania i Ograniczenia Techniczne

- Zachowaj `goal governance adopt` jako publiczny entrypoint; implementacja
  pozostaje w przypiętym `scripts/create_adoption_lock.py` pakietu standardu.
- Wyznacz braki względem stanu po zastosowaniu `payloads`, nie względem samego
  bieżącego drzewa targetu.
- Raportuj tylko target-owned `requiredFiles`; nie twórz ich i nie modyfikuj.
- Zachowaj kody `--check`: `0` dla pakietu up-to-date, `1` dla driftu.
- Dodaj regresje dla pustego targetu, plików zarządzanych przez payload,
  up-to-date z brakującym prerequisite oraz usunięcia ostrzeżenia po utworzeniu
  pliku przez właściciela targetu.
- Przestrzegaj odizolowanego środowiska Docker. `./project.sh` / `project.bat`
  uruchamia najpierw deterministyczny governance gate, a opcjonalną analizę
  wyłącznie przez obraz przypięty digestem SHA-256.

## Podlinkowane Zasoby i Dokumentacja Specyfikacji
- Dokumentacja Zarządcza Hub: https://github.com/wellmanifest/new-project
- Specyfikacja modułu: `scripts/create_adoption_lock.py`,
  `tests/adoption-lock.test.sh`, `docs/GOAL_ADOPTION.md`

## Dyrektywy Wykonawcze dla Agenta AI
- Odczytaj niniejsze wytyczne techniczne oraz istniejące, human-owned notatki
  z `user-{github_username}.md`. Nie twórz ani nie modyfikuj ich za człowieka.
- Na tej podstawie zbuduj specyfikację wykonawczą w pliku `ai-codex.md` (rozumienie intencji, zakres prac, koncepcja, Kryteria Odbioru).
- Przed pisaniem kodu zapisz plan w `ai-codex.md`, `TODO.md` i
  `intent.json`. Polecenie zlecające wykonanie lub tryb autonomiczny tworzy
  `SESSION_EXECUTION_AUTHORIZATION`; realizuj zapisany zakres bez ponownego
  pytania o tę samą zgodę (`P-CORE-008`).
- Osobnej władzy wymagają destrukcja, sekrety, nowa koordynacja zewnętrzna,
  materialnie nowy cel oraz trusted merge approval.
- Kod wykonywalny, testy i skrypty badawcze zapisuj poza katalogiem ticketu;
  ticket przechowuje wyłącznie governance, decyzje, logi i dowody.
