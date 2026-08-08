# Preprompt & Wytyczne Techniczne (ticket-036)

- **Tytuł Zadania**: Own root release and environment contracts
- **Utworzono**: 2026-08-08T12:18:40Z

## Wymagania i Ograniczenia Techniczne
- Dodaj wyłącznie dokładne ścieżki `CHANGELOG.md` i `.env.example` do
  `governance.ownedPaths` w domyślnym manifeście.
- Nie zmieniaj `VERSION`, głównego `CHANGELOG.md`, runtime walidatora ani
  package-manifestu.
- Dodaj pozytywne i negatywne fixture'y do istniejących testów Bash.
- Negatywny przypadek musi asertywnie wymagać `GOV-WORKSTREAM-003`.
- Uruchom pełny hub test contract przed publikacją PR.

## Podlinkowane Zasoby i Dokumentacja Specyfikacji
- Dokumentacja Zarządcza Hub: https://github.com/wellmanifest/new-project
- Domyślny manifest: `governance/manifest.default.json`
- Walidacja: `tests/governance-validator.test.sh`
- Adopcja: `tests/adoption-lock.test.sh`

## Dyrektywy Wykonawcze dla Agenta AI
- Odczytaj niniejsze wytyczne techniczne oraz istniejące, human-owned notatki
  z `user-{github_username}.md`. Nie twórz ani nie modyfikuj ich za człowieka.
- Na tej podstawie zbuduj specyfikację wykonawczą w pliku `ai-codex.md` (rozumienie intencji, zakres prac, koncepcja, Kryteria Odbioru).
- Przed pisaniem kodu przedstaw plan w `ai-codex.md` oraz w `TODO.md` do weryfikacji człowieka (`P-CORE-008`).
- Kod wykonywalny, testy i skrypty badawcze zapisuj poza katalogiem ticketu;
  ticket przechowuje wyłącznie governance, decyzje, logi i dowody.
