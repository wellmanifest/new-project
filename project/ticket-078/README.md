# Ticket 078: Add HOME versus ADOPT placement to ticket intent

- **ID**: ticket-078
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
- **Utworzono**: 2026-08-14

## Cel i Zakres

Dodać opcjonalny, zamknięty blok `placement` do `new-project.intent/v2` i
`v3`, aby agent przed implementacją jednoznacznie rozdzielał HOME repozytorium
od ADOPT standardów Wellmanifest. Kontrakt obejmuje `home`, `shape`, opcjonalny
`runtimeOwner` i listę `adopt`; `runtime_service` nie może używać
`home=wellmanifest`.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Zamknięty JSON Schema akceptuje poprawny opcjonalny `placement`
  w intentach v2/v3 i nie łamie istniejących ticketów bez tego pola.
- [x] AC-02: Walidator deterministycznie odrzuca nieznane wartości `home`,
  `shape`, `runtimeOwner`, błędne identyfikatory `adopt` oraz kombinację
  `runtime_service` + `home=wellmanifest`.
- [x] AC-03: `POLICY.md`, `CONTRIBUTING.md`, `AGENTS.md` i szablon targetu
  używają zamkniętego słownika HOME vs ADOPT i nie utożsamiają adopcji z home.
- [x] AC-04: Rejestr enforcement wiąże nowe reguły z `GOV-INTENT-002`, a pełny
  zestaw testów governance przechodzi.
- [ ] AC-05: Zmiana jest opublikowana przez PR przypięty wyłącznie do
  `ticket-078` i otrzymuje trusted exact-head approval przed merge.

## Ryzyka i Uwagi

- `placement` pozostaje opcjonalne w schemacie, aby stare tickety nadal się
  walidowały; wymaganie jego wypełnienia dla nowych repozytoriów jest regułą
  proceduralną.
- Ta zmiana nie publikuje nowego taga. Wydanie po merge będzie osobnym,
  mechanicznym ticketem release.

## Dowody walidacji lokalnej

- Governance Hub scope gate: `GOV-PASS` (0 błędów, 0 ostrzeżeń).
- Wszystkie dziewięć zestawów `tests/*.test.sh`: PASS.
- JSON Schema, JSON syntax, Python compile, Ruff 0.15.21, diff whitespace i
  wzorce sekretów: PASS.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-078/`.
