# Ticket 011: Windows CI dla wrapperów i generatora

- **ID**: ticket-011
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-04

## Cel i zakres

Dodać rzeczywiste Windows CI dla `project.bat`, wrappera governance i
generatora adopcji, bez traktowania linuksowych fixture'ów jako dowodu
zgodności Windows.

## Kryteria odbioru

Implementacja jest gotowa do walidacji na chronionym runnerze `windows-latest`.
Status `DONE` wymaga pozytywnego wyniku joba `windows-governance` dla dokładnego
SHA PR oraz zaufanego approval.

- [x] Workflow uruchamia się na chronionym Windows runnerze.
- [x] Wrappery `.bat` przechodzą ścieżkę pozytywną i fail-closed.
- [x] Generator zachowuje atomowość i poprawne ścieżki na Windows.
- [x] Status Windows jest wymagany przez aktywny ruleset gałęzi `main`.

## Dowody zakończenia

- PR #11 został scalony dla dokładnego SHA
  `62bf340e2219a38bbf9a0fe5379842c8af4d50ab`.
- Exact-head review aplikacji `ifuri-validator-agent` ma stan `APPROVED`.
- Checki `test` i `windows-governance` zakończyły się `SUCCESS`.
- Aktywny ruleset `main-governance-protection` wymaga checku
  `windows-governance` przed merge.
