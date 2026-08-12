# Preprompt & Wytyczne Techniczne (ticket-073)

- **Tytuł Zadania**: Make remediation intent projections atomic and analyzable
- **Utworzono**: 2026-08-12T17:16:10Z

## Wymagania i Ograniczenia Techniczne
- Zaimplementuj wymagania zgodnie z opisaną architekturą projektu.
- Przestrzegaj odizolowanego środowiska Docker. `./project.sh` / `project.bat`
  uruchamia najpierw deterministyczny governance gate, a opcjonalną analizę
  wyłącznie przez obraz przypięty digestem SHA-256.

## Podlinkowane Zasoby i Dokumentacja Specyfikacji
- Dokumentacja Zarządcza Hub: https://github.com/wellmanifest/new-project
- Specyfikacja modułu: `docs/DIAGNOSTIC_REMEDIATION_DSL.md`
- Poprzedni kontrakt: `project/ticket-067/`
- Regresja produkcyjna: target-owned dowody `semcod/goal`, `ticket-055`

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
- Zachowaj todo2code jako opcjonalne, zewnętrzne narzędzie analizy. Adapter ma
  działać bez nowej zależności runtime i korelować artefakty przez record IDs.
- Jedna akcja DSL ma dawać jeden kompletny rekord intencji w projekcji; tekst
  pomocniczy nie może stać się anonimowym wymaganiem.
