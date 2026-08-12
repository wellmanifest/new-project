# Ticket 072: Publish orphan local branch audit as new-project 0.16.2

- **ID**: ticket-072
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-12

## Cel i zakres

Opublikować jako immutable `new-project 0.16.2` zintegrowaną zmianę ticketu
071, która rozszerza lokalny audyt workspace o osierocone branche. Wydanie
zmienia wyłącznie nośniki wersji, testy spójności wersji i changelog; kod
audytu pozostaje dokładnie tym, który przeszedł PR #104 i został scalony do
`main`.

## Kryteria odbioru

- [ ] AC-01: `VERSION` i oba manifesty standardu deklarują `0.16.2`, a testy
  blokady adopcji oraz walidatora oczekują tej samej wersji.
- [ ] AC-02: changelog opisuje wykrywanie pozostawionych branchy i zachowanie
  read-only/fail-closed bez przepisywania historii wydania `0.16.1`.
- [ ] AC-03: pełny kontrakt Linux, Ruff, testy Windows i dokładny Validator App
  przechodzą dla bieżącego SHA PR.
- [ ] AC-04: zatwierdzony payload jest scalony bez zmiany drzewa, a CI po
  scaleniu przechodzi na dokładnym merge SHA.
- [ ] AC-05: Goal `2.1.298` tworzy annotowany tag `v0.16.2` i finalny GitHub
  Release z czystego, ponownie przetestowanego `main`; tag i release wskazują
  ten sam merge SHA.

## Ryzyka i uwagi

- Publikacja jest zewnętrznym, niemutowalnym skutkiem. Nastąpi dopiero po
  exact-head approval, merge i ponownych testach czystego `main`.
- `goal.yaml` jest już śledzonym kontraktem dostawy i nie należy do zakresu
  tej zmiany. Brudny główny checkout użytkownika pozostaje nietknięty.
- Ticket 069 jest `BLOCKED` i nie rezerwuje workstreamu ani ścieżek. Jego
  niezależne, nieopublikowane zmiany nie są częścią tego wydania.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-072/`.
