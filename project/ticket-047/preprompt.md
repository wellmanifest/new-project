# Preprompt & Wytyczne Techniczne (ticket-047)

- **Tytuł Zadania**: Publish bounded autonomy migration fix
- **Utworzono**: 2026-08-10T08:26:19Z

## Wymagania i Ograniczenia Techniczne
- Zaimplementuj wymagania zgodnie z opisaną architekturą projektu.
- Przestrzegaj odizolowanego środowiska Docker. `./project.sh` / `project.bat`
  uruchamia najpierw deterministyczny governance gate, a opcjonalną analizę
  wyłącznie przez obraz przypięty digestem SHA-256.

## Podlinkowane Zasoby i Dokumentacja Specyfikacji
- Dokumentacja Zarządcza Hub: https://github.com/wellmanifest/new-project
- Generator ticketów: `project/new-ticket.sh`, `template/files/*.template.md`
- Naprawa bazowa: `project/ticket-046/`
- Poprzednie wydanie: `project/ticket-044/`

## Dyrektywy Wykonawcze dla Agenta AI
- Odczytaj niniejsze wytyczne techniczne oraz istniejące, human-owned notatki
  z `user-{github_username}.md`. Nie twórz ani nie modyfikuj ich za człowieka.
- Na tej podstawie zbuduj specyfikację wykonawczą w pliku `ai-codex.md` (rozumienie intencji, zakres prac, koncepcja, Kryteria Odbioru).
- Przed pisaniem kodu zapisz plan, intent i bounded session authorization.
  Bieżące polecenie wykonania/autonomii nie wymaga osobnego potwierdzenia.
- Nie traktuj session authorization jako zgody na destrukcję, sekrety,
  materialnie nowy cel ani trusted merge/release approval.
- Kod wykonywalny, testy i skrypty badawcze zapisuj poza katalogiem ticketu;
  ticket przechowuje wyłącznie governance, decyzje, logi i dowody.
