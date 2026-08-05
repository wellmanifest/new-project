---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-018
---
# Participant: codex (AI agent)

## Understanding

Istniejący Pythonowy governance runtime nie sprawdza stanu repozytorium GitHub.
`todo2code` potrafi bezpiecznie analizować lokalny worktree i dostarczone refy,
ale nie enumeruje GitHub PR-ów ani nie sprawdza `delete_branch_on_merge`.
Brakujący element to mały adapter evidence acquisition w chronionym workflow
oraz deterministyczny walidator zamkniętego snapshotu.

## Execution plan

1. Dodać `scripts/branch_lifecycle_check.py` z zamkniętym kontraktem wejścia,
   stabilnymi diagnostics i raportem tekstowym/JSON.
2. Rozszerzyć reusable `.github/workflows/governance.yml` o pobranie metadata,
   branchy i otwartych PR-ów przez przypięty `actions/github-script`.
3. Dodać pozytywne, negatywne, forkowe i malformed fixture w
   `tests/branch-lifecycle.test.sh`.
4. Utrzymać zamknięty katalog kodów w module bez naruszania centralnego
   rejestru należącego wyłącznie do `governance_check.py`.
5. Podłączyć test do `.github/workflows/ci.yml` i uruchomić pełny kontrakt huba.

## Actual changes

- Dodano ścisły `branch-lifecycle-snapshot/v1` i deterministyczny raport z
  kodami `GOV-BRANCH-LIFECYCLE-001..003`.
- Reusable workflow pobiera read-only metadata repozytorium, branche i otwarte
  PR-y, po czym przekazuje ephemeral snapshot do walidatora bez sieci.
- Fixture pokrywają stan spoczynku, wewnętrzny i forkowy PR, wyłączone
  auto-delete, branch osierocony, brak heada oraz nieznane pola.
- Test 018 jest częścią Linux CI; wszystkie lokalnie dostępne zestawy przeszły.
- Centralny `diagnostics.json` pozostał bez zmian, ponieważ jego meta-kontrakt
  obejmuje wyłącznie kody emitowane przez `governance_check.py`.

## Blockers

- Brak. Ticket 017 jest `DONE / DONE`, a użytkownik zatwierdził ticket 018.

## Architecture before implementation

- `github-evidence-acquisition`: workflow ma token read-only i zapisuje JSON do
  `runner.temp`; nie podejmuje decyzji oraz nie usuwa branchy.
- `deterministic-lifecycle-validator`: czysty Python standard library sprawdza
  kontrakt i generuje stabilne diagnostics.
- `todo2code` nie jest wymaganym komponentem. Jego obecny workspace preflight i
  branch portfolio pozostają warstwą lokalnej/semantycznej analizy advisory.
