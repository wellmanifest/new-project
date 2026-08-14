# Ticket 084: Release generated placeholder fix as new-project 0.18.1

- **ID**: ticket-084
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-14

## Cel i Zakres

Opublikować zintegrowaną poprawkę bezpiecznych markerów bootstrapu z
ticket-083 jako immutable `new-project 0.18.1`. Wydanie synchronizuje wyłącznie
sześć nośników wersji, aktywne asercje testów i changelog. Nie zmienia skanera
ani semantyki `GOV-SECRET-001` po ich merge.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `VERSION`, oba manifesty i aktywne asercje testowe deklarują
      dokładnie `0.18.1`.
- [x] AC-02: Changelog opisuje poprawkę markerów `__GENERATE_*__` jako patch i
      zachowuje historię `0.18.0`.
- [x] AC-03: Wszystkie zestawy testów, Ruff, secret scan i governance
      przechodzą dla dokładnego commita kandydata.
- [ ] AC-04: PR otrzymuje trusted exact-head Validator approval i jest scalony
      bez zmiany zatwierdzonego drzewa.
- [ ] AC-05: Czysty merge `main` przechodzi retest, a annotowany tag i finalny
      GitHub Release `v0.18.1` wskazują dokładnie ten merge SHA.

## Ryzyka i Uwagi
- Tag i finalny release są niemutowalne; powstaną dopiero po trusted merge i
  ponownym teście czystego `main`.
- Jest to patch release, ponieważ publikuje wyłącznie kompatybilną poprawkę
  false-positive bez rozszerzenia składni sekretów.
- Adopcja w Platform pozostaje osobnym target-owned ticketem i nie należy do
  write scope tego wydania.

## Dowody przed publikacją

- Diff implementacyjny obejmuje dokładnie sześć zadeklarowanych nośników.
- Wszystkie dziewięć zestawów `tests/*.test.sh`, wymagane checki, JSON/schema,
  secret scan i Ruff `0.15.21`: PASS.
- `v0.18.1` nie istnieje jako tag ani GitHub Release przed publikacją.
- Lokalny Ruff `0.16.1` emituje nowe findingi na niezmienionych plikach bazy;
  release używa kanonicznej przypiętej wersji `0.15.21` zgodnie z poprzednim
  kontraktem wydania, bez maskowania findings w testowanym kodzie.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-084/`.
