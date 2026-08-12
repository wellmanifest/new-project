# Ticket changelog (ticket-063)

## [0.1.0] - 2026-08-12

- Zapisano przyczynę pozostawania lokalnych worktree/klonów i lukę instalacji
  zdalnego enforcementu.
- Zweryfikowano oraz uprzątnięto 26 artefaktów pilotów `new-project` bez utraty
  kodu produktu.
- Dodano deterministyczny audyt dodatkowych klonów i linked worktree, w tym
  worktree zarejestrowanych poza skanowanym katalogiem.
- Dodano zarządzany workflow targetu sprawdzający live stan branchy i PR-ów na
  GitHubie oraz włączono oba checkery do pakietu adopcyjnego.
- Powiązano nowe reguły z kodami enforcementu i poprawiono historyczne
  mapowanie reguł lifecycle branchy.
- Zachowano unikalne dane w tagach/refach archiwalnych, usunięto bezpieczne
  workspace’y i potwierdzono czysty stan lokalny oraz 77 zdalnych repozytoriów.
- Zintegrowano zatwierdzony merge Node 24 jako nową bazę i przepięto tworzony
  workflow targetu na immutable checkout v7 oraz github-script v8.
- Ponowiono pełny kontrakt po integracji: wszystkie testy, Ruff i mapowanie
  160 reguł na 48 kodów przechodzą bez luk.
- Po semantycznym review Validatora domknięto rekurencyjne odkrywanie
  zarejestrowanych worktree i ujednoznaczniono przechwytywanie diagnostyki w
  regresji brakującego katalogu.
