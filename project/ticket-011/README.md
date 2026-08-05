# Ticket 011: Windows CI dla wrapperów i generatora

- **ID**: ticket-011
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-04

## Cel i zakres

Dodać rzeczywiste Windows CI dla `project.bat`, wrappera governance i
generatora adopcji, bez traktowania linuksowych fixture'ów jako dowodu
zgodności Windows.

## Kryteria odbioru

Implementacja jest gotowa do walidacji na chronionym runnerze `windows-latest`.
Status `DONE` wymaga pozytywnego wyniku joba `windows-governance` dla dokładnego
SHA PR oraz zaufanego approval.

- [ ] Workflow uruchamia się na chronionym Windows runnerze.
- [ ] Wrappery `.bat` przechodzą ścieżkę pozytywną i fail-closed.
- [ ] Generator zachowuje atomowość i poprawne ścieżki na Windows.
- [ ] Status Windows jest wymagany przed kolejnym wydaniem.
