# Ticket 054: Ignore Compose output tags for build services

- **ID**: ticket-054
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-11

## Cel i Zakres

Rozszerzyć regułę `GOV-DOCKER-002` z ticketu 052 tak, aby rozróżniała
zewnętrzny obraz Compose od lokalnego tagu wynikowego. Mutowalne `image:` ma
pozostać błędem domyślnie, także przy samym `build:`, ponieważ Compose może
najpierw próbować pobrać obraz. Wyjątek jest bezpieczny wyłącznie wtedy, gdy ta
sama usługa jawnie deklaruje zarówno `build:`, jak i `pull_policy: build`.

Zakres obejmuje tylko deterministyczny parser bez zależności YAML, diagnostykę
i regresje validatora. Reguła dla każdego `FROM`, zewnętrznych usług Compose i
usług z inną lub brakującą polityką pobierania pozostaje fail-closed.

## Kryteria Odbioru (Acceptance Criteria)

- [ ] AC-01: Usługa Compose z mutowalnym `image:`, `build:` i dokładnym
  `pull_policy: build` przechodzi jako lokalny tag wynikowy.
- [ ] AC-02: Taki sam tag bez `pull_policy`, z inną polityką albo bez `build:`
  nadal daje `GOV-DOCKER-002` z lokalizacją linii obrazu.
- [ ] AC-03: Obrazy przypięte digestem, `scratch` i wszystkie istniejące
  kontrakty zachowują wynik; brak nowej zależności runtime.
- [ ] AC-04: Pełny kontrakt Linux oraz żywy pilot `semcod/code2logic`
  potwierdzają, że bezpieczny wyjątek nie ukrywa jego sześciu mutowalnych
  referencji.
- [ ] AC-05: Zmiana pozostaje lokalna; bez push, PR, merge, tagu, release ani
  publikacji pakietu.

## Ryzyka i Uwagi

- Lekki parser Compose nie może udawać pełnego parsera YAML. Rozpoznaje jedynie
  bezpośrednie pola usług pod `services:` i pozostaje fail-closed dla form,
  których nie potrafi bezpiecznie skorelować.
- Samo `build:` nie eliminuje pulla; wyjątek bez `pull_policy: build` osłabiłby
  politykę supply-chain.
- Ticket zależy od lokalnego ticketu 052; implementacja i walidacja mają bazę
  na jego dokładnym HEAD `ed3c577f6abb9cc4c26bed6e218ea6177ccda3cf`.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-054/`.
