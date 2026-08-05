# Ticket 020: Runtime zmiennych srodowiskowych dla governance DSL

- **ID**: ticket-020
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-05

## Cel i Zakres
Rozszerzyć governance DSL o jawny, deterministyczny kontrakt zmiennych
środowiskowych oraz runtime pozwalający bezpiecznie używać wartości z `.env`.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Deklaracje DSL rozróżniają zwykłe zmienne, wymagane wartości i sekrety.
- [x] AC-02: Runtime stosuje precedencję process > `.env` > default i eksportuje tylko zadeklarowane nazwy.
- [x] AC-03: Raporty redagują sekrety, a ścieżki `.env` nie mogą wyjść poza katalog kontraktu.
- [x] AC-04: Test automatyczny obejmuje rozwiązywanie, override, redakcję i przypadki negatywne.

## Ryzyka i Uwagi
- Ryzyko: przypadkowe ujawnienie sekretu; mitygacja: brak trybu wypisującego
  surowe sekrety oraz uruchamianie procesu potomnego bez pośrednictwa shella.

## Dowody walidacji

- `bash tests/governance-env.test.sh` - PASS
- `bash tests/governance-scripts.test.sh` - PASS
- `bash tests/governance-validator.test.sh` - PASS

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-020/`.
