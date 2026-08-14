# Ticket 075: Publish delivery profiles as new-project 0.17.0

- **ID**: ticket-075
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-14

## Cel i Zakres

Opublikować jako immutable `new-project 0.17.0` zintegrowany kontrakt ticketu
074: jawne tryby repozytorium, warunkowy Docker i zamknięte profile dostawy
XS/S/M/L. Zmiana wydaniowa synchronizuje wyłącznie sześć nośników wersji,
asercje spójności i changelog; nie modyfikuje zintegrowanego walidatora ani
semantyki profili.

## Kryteria Odbioru (Acceptance Criteria)

- [ ] AC-01: `VERSION` i oba manifesty standardu deklarują `0.17.0`, a testy
  adopcji oraz walidatora oczekują tej samej wersji.
- [ ] AC-02: changelog publikuje zintegrowane profile delivery jako nowe,
  kompatybilne wstecz minor release bez przepisywania historii `0.16.2`.
- [ ] AC-03: wszystkie zestawy Linux, Ruff, wymagane checki i governance
  przechodzą na dokładnym HEAD kandydata.
- [ ] AC-04: PR otrzymuje trusted exact-head Validator approval i jest scalony
  bez zmiany zatwierdzonego drzewa.
- [ ] AC-05: czysty merge `main` przechodzi ponowne testy, a annotowany tag i
  finalny GitHub Release `v0.17.0` wskazują dokładnie ten merge SHA.

## Ryzyka i Uwagi

- Publikacja taga i release jest niemutowalnym skutkiem i nastąpi dopiero po
  trusted merge oraz czystym reteście zintegrowanego `main`.
- To minor release, ponieważ udostępnia nowy kontrakt konfiguracji i egzekwuje
  budżety per klasa złożoności; nie wolno zmienić znaczenia `v0.16.2`.
- Downstream Hub pozostaje fail-closed na swojej obecnej wersji do czasu
  osobnej, exact-SHA adopcji po publikacji.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-075/`.
