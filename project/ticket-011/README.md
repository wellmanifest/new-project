# Ticket 011: Windows CI dla wrapperów i generatora

- **ID**: ticket-011
- **Owner**: unresolved:human
- **Status**: BACKLOG
- **Workflow state**: BACKLOG
- **Utworzono**: 2026-08-04

## Cel i zakres

Dodać rzeczywiste Windows CI dla `project.bat`, wrappera governance i
generatora adopcji, bez traktowania linuksowych fixture'ów jako dowodu
zgodności Windows.

## Kryteria odbioru

- [ ] Workflow uruchamia się na chronionym Windows runnerze.
- [ ] Wrappery `.bat` przechodzą ścieżkę pozytywną i fail-closed.
- [ ] Generator zachowuje atomowość i poprawne ścieżki na Windows.
- [ ] Status Windows jest wymagany przed kolejnym wydaniem.
