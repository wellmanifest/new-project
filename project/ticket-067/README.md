# Ticket 067: Diagnostic remediation intent DSL and todo2code analysis

- **ID**: ticket-067
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-12

## Cel i Zakres

Rozszerzyć kanoniczną diagnostykę z ticketu 066 o wersjonowany DSL intencji
naprawy. Stabilny katalog i `error/*.md` nadal opisują rozwiązanie wielokrotnego
użytku, natomiast konkretne wystąpienie błędu ma otrzymać w repozytorium
docelowym hash-bound plan wejściowy dla LLM: fakty, warunki stosowalności,
wykluczenia false-positive, outcome/non-goals, bezpieczne kroki, zależności i
deterministyczne weryfikacje.

Standard ma walidować tę intencję bez LLM, renderować kanoniczny brief oraz
wejście dla istniejącego pipeline todo2code. Wynik todo2code pozostaje
doradczym, związanym hashem overlayem: może ujawnić niespójne ścieżki, brak
pokrycia kryteriów i dwuznaczności oraz dodać wskazówki dla planującego LLM,
ale nie może rozszerzyć zaakceptowanego zakresu ani zatwierdzić zmiany.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Normatywny kontrakt rozróżnia reusable solution
  (`diagnostics.json` + `error/*.md`) od instance-specific remediation intent
  zapisanego wyłącznie w ticketcie repozytorium docelowego.
- [x] AC-02: Schema i dependency-free validator wykrywają błędy struktury,
  nieuziemione false-positive, ciche pominięcia bez kodu, cykle kroków,
  brak weryfikacji i ryzykowne operacje bez jawnej autoryzacji.
- [x] AC-03: Renderer tworzy stabilny brief dla LLM oraz task/TODO dla
  todo2code; importer wiąże analizę z dokładnym digestem intencji i wykrywa
  ścieżki/kryteria spoza kontraktu.
- [x] AC-04: Regresja odwzorowuje klasy problemów z raportu Diagit: false
  positive OpenRouter, niedostępny path, niejednoznaczny layout, drift wydania,
  brak inventory i zakaz automatycznego czyszczenia brudnych worktree.
- [x] AC-05: Focused testy, istniejący audyt diagnostyk/rule traceability,
  pełny Linux contract i rzeczywisty deterministyczny pipeline todo2code
  przechodzą bez nowej zależności runtime.

## Ryzyka i Uwagi

- DSL nie implementuje domenowych detektorów Diagit. Określa wspólny kontrakt,
  w którym target zapisuje wynik detekcji i intencję naprawy.
- Todo2code i LLM są warstwą advisory; scope, bezpieczeństwo, governance gate i
  trusted exact-head approval pozostają niezależnymi twardymi granicami.
- Brudnych worktree, nieczytelnych ścieżek ani nieznanych danych nie wolno
  automatycznie usuwać lub ukrywać.
- Ticket 065 został niezależnie zamknięty przez PR #97 przed publikacją tego
  workstreamu; ticket 067 nie tagował v0.15.0 ani nie zmieniał jego plików.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-067/`.
