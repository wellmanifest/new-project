# Preprompt: terminal workspace and branch lifecycle

- Rozróżnij lokalny filesystem od stanu GitHuba; nie deklaruj, że CI widzi
  lokalne worktree lub klony.
- Przed cleanupem potwierdź dirty state, osiągalność HEAD i klasyfikację danych.
- Nigdy nie usuwaj automatycznie unikalnego lub niezidentyfikowanego materiału.
- Dostarcz read-only checker przez pakiet adopcyjny i Goal.
- Zainstaluj w targetach rzeczywistą kontrolę zdalnego lifecycle.
- Testuj deterministycznie i nie wykonuj publikacji w ramach implementacji.

