# Ticket 059: Recognize Compose-only Docker roots

- **ID**: ticket-059
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
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
- [ ] AC-02: Compose-only root z jawnym nested Dockerfile przechodzi profil
  `docker` i pełną kontrolę pinów.
- [ ] AC-03: Nested Dockerfile bez rootowego markera nadal otrzymuje
  `GOV-STACK-001`.
- [ ] AC-04: Manifest zna `.yml` i `.yaml`, pełny Linux contract oraz pilot
  `mcp` przechodzą bez sztucznego root Dockerfile.

## Ryzyka i Uwagi
- Compose jest tylko markerem stosu, nie substytutem jawnej listy plików do
  inspekcji.
- Nie naprawiamy ani nie przepinamy obrazów downstream w tym ticketcie.
- Nie wykonujemy push, PR, merge, tagowania ani publikacji.

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
