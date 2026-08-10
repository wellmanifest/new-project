# Preprompt & Wytyczne Techniczne (ticket-045)

- **Tytuł Zadania**: Govern publishing through Goal full workflow
- **Utworzono**: 2026-08-09T12:13:09Z

## Wymagania i Ograniczenia Techniczne
- Zachować `PULL_REQUEST_REQUIRED_FOR_IMPLEMENTATION` i zakaz bezpośredniego
  pushu implementacji na domyślną gałąź.
- Używać pełnego workflow `goal -a` z jawnym `--delivery-mode`.
- Dla publikacji implementacji wymagać `pull-request --no-publish`.
- Nie utożsamiać lokalnego hooka ani `.governance/delivery-events.jsonl` z
  autorytatywnym zatwierdzeniem.
- Nie opierać kompatybilności wyłącznie na numerze wersji Goal; wykonać
  feature probe dla `--delivery-mode`.
- Nie publikować pakietu, taga ani GitHub Release w tym ticketcie.
- Nie modyfikować repozytorium `semcod/goal` ani repozytoriów downstream.

## Podlinkowane Zasoby i Dokumentacja Specyfikacji
- Dokumentacja Zarządcza Hub: https://github.com/wellmanifest/new-project
- `semcod/goal/project/ticket-003/README.md`
- `semcod/goal/goal/governance/delivery.py`
- `CONTRIBUTING.md`, sekcja `PROCEDURA PUBLICATION`
- `docs/RELEASES.md`

## Dyrektywy Wykonawcze dla Agenta AI
- Odczytaj niniejsze wytyczne techniczne oraz istniejące, human-owned notatki
  z `user-{github_username}.md`. Nie twórz ani nie modyfikuj ich za człowieka.
- Na tej podstawie zbuduj specyfikację wykonawczą w pliku `ai-codex.md` (rozumienie intencji, zakres prac, koncepcja, Kryteria Odbioru).
- Przed pisaniem kodu przedstaw plan w `ai-codex.md` oraz w `TODO.md` do weryfikacji człowieka (`P-CORE-008`).
- Kod wykonywalny, testy i skrypty badawcze zapisuj poza katalogiem ticketu;
  ticket przechowuje wyłącznie governance, decyzje, logi i dowody.
- Zmień maksymalnie pięć plików implementacyjnych w dwóch odpowiedzialnościach.
- Nie dodawaj zależności runtime.
- Obejmij każdą nową stabilną regułę plikiem
  `governance/rule-enforcement.json`.
- Uruchom pełny hub test contract oraz `git diff --check`.
