# Preprompt & Wytyczne Techniczne (ticket-067)

- **Tytuł Zadania**: Diagnostic remediation intent DSL and todo2code analysis
- **Utworzono**: 2026-08-12T10:56:12Z

## Wymagania i Ograniczenia Techniczne
- Zaimplementuj wymagania zgodnie z opisaną architekturą projektu.
- Przestrzegaj odizolowanego środowiska Docker. `./project.sh` / `project.bat`
  uruchamia najpierw deterministyczny governance gate, a opcjonalną analizę
  wyłącznie przez obraz przypięty digestem SHA-256.

## Podlinkowane Zasoby i Dokumentacja Specyfikacji
- Dokumentacja Zarządcza Hub: https://github.com/wellmanifest/new-project
- Kanoniczna diagnostyka: `governance/diagnostics.json`, `error/*.md`
- Ocena zmian: `governance/change-evaluation.schema.json`
- Todo2code code-change plans: `t2c.code-change-plan/v1`
- Specyfikacja modułu: {Wpisz odnośnik do dokumentacji technicznej lub pliku}

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
- Nie zapisuj raportu ani ticketu Diagit w tym hubie. Fixture ma być
  zanonimizowanym testem kontraktu, a rzeczywista instancja DSL należy do
  repozytorium docelowego.
- Traktuj LLM i todo2code jako źródła advisory. Deterministyczny validator,
  zaakceptowany intent i governance gate pozostają authority.
