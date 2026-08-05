# Preprompt i wytyczne techniczne (ticket-014)

- **Tytuł zadania**: Kanoniczna klasyfikacja pracy BUG, FEATURE, SERVICE
- **Utworzono**: 2026-08-05T08:31:00Z

## Wymagania

- Użyj deklaratywnego JSON DSL z wersją i oddzielnym JSON Schema Draft 2020-12.
- Nie łącz `kind` z `priority`; `BUG/P3` i `SERVICE/P0` są poprawnymi parami.
- Sortuj gotowe zadania według `kind`, potem `priority`, potem stabilnego ID;
  zależności muszą pozostać przed zadaniem zależnym.
- Klasyfikuj wzrost CC względem baseline lub nowe przekroczenie progu jako
  `BUG/regression`, a istniejący, niepogorszony dług CC jako `SERVICE/health`.
- Nie używaj LLM jako źródła deterministycznej klasyfikacji.
- Zachowaj kompatybilność istniejących locków i historycznych ticketów.

## Zasoby

- Standard: https://github.com/wellmanifest/new-project
- Konsument planów: https://github.com/semcod/todo2code
- Konsument lokalny: https://github.com/semcod/goal

## Granice wykonawcze

Przed implementacją wymagane jest zatwierdzenie `ai-codex.md`, `TODO.md` i
`intent.json`. Zmiany w repozytoriach konsumenckich dostaną własne tickety,
branche i testy po opublikowaniu dokładnego SHA standardu.
