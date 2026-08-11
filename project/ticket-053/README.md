# Ticket 053: Keep managed Python lint-neutral downstream

- **ID**: ticket-053
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-11

## Cel i Zakres

Naprawić regresję ujawnioną przez żywą adopcję w `semcod/code2docs`: trzy
zarządzane pliki Pythona dodają 17 błędów Ruffa do repozytorium docelowego.
Źródła mają pozostać semantycznie równoważne, a skrypty z shebangiem mają być
instalowane z bitem wykonywalnym zgodnym z ich źródłowym trybem.

Zakres obejmuje dwa źródła wymagające mechanicznych uproszczeń, manifest
pakietu, test trybu adopcji, jawny Docker opt-in fixture oraz dowód
integracyjny z konfiguracją Ruffa rzeczywistego repo. Nie zmienia reguł
governance, diagnostyki, schematów ani publicznego zachowania walidatora.

## Kryteria Odbioru (Acceptance Criteria)

- [ ] AC-01: `scripts/decision_record.py` i `scripts/governance_check.py`
  przechodzą konfigurację Ruffa `code2docs` bez naruszeń i bez wyciszeń.
- [ ] AC-02: trzy zarządzane skrypty `.governance/*.py` są deklarowane jako
  executable, a test adopcji potwierdza tryb w repo docelowym.
- [ ] AC-03: pełny kontrakt Linux, testy validatora, decision record i adopcji
  przechodzą bez zmiany oczekiwanych kodów `GOV-*`; fixture testujący
  `GOV-DOCKER-002` jawnie włącza opcjonalną politykę Docker.
- [ ] AC-04: złożony kandydat po ponownej adopcji w `code2docs` nie zwiększa
  baseline Ruffa 514 i zachowuje 161 przechodzących testów produktu.
- [ ] AC-05: zmiana pozostaje lokalna; bez push, PR, merge, tagu, release ani
  publikacji pakietu.

## Ryzyka i Uwagi

- Mechaniczne uproszczenia mogą niechcący zmienić rozpoznawanie scope lub
  walidację pakietu; istniejące testy kontraktowe muszą przejść w całości.
- Zmiana `executable=false` na `true` wpływa na tryb plików w downstream, lecz
  odpowiada istniejącym shebangom i trybowi `775` źródeł; test adopcji ma
  sprawdzić dokładnie ten efekt.
- Ruff jest dowodem integracyjnym z istniejącego, przypiętego lockfile
  `code2docs`, nie nową zależnością runtime standardu.
- Złożenie ticketów 051 i 052 ujawniło fałszywy test: fixture dziedziczył nowe
  `docker.required=false`, więc przypadki mutowalnych obrazów nie uruchamiały
  reguły. Jawny target opt-in przywraca rzeczywiste pokrycie bez zmiany
  portable defaults.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-053/`.
