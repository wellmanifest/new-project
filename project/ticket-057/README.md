# Ticket 057: Own VERSION in stackless repositories

- **ID**: ticket-057
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-11

## Cel i Zakres

Naprawić domyślny manifest dla repozytoriów bez wykrytego stosu. `VERSION`
jest plikiem obowiązkowym, lecz obecnie żaden workstream nie jest jego
właścicielem, więc poprawnie zaplanowana zmiana wersji kończy się
`GOV-WORKSTREAM-003`. Plik ma należeć do workstreamu `integration`, a test
walidatora ma utrwalić zarówno dozwolony, jak i odrzucony przypadek.

Zmiana obejmuje wyłącznie domyślną mapę własności i focused regression. Nie
tworzy `VERSION` w targetach, nie zmienia adopcji, stacków, schematu, wersji
pakietu ani Goal.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Polecenie użytkownika stanowi bounded
  `SESSION_EXECUTION_AUTHORIZATION` dla lokalnej implementacji i testów.
- [x] AC-02: Stackless manifest przypisuje dokładną ścieżkę `VERSION` do
  workstreamu `integration`.
- [x] AC-03: Ticket `integration` ograniczony do `VERSION` przechodzi
  walidację, a ticket `application` z tym samym zakresem otrzymuje
  `GOV-WORKSTREAM-003`.
- [x] AC-04: Focused governance validator, pełny Linux contract i Ruff
  przechodzą bez regresji.
- [x] AC-05: Powtórzony pilot `godot` przez exact-SHA standardu osiąga
  `GOV-PASS` bez wyłączania reguł własności.

## Ryzyka i Uwagi
- `VERSION` jest współdzielonym nośnikiem release, dlatego jego właścicielem
  jest `integration`, a nie szeroko uprzywilejowany workstream `governance`.
- Regresja musi użyć bazowego manifestu ze `stacks: []`, aby profil językowy
  nie maskował błędu.
- Nie wykonujemy push, PR, merge, tagowania ani publikacji.

## Dowody walidacji

- `bash tests/governance-validator.test.sh` przechodzi dla exact drzewa
  implementacji `8a65c3d`: `integration` może zmienić `VERSION`, a
  `application` otrzymuje `GOV-WORKSTREAM-003`.
- Wszystkie polecenia linuxowego joba CI przechodzą: osiem zestawów testów,
  kontrakty JSON, required-check wiring oraz kontrola kompletności suite.
- `ruff check scripts/governance_check.py` i `git diff --check` przechodzą.
- Świeży pilot `godot` z target-owned prerequisites na zaakceptowanej bazie
  przyjął exact rewizję `8a65c3d` przez Goal; commit payloadu `dd758ad`
  uzyskał `GOV-PASS` dla jawnej bazy, inferred base i zarządzanego wrappera.
- Pilot zachował `stacks: []`, `docker.required=false` i brak `Dockerfile`;
  `git fsck --full` oraz smoke test śledzonego HTML także przechodzą.
- Nie dodano zależności, nie zmieniono schematu ani runtime walidatora; zmiana
  powierzchni implementacyjnej to manifest i jego focused regression.

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
nie do `project/ticket-057/`.
