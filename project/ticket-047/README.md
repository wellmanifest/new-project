# Ticket 047: Complete and publish bounded autonomy migration fix

- **ID**: ticket-047
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-10

## Cel i Zakres

Domknąć kontrakt autonomii z ticketu 046 w generatorze nowych ticketów, który
wciąż emituje stare `PLAN / WAIT_FOR_APPROVAL`, „waiting for approval” i wymóg
osobnej zgody. Template’y huba oraz fallback zarządzanego `new-ticket.sh` mają
domyślnie tworzyć `IN_PROGRESS / EDIT` z zapisaną bounded
`SESSION_EXECUTION_AUTHORIZATION`, bez osłabiania osobnego trusted merge review.

Następnie opublikować pełną naprawę migratora i kontraktu autonomii jako
immutable patch `v0.14.1`, związany z dokładnym przetestowanym merge SHA.

## Kryteria Odbioru (Acceptance Criteria)

- [ ] AC-01: Template’y i fallback `new-ticket.sh` tworzą ticket w
  `IN_PROGRESS / EDIT`, zapisują bounded session authorization i nie emitują
  bezwarunkowego wymagania świeżej zgody.
- [ ] AC-02: Regresje scaffoldera wymagają tej semantyki i nadal zachowują
  blokady kolizji workstreamów, ownership human files oraz deterministyczną
  alokację ID.
- [ ] AC-03: `VERSION`, manifest, changelog i aktywne asercje wskazują `0.14.1`;
  syntetyczny następny upgrade używa `0.14.2`, a historyczne fixture’y zostają.
- [ ] AC-04: Pełny Linux contract, Windows i exact-head Validator App są
  zielone przed merge.
- [ ] AC-05: Pełny Linux contract przechodzi ponownie na czystym merge SHA.
- [ ] AC-06: Nowy annotowany `v0.14.1` i opublikowany GitHub Release wskazują
  dokładnie zwalidowany merge SHA; wcześniejsze tagi nie są przesuwane.

## Ryzyka i Uwagi

- Domyślny stan scaffoldera jest publicznym zachowaniem: test porównuje template
  i fallback, aby downstream bez katalogu template nie wrócił do starej bramki.
- Autonomia pozostaje ograniczona intentem; destrukcja, sekrety, nowa
  koordynacja zewnętrzna, materialny nowy cel i merge wymagają osobnej władzy.
- Tag i Release są nieodwracalne operacyjnie, dlatego następują dopiero po
  chronionym PR i ponownym teście czystego merge SHA.
- Brak zmian zależności i brak mutacji downstream w tym ticketcie.

## Autoryzacja

Bieżące polecenie użytkownika zleca kontynuację, test, publikację i tryb
autonomiczny. Stanowi bounded `SESSION_EXECUTION_AUTHORIZATION` dla tego intentu
bez osobnego potwierdzenia; nie stanowi trusted merge approval.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-047/`.
