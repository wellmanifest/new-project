# Preprompt & Wytyczne Techniczne (ticket-018)

- **Tytuł Zadania**: Deterministyczny audyt lifecycle branchy GitHub
- **Utworzono**: 2026-08-05T10:15:56Z

## Wymagania i Ograniczenia Techniczne
- Oddziel akwizycję faktów GitHub od deterministycznej walidacji snapshotu.
- Skrypt nie może wywoływać `gh`, GitHub API, Git ani LLM.
- Snapshot ma mieć ścisły, wersjonowany kontrakt i bounded arrays.
- Nie usuwaj branchy; emituj stabilne diagnostics oraz remediacje.
- Uwzględnij heady otwartych PR-ów tylko z repozytorium bazowego.
- Zachowaj required gate niezależny od `todo2code`; jego branch portfolio może
  być później dowodem advisory dla semantycznych duplikatów.

## Podlinkowane Zasoby i Dokumentacja Specyfikacji
- Dokumentacja Zarządcza Hub: https://github.com/wellmanifest/new-project
- Reusable workflow: `.github/workflows/governance.yml`
- Runtime governance: `scripts/governance_check.py`
- Lokalna analiza branchy: `semcod/todo2code/src/core/branch-portfolio.ts`

## Dyrektywy Wykonawcze dla Agenta AI
- Odczytaj niniejsze wytyczne techniczne oraz istniejące, human-owned notatki
  z `user-{github_username}.md`. Nie twórz ani nie modyfikuj ich za człowieka.
- Na tej podstawie zbuduj specyfikację wykonawczą w pliku `ai-codex.md` (rozumienie intencji, zakres prac, koncepcja, Kryteria Odbioru).
- Przed pisaniem kodu przedstaw plan w `ai-codex.md` oraz w `TODO.md` do weryfikacji człowieka (`P-CORE-008`).
- Kod wykonywalny, testy i skrypty badawcze zapisuj poza katalogiem ticketu;
  ticket przechowuje wyłącznie governance, decyzje, logi i dowody.
