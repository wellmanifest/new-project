# Preprompt & Wytyczne Techniczne (ticket-060)

- **Tytuł Zadania**: Upgrade reusable workflows to Node 24 actions
- **Utworzono**: 2026-08-12T00:09:38Z

## Wymagania i Ograniczenia Techniczne

- Zastąp wyłącznie piny akcji należące do dwóch workflow standardu.
- Użyj pełnych, zweryfikowanych SHA oficjalnych tagów Node.js 24 i zachowaj
  komentarze wersji obok pinów.
- Nie zmieniaj zdarzeń, permissions, warunków, skryptów GitHub API ani wejść
  reusable workflow.
- Uruchom pełny test contract huba oraz rzeczywiste Linux/Windows Check Runs.

## Podlinkowane Zasoby i Dokumentacja Specyfikacji
- Dokumentacja Zarządcza Hub: https://github.com/wellmanifest/new-project
- Workflow lokalny: `.github/workflows/ci.yml`
- Workflow reusable: `.github/workflows/governance.yml`
- Oficjalne wydania akcji: repozytoria `actions/checkout`,
  `actions/setup-python` i `actions/github-script`.

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
