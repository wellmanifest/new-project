# Preprompt & Wytyczne Techniczne (ticket-086)

- **Tytuł Zadania**: GOV-INTENT runbook and post-merge derive rules
- **Utworzono**: 2026-08-15T14:53:12Z

## Wymagania i Ograniczenia Techniczne
- Najpierw commit planu (`project/ticket-086/**`, `TODO.md`, `project/TICKETS.md`),
  potem osobny commit implementacji. Nie łączyć ich.
- Nie otwierać pull requesta. Nie force-pushować `main`. Nie scalać ticket-077.
- `acceptedBaseSha` musi być SHA `origin/main` (`ac8730a141ae15c7b087139565559c66906f8b74`).
- Maksymalnie 9 plików implementacyjnych i 3 komponenty.
- Runbook `error/GOV-INTENT.md` musi mieć sekcje Situation, Meaning, Safe
  resolution, Verification, Do not, Related rules.
- Nowe reguły Policy DSL w fenced `dsl` blocks. Mapowanie rule-enforcement
  kompletne; brakujące GOV-* oznacza `enforcement: manual` z powodem.
- Digest `CONTRIBUTING.md` w `dsl-manifest.json` wyprowadzić z pliku, nie
  zostawiać drugiej ręcznej kopii.

## Podlinkowane Zasoby i Dokumentacja Specyfikacji
- Dokumentacja Zarządcza Hub: https://github.com/wellmanifest/new-project
- Draft runbook: branch `gov-intent-runbook` commit `c01734d`
- Ticket-030 (derive required checks from one source)
- `error/README.md` (kontrakt runbooka)
- `docs/POLICY_DSL.md`

## Dyrektywy Wykonawcze dla Agenta AI
- Odczytaj niniejsze wytyczne techniczne oraz istniejące, human-owned notatki
  z `user-{github_username}.md`. Nie twórz ani nie modyfikuj ich za człowieka.
- Na tej podstawie zbuduj specyfikację wykonawczą w pliku `ai-grok.md`.
- Przed pisaniem kodu zapisz plan w `ai-grok.md`, `TODO.md` i
  `intent.json`. Polecenie zlecające wykonanie lub tryb autonomiczny tworzy
  `SESSION_EXECUTION_AUTHORIZATION`; realizuj zapisany zakres bez ponownego
  pytania o tę samą zgodę (`P-CORE-008`).
- Osobnej władzy wymagają destrukcja, sekrety, nowa koordynacja zewnętrzna
  oraz materialnie nowy cel. Publikacja na chroniony `main` nie należy do
  zakresu: wypchnij gałąź ticketu.
- Kod wykonywalny, testy i skrypty badawcze zapisuj poza katalogiem ticketu.
