# Preprompt & Wytyczne Techniczne (ticket-055)

- **Tytuł Zadania**: Resolve default base for multi-commit initial adoption
- **Utworzono**: 2026-08-11T21:02:40Z

## Wymagania i Ograniczenia Techniczne
- Zachowaj `goal governance check` jako jedyny wrapper uruchomieniowy; reguły i
  resolver bazy pozostają w przypiętym pakiecie `new-project`.
- Traktuj jawne `--base` jako nadrzędne. Automatycznie wybieraj bazę wyłącznie
  dla dokładnie jednego aktywnego ticketu z `delivery.standardAdoption`.
- Dodaj regresję z osobnym commitem planu pomiędzy zaakceptowaną bazą a commitem
  adopcji. Test bez `--base` musi ocenić pełny diff i zmieniony lock.
- Nie rozszerzaj tej zmiany na ogólne zgadywanie bazy zwykłych ticketów.
- Przestrzegaj odizolowanego środowiska Docker. `./project.sh` / `project.bat`
  uruchamia najpierw deterministyczny governance gate, a opcjonalną analizę
  wyłącznie przez obraz przypięty digestem SHA-256.

## Podlinkowane Zasoby i Dokumentacja Specyfikacji
- Dokumentacja Zarządcza Hub: https://github.com/wellmanifest/new-project
- Specyfikacja modułu: `scripts/governance_check.py`,
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
