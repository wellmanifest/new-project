# Ticket 083: Recognize generated secret placeholders safely

- **ID**: ticket-083
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-14

## Cel i Zakres

Skaner `GOV-SECRET-001` traktuje wymagane przez runtime markery bootstrapu
`__GENERATE_*__` jak prawdziwe sekrety. W rezultacie bezpieczna zmiana
`.env.example` w repozytorium adoptującym standard jest blokowana przez
placeholdery, które sam standard i runtime wymagają do automatycznego
wygenerowania poświadczeń.

Zakres obejmuje wyłącznie precyzyjne rozpoznanie pełnej wartości
`__GENERATE_[A-Z0-9_]+__` oraz regresje zachowujące fail-closed wykrywanie
prawdziwych tokenów i wartości tylko podobnych do markera.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: Dokładny, wielkoliterowy marker `__GENERATE_[A-Z0-9_]+__` nie
      emituje `GOV-SECRET-001`.
- [ ] AC-02: Marker z prefiksem, sufiksem, małymi literami albo niedozwolonym
      znakiem nadal jest skanowany jak zwykła wartość i nie tworzy wyjątku.
- [ ] AC-03: Długa rzeczywista wartość tokenu nadal emituje
      `GOV-SECRET-001`, a pełny kontrakt walidatora i bramka huba przechodzą.

## Ryzyka i Uwagi
- Najważniejszym ryzykiem jest zbyt szeroki wyjątek maskujący sekret.
  Mitygacja: osobne, zakotwiczone `fullmatch`, dozwolony alfabet ograniczony do
  `[A-Z0-9_]` i ujemne regresje dla wartości podobnych do markera.
- Ticket nie odczytuje sekretów, nie zmienia bootstrapu runtime i nie osłabia
  skanowania plików `.env.example`.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-083/`.
