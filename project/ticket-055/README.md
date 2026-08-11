# Ticket 055: Resolve default base for multi-commit initial adoption

- **ID**: ticket-055
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-11

## Cel i Zakres

Naprawić domyślne uruchomienie `goal governance check` po wielocommitowej
adopcji standardu. Gdy użytkownik nie poda `--base`, zarządzany walidator ma
użyć `delivery.acceptedBaseSha` z dokładnie jednego aktywnego ticketu
adopcyjnego, dzięki czemu oceni cały commit planu i commit instalujący pakiet.

Jawne `--base` pozostaje nadrzędne. Zmiana nie przenosi reguł do Goal, nie
zgaduje bazy dla zwykłych ticketów i nie zmienia procesu publikacji.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Polecenie użytkownika stanowi bounded
  `SESSION_EXECUTION_AUTHORIZATION` dla lokalnej implementacji i testów.
- [x] AC-02: Brak `--base` przy dokładnie jednym aktywnym tickecie adopcyjnym
  rozwiązuje bazę do jego pełnego `delivery.acceptedBaseSha`.
- [x] AC-03: Fixture `base -> plan commit -> adoption commit` przechodzi przez
  zarządzany walidator bez jawnego `--base` i obejmuje zmieniony lock.
- [x] AC-04: Jawny `--base` zachowuje dotychczasowe pierwszeństwo, a błędna lub
  niejednoznaczna adopcja nadal kończy się fail-closed `GOV-SYNC-001`.
- [x] AC-05: Test walidatora i pełny kontrakt Linux przechodzą; poprawka zostaje
  ponownie sprawdzona przez `./project.sh` w izolowanym pilocie `semcod/codot`.

## Ryzyka i Uwagi

- Automatyczna baza jest dopuszczona wyłącznie dla jednego aktywnego ticketu
  z deklaracją `standardAdoption`; zwykłe tickety zachowują obecny kontrakt.
- Źródłem bazy jest zaakceptowany pełny SHA zapisany przed implementacją, nie
  `HEAD^`, nazwa brancha ani stan zdalny.
- Nie wykonujemy push, PR, merge, tagowania ani publikacji.

## Dowody walidacji

- `bash tests/governance-validator.test.sh` przechodzi dla jawnej i wyznaczonej
  bazy w historii `base -> plan -> initial adoption`.
- Wszystkie osiem zestawów Linux CI, kontrakty JSON, kontrola kompletności CI
  i `ruff check scripts/governance_check.py` przechodzą.
- Izolowany `semcod/codot` przypięty do kandydata `ebc274a` przechodzi przez
  `./project.sh` bez `--base`, jawny Goal i idempotentny preflight. Python,
  skupiony Go i Compose zachowują baseline; pełny Go ma ten sam wcześniejszy
  błąd kompilacji. Oryginalny checkout i kod produktu pozostały niezmienione.

## Autoryzacja

Bieżące polecenie użytkownika zleca lokalną poprawkę standardu, test regresyjny
i ponowienie pilota. Operacje zewnętrzne wymagają osobnej dyspozycji.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-055/`.
