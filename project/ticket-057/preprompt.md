# Preprompt & Wytyczne Techniczne (ticket-057)

- **Tytuł Zadania**: Own VERSION in stackless repositories
- **Utworzono**: 2026-08-11T22:26:38Z

## Wymagania i Ograniczenia Techniczne

- Dodaj dokładną ścieżkę `VERSION` do `integration.ownedPaths` w domyślnym
  manifeście; nie rozszerzaj globów ani uprawnień innych workstreamów.
- Dodaj pozytywny fixture dla `integration` i negatywny dla `application`.
- Użyj bazowego profilu `stacks: []`; nie uzależniaj naprawy od profilu
  językowego.
- Nie twórz ani nie modyfikuj plików target-owned w downstream repozytoriach.
- Nie zmieniaj Goal, schematów, zależności ani wersji pakietu.
- Przestrzegaj odizolowanego środowiska Docker. `./project.sh` / `project.bat`
  uruchamia najpierw deterministyczny governance gate, a opcjonalną analizę
  wyłącznie przez obraz przypięty digestem SHA-256.

## Podlinkowane Zasoby i Dokumentacja Specyfikacji
- Dokumentacja Zarządcza Hub: https://github.com/wellmanifest/new-project
- Specyfikacja modułu: `governance/manifest.default.json`,
  `tests/governance-validator.test.sh`

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
