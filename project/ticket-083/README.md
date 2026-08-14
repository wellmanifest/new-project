# Ticket 083: Recognize generated secret placeholders safely

- **ID**: ticket-083
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
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
- [x] AC-01: Dokładny, wielkoliterowy marker `__GENERATE_[A-Z0-9_]+__` nie
      emituje `GOV-SECRET-001`.
- [x] AC-02: Marker z prefiksem, sufiksem, małymi literami albo niedozwolonym
      znakiem nadal jest skanowany jak zwykła wartość i nie tworzy wyjątku.
- [x] AC-03: Długa rzeczywista wartość tokenu nadal emituje
      `GOV-SECRET-001`, a pełny kontrakt walidatora i bramka huba przechodzą.

## Dowody walidacji

- `bash tests/governance-validator.test.sh`: PASS; katalog diagnostyczny ma 65
  kodów i zero findings.
- Focused Ruff przechodzi po wyłączeniu dwóch istniejących kodów bazowych w
  tym samym pliku (`BLE001`, `I001`); ticket nie rozszerza zakresu o ich
  porządkowanie.
- Nowy skaner uruchomiony na rzeczywistym `.env.example` Platform ticket-021
  zwraca `probable_secret_fields=[]` bez odczytu jakiegokolwiek sekretu.

## Ryzyka i Uwagi
- Najważniejszym ryzykiem jest zbyt szeroki wyjątek maskujący sekret.
  Mitygacja: osobne, zakotwiczone `fullmatch`, dozwolony alfabet ograniczony do
  `[A-Z0-9_]` i ujemne regresje dla wartości podobnych do markera.
- Ticket nie odczytuje sekretów, nie zmienia bootstrapu runtime i nie osłabia
  skanowania plików `.env.example`.

## Dowody publikacji

- Pull request [#130](https://github.com/wellmanifest/new-project/pull/130)
  przeszedł `test` i `windows-governance` na dokładnym HEAD
  `7427b51a000bb7103483dd816b23a95fe0347ad6`.
- Validator App `ifuri-validator-agent[bot]` zatwierdził ten sam HEAD i scalił
  go przez chroniony proces jako
  `af9cb1231f7eafc9a484dacdc3deaf5b589e1001`.
- Gałąź implementacyjna została usunięta przed utworzeniem tego
  governance-only closure ze zintegrowanego `main`.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-083/`.
