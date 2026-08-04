# Ticket 001: Utrzymanie i rozwój standardu new-project

- **ID**: ticket-001
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-04

## Cel i Zakres

Ujednolicić zasady utrzymania `wellmanifest/new-project`: repozytorium jest
edytowalnym źródłem standardu, pod warunkiem że każda wieloetapowa zmiana jest
prowadzona w tym repozytorium i przypisana do dokładnie jednego ticketu
`project/ticket-{NNN}` z zatwierdzonym zakresem.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: `AGENTS.md`, `POLICY.md`, `CONTRIBUTING.md` i dokumentacja nie
  określają huba jako bezwzględnie tylko do odczytu.
- [x] AC-02: Utrzymanie huba wymaga ticketu `project/ticket-{NNN}` i zgodnego
  `intent.json`; tickety systemów docelowych nadal powstają wyłącznie w ich
  własnych repozytoriach.
- [x] AC-03: Reguły nie zezwalają agentowi tworzyć lub zmieniać plików
  `user-*` ani wykonywać zmian poza `allowedPaths`.
- [x] AC-04: Kontrola spójności dokumentów i diffu nie wykazuje pozostałych
  sprzecznych deklaracji READ-ONLY.

## Ryzyka i Uwagi

- Ryzyko: ticket utrzymaniowy huba może zostać pomylony z ticketem systemu
  docelowego. Mitygacja: jawne rozdzielenie kontekstów repozytorium w zasadach.
- Ryzyko: nowy wyjątek mógłby ominąć granicę zakresu. Mitygacja: dokładnie jeden
  aktywny ticket i `intent.allowedPaths` dla każdej zmiany.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-001/`.
