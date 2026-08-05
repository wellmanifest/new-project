# Preprompt & Wytyczne Techniczne (ticket-026)

- **Tytuł Zadania**: Egzekwowalne pokrycie reguł CONTRIBUTING w runtime i CI huba
- **Utworzono**: 2026-08-05T12:14:51Z

## Wymagania i Ograniczenia Techniczne

- Nie twórz wykonywalnego, ogólnego interpretera dowolnych poleceń DSL.
- Użyj zamkniętego rejestru adapterów; żadnego `eval`, dynamicznej powłoki ani
  komend pochodzących z JSON.
- Porównuj reguły z rejestru z ID wyekstrahowanymi z bieżącego
  `CONTRIBUTING.md`.
- Rozróżniaj egzekwowanie lokalne, chroniony workflow/API GitHub, decyzję
  człowieka i procedurę agenta.
- Nie oznaczaj `FULL`, jeśli egzekutor albo test nie istnieje.
- Zachowaj LLM jako advisory; konfiguracja Validatora pozostaje
  `openrouter/z-ai/glm-5.2`.
- Nie wchodź w pliki ticketów 023/025 ani w ich aktywny zakres.

## Podlinkowane Zasoby i Dokumentacja Specyfikacji
- Dokumentacja Zarządcza Hub: https://github.com/wellmanifest/new-project
- Runtime: [`scripts/runtime.sh`](../../scripts/runtime.sh)
- Procedura: [`CONTRIBUTING.md`](../../CONTRIBUTING.md)
- Walidator governance: [`scripts/governance_check.py`](../../scripts/governance_check.py)
- CI huba: [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)

## Dyrektywy Wykonawcze dla Agenta AI
- Odczytaj niniejsze wytyczne techniczne oraz istniejące, human-owned notatki
  z `user-{github_username}.md`. Nie twórz ani nie modyfikuj ich za człowieka.
- Na tej podstawie zbuduj specyfikację wykonawczą w pliku `ai-codex.md` (rozumienie intencji, zakres prac, koncepcja, Kryteria Odbioru).
- Przed pisaniem kodu przedstaw plan w `ai-codex.md` oraz w `TODO.md` do weryfikacji człowieka (`P-CORE-008`).
- Kod wykonywalny, testy i skrypty badawcze zapisuj poza katalogiem ticketu;
  ticket przechowuje wyłącznie governance, decyzje, logi i dowody.
