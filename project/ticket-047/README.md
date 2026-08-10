# Ticket 047: Complete and publish bounded autonomy migration fix

- **ID**: ticket-047
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
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

- [x] AC-01: Template’y i fallback `new-ticket.sh` tworzą ticket w
  `IN_PROGRESS / EDIT`, zapisują bounded session authorization i nie emitują
  bezwarunkowego wymagania świeżej zgody.
- [x] AC-02: Regresje scaffoldera wymagają tej semantyki i nadal zachowują
  blokady kolizji workstreamów, ownership human files oraz deterministyczną
  alokację ID.
- [x] AC-03: `VERSION`, manifest, changelog i aktywne asercje wskazują `0.14.1`;
  syntetyczny następny upgrade używa `0.14.2`, a historyczne fixture’y zostają.
- [x] AC-04: Pełny Linux contract, Windows i exact-head Validator App są
  zielone przed merge.
- [x] AC-05: Pełny Linux contract przechodzi ponownie na czystym merge SHA.
- [x] AC-06: Nowy annotowany `v0.14.1` i opublikowany GitHub Release wskazują
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

## Stan

`DONE / DONE`. PR #75 przeszedł Linux, Windows i exact-head Validator App dla
`d7ab953`, po czym został scalony jako `main@63a3d56`. Pełny Linux contract
przeszedł ponownie w czystym detached checkout. Annotowany `v0.14.1` peeluje
dokładnie do `63a3d56`, a opublikowany GitHub Release nie jest draftem ani
prerelease'em. Wcześniejsze tagi nie zostały zmienione.

Goal 2.1.289 dostarczył oba PR-y w trybie `pull-request`, lecz jego wymagany
`direct-main --force-publish` na czystym merge SHA zatrzymał się przed delivery
na „No changes to commit”. Aby nie tworzyć nowego, niezatwierdzonego SHA,
immutable tag i Release opublikowano kontrolowanym fallbackiem na już
zwalidowanym merge; defekt Goal został przekazany do jego backlogu.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-047/`.
