# Preprompt & Wytyczne Techniczne (ticket-081)

- **Tytuł Zadania**: Adopt Policy DSL v1 for CONTRIBUTING
- **Utworzono**: 2026-08-14T17:35:26Z

## Wymagania i Ograniczenia Techniczne
- Zaimplementuj wymagania zgodnie z opisaną architekturą projektu.
- Przestrzegaj odizolowanego środowiska Docker. `./project.sh` / `project.bat`
  uruchamia najpierw deterministyczny governance gate, a opcjonalną analizę
  wyłącznie przez obraz przypięty digestem SHA-256.

## Podlinkowane Zasoby i Dokumentacja Specyfikacji
- Dokumentacja Zarządcza Hub: https://github.com/wellmanifest/new-project
- Specyfikacja modułu: `wellmanifest/policy-dsl/spec/POLICY_DSL.md`
- Standard manifestu: `wellmanifest/dsl/spec/DSL_STANDARD.md`
- Kontekst środowiska: `wellmanifest/env-dsl/spec/ENV_DSL.md`
- Granica efektów: `wellmanifest/poa/standard/poa-process.schema.v1.json`

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
