# Ticket 052: Enforce immutable Docker image references

- **ID**: ticket-052
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-11

## Cel i Zakres

Egzekwować deklarowaną już przez standard zasadę immutable Docker inputs.
Gdy target ma `docker.required=true`, każdy nie-`scratch` obraz w instrukcji
Dockerfile `FROM` oraz każdy Compose `image:` musi zawierać pełny
`@sha256:<64 lowercase hex>`.

Kontrola jest deterministyczna, offline i bez nowych zależności. Lokalne
serwisy Compose używające wyłącznie `build:` nie wymagają sztucznego `image:`.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Polecenie użytkownika, aby poprawiać standard na podstawie
  kolejnych pilotów, stanowi bounded `SESSION_EXECUTION_AUTHORIZATION`.
- [x] AC-02: Pinned Dockerfile `FROM`, `scratch` i pinned Compose images
  przechodzą bez dostępu do sieci.
- [x] AC-03: Tag, `latest`, zmienna i niepełny/uppercase digest kończą się
  nowym, stabilnym `GOV-DOCKER-002` z dokładną ścieżką i numerem linii.
- [x] AC-04: Regresje pokrywają Dockerfile flags/alias oraz cytowane Compose
  scalar values, `C-DOCKER-004` mapuje rzeczywisty kod egzekwujący, a pełny
  kontrakt Linux przechodzi.
- [x] AC-05: Nie zmieniają się zależności, schema, manifest default, package,
  wersja ani wydanie; brak external delivery.

## Ryzyka i Uwagi

- Dependency-free skaner celowo obsługuje tylko normatywne miejsca referencji:
  `FROM` i scalar `image:`. Nie próbuje interpretować całego YAML ani build args.
- Dynamiczny `${IMAGE}` nie jest immutable evidence i ma fail-closed. Target
  może wygenerować przed review konkretny plik z digestem.
- `scratch` jest specjalnym, bezwarstwowym Docker base i nie ma registry digestu.
- Pilot `algitex` reprodukuje lukę: `python:3.12-slim` oraz wiele `:latest`
  przechodzą obecny `GOV-PASS` mimo dokumentowanej polityki pinów.
- Traceability wcześniej przypisywało `C-DOCKER-004` do `GOV-DOCKER-001`, choć
  ten kod sprawdza wyłącznie obecność runtime declaration. Nowy kod zastępuje
  to semantycznie błędne mapowanie.

## Autoryzacja

Dozwolone są lokalne zmiany i testy. Push, PR, merge, bump, tag i publikacja
pozostają poza zakresem.

## Dowody walidacji

- Pinned Dockerfile z `--platform`/`AS`, `scratch`, cytowany pinned Compose
  image i lokalny service `build:` przechodzą.
- Tag, Compose `latest`, `${BASE_IMAGE}` oraz uppercase digest zwracają
  `GOV-DOCKER-002`; text report wskazuje np. `Dockerfile:1` i `compose.yml:3`.
- `C-DOCKER-004` mapuje teraz faktyczny kod pinning zamiast presence-only
  `GOV-DOCKER-001`; rule traceability ma 0 nieprzypisanych kodów.
- Focused validator, rule-enforcement i wszystkie komendy Linux CI przechodzą.

## Stan

`DONE / DONE` lokalnie. Nie wykonano push, PR, merge, bumpu, tagu ani
publikacji.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-052/`.
