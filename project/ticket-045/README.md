# Ticket 045: Govern publishing through Goal full workflow

- **ID**: ticket-045
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
- **Utworzono**: 2026-08-09

## Cel i zakres

Ustanowić normatywny, fail-closed kontrakt publikacji przez pełny workflow
Goal. Repozytorium, które deklaruje zarządzaną publikację, ma wykonywać
`goal -a` z jawnym trybem dostawy zamiast surowego `git push` lub bezpośredniej
publikacji do rejestru.

Kontrakt rozdzieli publikację implementacji od wydania:

1. implementacja używa `goal --delivery-mode pull-request --no-publish -a
   push --ticket ticket-NNN`;
2. publikacja rejestru lub immutable release jest dozwolona dopiero z
   zatwierdzonego i ponownie zwalidowanego merge SHA;
3. lokalny event Goal jest dowodem audytowym, ale nie zastępuje chronionego CI,
   branch protection ani exact-head approval.

Ticket zmienia wyłącznie standard i testy huba. Nie publikuje wydania
`new-project`, nie modyfikuje `semcod/goal` i nie migruje repozytoriów
downstream.

## Kryteria odbioru

- [x] AC-01: `CONTRIBUTING.md` zawiera stabilne reguły rozróżniające publikację
  implementacji, rejestru i immutable release przez `goal -a`.
- [x] AC-02: Implementacja jest publikowana wyłącznie w trybie
  `pull-request --no-publish`; publikacja rejestru, taga lub Release przed
  trusted merge i ponowną walidacją jest zabroniona.
- [x] AC-03: Kontrakt wymaga walidacji `goal.yaml` oraz feature probe dla
  `--delivery-mode`; sam numer wersji Goal nie jest wystarczającym dowodem.
- [x] AC-04: `docs/RELEASES.md` opisuje nową procedurę oraz jasno oznacza
  historyczną, ręczną publikację wcześniejszych wersji.
- [x] AC-05: Każda nowa reguła ma kompletne mapowanie enforcement, a testy
  blokują brak `goal -a`, pomieszanie etapów lub uznanie lokalnego hooka/eventu
  za trust root.

## Ryzyka i uwagi

- `goal -a` domyślnie obejmuje testy, commit, push i publish. Bez jawnego
  `pull-request --no-publish` mógłby opublikować pakiet przed review.
- Globalny i repozytoryjny build Goal mogą raportować tę samą wersję, a mieć
  różny zestaw funkcji. Kontrakt wymaga feature probe, nie tylko semver.
- Lokalny pre-push hook można ominąć; autorytatywne egzekwowanie pozostaje w
  chronionym GitHub workflow i ruleset.
- Istniejące wydania pozostają immutable i nie będą przepisywane w celu
  retroaktywnego przypisania im użycia Goal.

## Stan

Użytkownik zatwierdził kontynuację 2026-08-09. Ticket przeszedł do
`IN_PROGRESS / VALIDATION`; interaktywna zgoda nie zastępuje niezależnego,
exact-head approval wymaganego przed merge.

## Dowody walidacji

- Wszystkie cztery nowe reguły `C-PUBLISH-005..008` są wykrywane przez parser
  i mają jawne mapowanie enforcement.
- Capability probe potwierdził, że `--ticket` należy umieścić po jawnej
  podkomendzie `push`, natomiast rootowe `-a` zachowuje pełny workflow.
  Normatywna komenda używa rzeczywistej składni 2.1.289; ticket wiążą również
  intent, branch i PR na current HEAD.
- Regresja kontraktu Goal: PASS.
- Pełny Linux hub contract, w tym osiem zestawów testów: PASS.
- Niezależne powtórzenie 2026-08-10 użyło `uv run --no-project --with
  jsonschema==4.25.1` oraz `set -euo pipefail`; wszystkie osiem zestawów i
  kontrola podpięcia suite do CI przeszły. Wcześniejsza próba host-only została
  odrzucona jako niepełna, ponieważ Python hosta nie miał zależności
  `jsonschema` przypiętej w CI.
- `git diff --check`: PASS.
- Docker Engine 29.1.3: dostępny.
- Windows i chroniony exact-head review pozostają zadaniem CI po publikacji PR.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-045/`.
