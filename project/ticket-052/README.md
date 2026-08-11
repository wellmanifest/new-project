# Ticket 052: Enforce immutable Docker image references

- **ID**: ticket-052
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
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
- [ ] AC-02: Pinned Dockerfile `FROM`, `scratch` i pinned Compose images
  przechodzą bez dostępu do sieci.
- [ ] AC-03: Tag, `latest`, zmienna i niepełny/uppercase digest kończą się
  nowym, stabilnym `GOV-DOCKER-002` z dokładną ścieżką i numerem linii.
- [ ] AC-04: Regresje pokrywają Dockerfile flags/alias oraz cytowane Compose
  scalar values, `C-DOCKER-004` mapuje rzeczywisty kod egzekwujący, a pełny
  kontrakt Linux przechodzi.
- [ ] AC-05: Nie zmieniają się zależności, schema, manifest default, package,
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

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-052/`.
