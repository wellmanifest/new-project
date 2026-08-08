# Preprompt & Wytyczne Techniczne (ticket-037)

- **Tytuł Zadania**: Publish immutable 0.12.0
- **Utworzono**: 2026-08-08T12:34:57Z

## Wymagania i Ograniczenia Techniczne
- Ujednolić `0.12.0` wyłącznie w pięciu dozwolonych plikach release'u.
- Nie zmieniać semantyki manifestu poza numerem wersji.
- Przed i po merge uruchomić pełny Linux CI contract.
- Zweryfikować brak istniejącego `v0.12.0` i Release przed publikacją.
- Utworzyć wyłącznie nowy annotowany tag dla przetestowanego merge SHA.
- Nigdy nie używać force-update taga ani istniejącego Release.

## Podlinkowane Zasoby i Dokumentacja Specyfikacji
- Dokumentacja Zarządcza Hub: https://github.com/wellmanifest/new-project
- Zmiana źródłowa: `project/ticket-036/README.md`
- Manifest: `governance/manifest.default.json`
- Testy: `tests/governance-validator.test.sh`, `tests/adoption-lock.test.sh`

## Dyrektywy Wykonawcze dla Agenta AI
- Odczytaj niniejsze wytyczne techniczne oraz istniejące, human-owned notatki
  z `user-{github_username}.md`. Nie twórz ani nie modyfikuj ich za człowieka.
- Na tej podstawie zbuduj specyfikację wykonawczą w pliku `ai-codex.md` (rozumienie intencji, zakres prac, koncepcja, Kryteria Odbioru).
- Przed pisaniem kodu przedstaw plan w `ai-codex.md` oraz w `TODO.md` do weryfikacji człowieka (`P-CORE-008`).
- Kod wykonywalny, testy i skrypty badawcze zapisuj poza katalogiem ticketu;
  ticket przechowuje wyłącznie governance, decyzje, logi i dowody.
