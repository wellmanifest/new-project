# Preprompt & Wytyczne Techniczne (ticket-001)

- **Tytuł Zadania**: Utrzymanie i rozwój standardu new-project
- **Utworzono**: 2026-08-04T12:14:00Z

## Wymagania i Ograniczenia Techniczne

- Zmień wyłącznie dokumenty wskazane przez `intent.json`.
- Nie używaj docelowego `project.sh` jako gate'a repozytorium standardu;
  weryfikuj utrzymanie huba zgodnie z jego własnym kontraktem CI.
- Zachowaj odrębność ticketów huba i ticketów systemów docelowych.

## Podlinkowane Zasoby i Dokumentacja Specyfikacji
- Dokumentacja Zarządcza Hub: https://github.com/wellmanifest/new-project
- Specyfikacja: `AGENTS.md`, `POLICY.md`, `CONTRIBUTING.md` i polecenie
  użytkownika z 2026-08-04.

## Dyrektywy Wykonawcze dla Agenta AI
- Odczytaj niniejsze wytyczne techniczne oraz istniejące, human-owned notatki
  z `user-{github_username}.md`. Nie twórz ani nie modyfikuj ich za człowieka.
- Na tej podstawie zbuduj specyfikację wykonawczą w pliku `ai-codex.md` (rozumienie intencji, zakres prac, koncepcja, Kryteria Odbioru).
- Przed pisaniem kodu przedstaw plan w `ai-codex.md` oraz w `TODO.md` do weryfikacji człowieka (`P-CORE-008`).
- Kod wykonywalny, testy i skrypty badawcze zapisuj poza katalogiem ticketu;
  ticket przechowuje wyłącznie governance, decyzje, logi i dowody.
