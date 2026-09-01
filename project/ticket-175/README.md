# Ticket 175: Make anti-noise upgrades valid for legacy adopters

- **ID**: ticket-175
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-09-01

## Cel i Zakres

Usunąć dwie blokady ujawnione przez pierwszy realny upgrade do 0.19.20:
brak ownership dla nowego rozszerzalnego pliku ticket-allocation oraz możliwość
zachowania przez legacy manifest obowiązkowych logów i redundantnych plików
ticketa. Poprawka i wersja 0.19.21 należą do jednego materialnego PR.

## Kryteria Odbioru (Acceptance Criteria)

- [ ] AC-01: Pierwsza adopcja i upgrade starszego adoptera mogą atomowo objąć
      wspólny manifest, lock, package marker, kontrakt agentów i rozszerzalne
      zasady w jednym workstreamie integracyjnym.
- [ ] AC-02: Manifest wymagający `ai-*.md`, raw logs, `preprompt.md` lub
      `changelog.md` jest odrzucany; dozwolone są tylko `README.md` i
      `intent.json`.
- [ ] AC-03: Testy adopcji, pełna bramka i chroniony merge przechodzą.

## Ryzyka i Uwagi

- Repozytoria z celową historyczną konfiguracją nośników muszą ją jawnie
  znormalizować w tym samym materialnym adoption PR; nie powstaje commit
  migracyjny zawierający wyłącznie dokumentację procesu.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-175/`.
