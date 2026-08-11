# Preprompt & Wytyczne Techniczne (ticket-059)

- **Tytuł Zadania**: Recognize Compose-only Docker roots
- **Utworzono**: 2026-08-11T22:50:57Z

## Wymagania i Ograniczenia Techniczne

- Dodaj cztery konwencjonalne rootowe nazwy Compose do markera `docker`.
- Dodaj warianty `.yaml` do domyślnej listy plików Compose manifestu.
- Fixture dodatni ma używać nested Dockerfile zadeklarowanego jawnie w
  manifeście; fixture ujemny ma usunąć wszystkie rootowe markery.
- Nie stosuj rekurencyjnego globu ani automatycznego rozszerzania zaufania.
- Przestrzegaj odizolowanego środowiska Docker. `./project.sh` / `project.bat`
  uruchamia najpierw deterministyczny governance gate, a opcjonalną analizę
  wyłącznie przez obraz przypięty digestem SHA-256.

## Podlinkowane Zasoby i Dokumentacja Specyfikacji
- Dokumentacja Zarządcza Hub: https://github.com/wellmanifest/new-project
- Specyfikacja modułu: `governance/stack-profiles.json`,
  `governance/manifest.default.json`, `scripts/governance_check.py`

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
