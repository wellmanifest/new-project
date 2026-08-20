# Ticket 095: Audit enforceability of Wellmanifest standards

- **ID**: ticket-095
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-20

## Cel i Zakres

Ustalić, czy standardy Wellmanifest są nie tylko opisane i lokalnie
walidowalne, lecz również wykonywane w CI i wymagane przed zmianą `main`.
Audyt obejmuje 15 wskazanych przez Foundera repozytoriów i rozdziela
governance procesu zmian, conformance standardu oraz zgodność danych żywego
adoptera. Wynik jest publikowany jako centralna dokumentacja z planem
remediacji; ten ticket nie zmienia badanych repozytoriów ani ich rulesetów.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Macierz obejmuje wszystkie 15 repozytoriów i odróżnia walidator
  lokalny, CI, ochronę `main` oraz zgodność danych runtime.
- [x] AC-02: Wnioski są oparte na wykonanych governance gates, testach
  conformance, DSL manifests i odczycie aktywnych reguł GitHub.
- [x] AC-03: Dokument wskazuje reprodukowalne defekty, w tym drift danych
  `policy-dsl`, nieprzenośne URI oraz nieprawdziwe required-checks adopterów.
- [x] AC-04: Docelowy kontrakt i kolejność remediacji są wystarczająco ścisłe,
  aby kolejne tickety mogły wdrażać poprawki bez zgadywania.

## Ryzyka i Uwagi

- Wynik jest migawką z 2026-08-20; reguły hostowane i żywe dane mogą się
  zmienić. Dokument zapisuje refy i komendy, aby następny audyt był
  porównywalny.
- Zielony test lokalny nie dowodzi, że GitHub wymaga go przed merge. Zielona
  governance nie dowodzi conformance domeny. Te warstwy są raportowane osobno.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-095/`.
