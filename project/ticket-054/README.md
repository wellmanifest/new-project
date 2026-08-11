# Ticket 054: Clarify Compose build image policy

- **ID**: ticket-054
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-11

## Cel i Zakres

Doprecyzować regułę `GOV-DOCKER-002` z ticketu 052 dla usług Compose,
które mają jednocześnie `build:` i mutowalne `image:`. Oficjalny kontrakt
Compose próbuje domyślnie pobrać taki obraz przed lokalnym buildem, więc
blokada jest prawidłowa. Dla usługi wyłącznie lokalnej pole `image:` można
pominąć; dla obrazu pobieranego należy użyć digestu.

Zakres obejmuje wyłącznie precyzyjniejszą remediację i regresję, że samo
`build:` nie wyłącza reguły. Nie dodaje częściowego parsera YAML ani nowego
wyjątku od polityki supply-chain.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Usługa Compose z samym `build:` i bez `image:` nadal przechodzi.
- [x] AC-02: Usługa z `build:` oraz mutowalnym `image:` nadal daje
  `GOV-DOCKER-002` z lokalizacją linii obrazu.
- [x] AC-03: Remediacja rozróżnia przypięcie zewnętrznego obrazu od usunięcia
  `image:` dla lokalnego buildu; brak parsera YAML i nowej zależności runtime.
- [x] AC-04: Pełny kontrakt Linux oraz żywy pilot `semcod/code2logic`
  potwierdzają, że doprecyzowanie nie ukrywa jego sześciu mutowalnych
  referencji.
- [x] AC-05: Zmiana pozostaje lokalna; bez push, PR, merge, tagu, release ani
  publikacji pakietu.

## Ryzyka i Uwagi

- Własny parser YAML dla jednego wyjątku powiększyłby zarządzany payload i
  stworzył ryzyko błędnej interpretacji Compose; został jawnie odrzucony.
- Samo `build:` nie eliminuje pulla; zwolnienie takich tagów osłabiłoby
  politykę supply-chain. Lokalny build może działać bez pola `image:`.
- Ticket zależy od lokalnego ticketu 052; implementacja i walidacja mają bazę
  na jego dokładnym HEAD `ed3c577f6abb9cc4c26bed6e218ea6177ccda3cf`.

## Wynik walidacji

- Focused validator oraz pełne osiem zestawów testów Linux przechodzą.
- Istniejący fixture z `build:` bez `image:` pozostaje zielony; nowy fixture
  z `build:` i `image: local/code2logic:latest` daje `GOV-DOCKER-002`, dokładną
  linię i nową remediację.
- Złożony kandydat `4ee2b3854c8651935d93dbbc144858befe75a8cc`
  przechodzi pełny kontrakt i przypięty Ruff downstream bez naruszeń.
- Upgrade przez Goal w żywym pilocie code2logic jest idempotentny i nadal
  raportuje wszystkie sześć mutowalnych referencji z precyzyjniejszą poradą.
- Ostateczna implementacja zmienia jedną linię produkcyjną i dodaje 15 linii
  testu; nie dodaje parsera, zależności ani nowej gałęzi polityki.
- Nie wykonano push, PR, merge, tagu, release ani publikacji pakietu.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-054/`.
