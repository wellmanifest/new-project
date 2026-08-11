# Ticket 059: Recognize Compose-only Docker roots

- **ID**: ticket-059
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-11

## Cel i Zakres

Naprawić profil `docker` dla monorepo, które ma rootowy Compose i Dockerfile w
jawnie wyliczonych podkatalogach. Obecny profil uznaje tylko root
`Dockerfile`/`Dockerfile.e2e`, więc prawdziwy układ `semcod/mcp` dostałby
`GOV-STACK-001` albo wymagał sztucznego pliku.

Rootowe `compose.yml`, `docker-compose.yml` oraz warianty `.yaml` mają być
markerami stosu. Lista walidowanych Dockerfile nadal pochodzi z manifestu;
naprawa nie wprowadza automatycznego, rekurencyjnego zaufania.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Polecenie użytkownika stanowi bounded
  `SESSION_EXECUTION_AUTHORIZATION` dla lokalnej implementacji i testów.
- [x] AC-02: Compose-only root z jawnym nested Dockerfile przechodzi profil
  `docker` i pełną kontrolę pinów.
- [x] AC-03: Nested Dockerfile bez rootowego markera nadal otrzymuje
  `GOV-STACK-001`.
- [x] AC-04: Manifest zna `.yml` i `.yaml`, pełny Linux contract przechodzi, a
  pilot `mcp` nie potrzebuje sztucznego root Dockerfile.

## Ryzyka i Uwagi
- Compose jest tylko markerem stosu, nie substytutem jawnej listy plików do
  inspekcji.
- Nie naprawiamy ani nie przepinamy obrazów downstream w tym ticketcie.
- Nie wykonujemy push, PR, merge, tagowania ani publikacji.

## Dowody walidacji

- Focused fixture z root `docker-compose.yml` i nested
  `services/api/Dockerfile` zwraca `GOV-PASS`; po przeniesieniu Compose do
  niestandardowego podkatalogu zwraca `GOV-STACK-001`.
- Domyślny manifest i profil obejmują `.yml`/`.yaml`, a jawna lista
  Dockerfile/Compose nadal steruje kontrolą wszystkich referencji.
- Wszystkie polecenia Linux CI, kompletność suite, kontrakty JSON i Ruff
  przechodzą na implementacji `e5d67c0`.
- Fresh `mcp` przyjął exact SHA bez `--upgrade`, zachował swój `project.sh` i
  rozpoznał root Compose oraz osiem nested Dockerfiles bez `GOV-STACK-001`.
- Gate `mcp` poprawnie zatrzymał się dalej na jednym `GOV-DOCKER-002` dla 10
  istniejących mutable references. To produktowy dług pinowania, nie regresja
  detekcji; pilot pozostaje jawnie `BLOCKED`, bez atrap SHA i bez ukrycia
  Dockera.

## Autoryzacja

Bieżące polecenie użytkownika zleca lokalne poprawianie standardu na podstawie
kolejnych pilotów. Operacje zewnętrzne wymagają osobnej dyspozycji.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-059/`.
