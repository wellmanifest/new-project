# Preprompt & Wytyczne Techniczne (ticket-046)

- **Tytuł Zadania**: Migrate locked manifests and authorize bounded autonomy
- **Utworzono**: 2026-08-10T07:29:46Z

## Wymagania i Ograniczenia Techniczne
- Zaimplementuj wymagania zgodnie z opisaną architekturą projektu.
- Przestrzegaj odizolowanego środowiska Docker. `./project.sh` / `project.bat`
  uruchamia najpierw deterministyczny governance gate, a opcjonalną analizę
  wyłącznie przez obraz przypięty digestem SHA-256.

## Podlinkowane Zasoby i Dokumentacja Specyfikacji
- Dokumentacja Zarządcza Hub: https://github.com/wellmanifest/new-project
- Specyfikacja modułu: {Wpisz odnośnik do dokumentacji technicznej lub pliku}
- Migrator: `scripts/create_adoption_lock.py`
- Regresje: `tests/adoption-lock.test.sh`
- Poprzedni kontrakt `extendable`: `project/ticket-024/`

## Dyrektywy Wykonawcze dla Agenta AI
- Odczytaj niniejsze wytyczne techniczne oraz istniejące, human-owned notatki
  z `user-{github_username}.md`. Nie twórz ani nie modyfikuj ich za człowieka.
- Na tej podstawie zbuduj specyfikację wykonawczą w pliku `ai-codex.md` (rozumienie intencji, zakres prac, koncepcja, Kryteria Odbioru).
- Przed pisaniem kodu zapisz plan w `ai-codex.md`, `TODO.md` i `intent.json`.
  Jeżeli polecenie użytkownika już zleca wykonanie lub tryb autonomiczny,
  zapisz `SESSION_EXECUTION_AUTHORIZATION` i nie pytaj ponownie o tę samą zgodę.
- Nie wyprowadzaj z tej zgody uprawnienia do destrukcji, sekretów, materialnie
  nowego celu, force-push ani trusted merge approval.
- Kod wykonywalny, testy i skrypty badawcze zapisuj poza katalogiem ticketu;
  ticket przechowuje wyłącznie governance, decyzje, logi i dowody.
- Traktuj istniejący legacy target manifest jako bazę tylko po weryfikacji jego
  dokładnego SHA-256 z lockiem. Nie pobieraj ruchomej referencji i nie twórz
  częściowego stanu przy błędzie.
