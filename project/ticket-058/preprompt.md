# Preprompt & Wytyczne Techniczne (ticket-058)

- **Tytuł Zadania**: Preserve colliding target root wrappers
- **Utworzono**: 2026-08-11T22:38:42Z

## Wymagania i Ograniczenia Techniczne

- Zmień wyłącznie strategie root `project.sh` i `project.bat` z `managed` na
  `seed`; nie osłabiaj `project/governance-check.*`.
- Udowodnij zachowanie istniejących bajtów i trybu bez `--upgrade`.
- Udowodnij utworzenie brakujących seedów oraz brak późniejszego driftu po ich
  legalnej lokalnej zmianie.
- Instrukcje targetu mają bezwarunkowo uruchamiać zarządzany
  `project/governance-check.*`, nie potencjalnie target-owned root wrapper.
- Nie implementuj parsera ani markerów sekcji dla dowolnych skryptów.
- Przestrzegaj odizolowanego środowiska Docker. `./project.sh` / `project.bat`
  uruchamia najpierw deterministyczny governance gate, a opcjonalną analizę
  wyłącznie przez obraz przypięty digestem SHA-256.

## Podlinkowane Zasoby i Dokumentacja Specyfikacji
- Dokumentacja Zarządcza Hub: https://github.com/wellmanifest/new-project
- Specyfikacja modułu: `governance/package-manifest.json`,
  `scripts/create_adoption_lock.py`, ticket 024, `docs/GOAL_ADOPTION.md`

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
