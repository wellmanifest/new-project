# Preprompt & Wytyczne Techniczne (ticket-097)

- **Tytuł Zadania**: Repair previously unreachable worktree hook chains
- **Utworzono**: 2026-08-20T23:08:14Z

## Wymagania i Ograniczenia Techniczne
- Zaimplementuj wymagania zgodnie z opisaną architekturą projektu.
- Przestrzegaj odizolowanego środowiska Docker. `./project.sh` / `project.bat`
  uruchamia najpierw deterministyczny governance gate, a opcjonalną analizę
  wyłącznie przez obraz przypięty digestem SHA-256.

## Podlinkowane Zasoby i Dokumentacja Specyfikacji
- Dokumentacja Zarządcza Hub: https://github.com/wellmanifest/new-project
- Installer: `scripts/install-worktree-guard.sh`
- Regression suite: `tests/worktree-overlap.test.sh`
- Predecessor: `project/ticket-096/README.md`

## Dyrektywy Wykonawcze dla Agenta AI
- Odczytaj niniejsze wytyczne techniczne oraz istniejące, human-owned notatki
  z `user-{github_username}.md`. Nie twórz ani nie modyfikuj ich za człowieka.
- Na tej podstawie zbuduj specyfikację wykonawczą w pliku `ai-codex.md` (rozumienie intencji, zakres prac, koncepcja, Kryteria Odbioru).
- Przed pisaniem kodu zapisz plan w `ai-codex.md`, `TODO.md` i
  `intent.json`. Polecenie zlecające wykonanie lub tryb autonomiczny tworzy
  `SESSION_EXECUTION_AUTHORIZATION`; realizuj zapisany zakres bez ponownego
  pytania o tę samą zgodę (`P-CORE-008`).
- Osobnej władzy wymagają destrukcja, sekrety, nowa koordynacja zewnętrzna
  oraz materialnie nowy cel. Jeżeli zapisany outcome obejmuje publikację,
  autoryzacja sesji pozwala uruchomić zadeklarowany chroniony proces dostawy i
  jego merge po exact-head trusted approval bez ponownego pytania. Sama
  autoryzacja sesji nigdy nie jest approval evidence, a agent nie scala
  bezpośrednio.
- Kod wykonywalny, testy i skrypty badawcze zapisuj poza katalogiem ticketu;
  ticket przechowuje wyłącznie governance, decyzje, logi i dowody.
