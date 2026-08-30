# Ticket 130: Prevent managed governance wrapper bytecode drift

- **ID**: ticket-130
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-26

## Cel i Zakres

Usunąć fałszywy drift powodowany przez `__pycache__`, który potrafi tworzyć
sam wrapper governance. Oba wspierane warianty checkera mają działać bez
zapisu bytecode, a overlap checker ma ignorować również zagnieżdżone cache
Pythona, bez ignorowania rzeczywistych zmian źródłowych.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Uruchomienie wrappera przy usuniętym
  `PYTHONDONTWRITEBYTECODE` nie pozostawia żadnego `__pycache__`.
- [x] AC-02: Test adopcji i bramka governance pozostają zielone.
- [x] AC-03: Taki sam plik cache w zagnieżdżonym `__pycache__` dwóch worktree
  nie generuje fałszywego konfliktu.

## Ryzyka i Uwagi
- Ryzyko: zmiana obejmuje plik zarządzany, więc Core i inni adopterzy otrzymają
  ją wyłącznie przez przypięty upgrade opublikowanego standardu.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-130/`.
