# Ticket 026: Egzekwowalne pokrycie reguł CONTRIBUTING w runtime i CI huba

- **ID**: ticket-026
- **Owner**: unresolved:human
- **Status**: PLAN
- **Workflow state**: WAIT_FOR_APPROVAL
- **Utworzono**: 2026-08-05

## Cel i zakres

Usunąć możliwość mylenia obecności reguły w `CONTRIBUTING.md` z jej
deterministycznym egzekwowaniem. Dodać jeden wersjonowany rejestr, który mapuje
każdą regułę `C-*` na klasę egzekwowania, zamknięty adapter, dowód testowy i
jawny stan pokrycia. `scripts/runtime.sh policy` ma odrzucać brakującą,
zduplikowaną albo nieobsługiwaną mapę.

Ten ticket jest pierwszym małym wycinkiem naprawy. Nie implementuje w jednym
PR wszystkich zachowań wymagających API GitHub, merge queue, uruchomionego
Dockera ani decyzji człowieka. Takie reguły muszą być jawnie sklasyfikowane
jako `protected` albo `human`, a luki semantyczne pozostają widoczne jako
`PARTIAL`/`MISSING`, nie jako fałszywe `PASS`.

## Ustalony stan bazowy

- `CONTRIBUTING.md` zawiera 87 unikalnych reguł `C-*`.
- `scripts/runtime.sh policy` enumeruje tylko 10 reguł
  `C-EVALUATION-001..010`.
- Pełne lokalne egzekwowanie ma obecnie wyłącznie rdzeń precedencji twardych
  bramek (`C-EVALUATION-004`) i odrzucanie nieaktualnych powiązań
  (`C-EVALUATION-005`). Pozostałe reguły tej sekcji są częściowe albo zależą
  od zewnętrznego producenta/chronionego workflow.
- CI huba uruchamia testy jednostkowe, ale nie waliduje własnego diffu
  kontraktem ticketu. Audyt PR #34 wykazał `GOV-TICKET-001` dla zmiany
  `.github/workflows/ci.yml` przy ticketcie pozostającym w `PLAN`.
- `governance/manifest.default.json` jest manifestem targetu, więc nie może być
  bezpośrednio użyty jako profil self-governance huba bez fałszywych błędów
  Docker/adoption. Dedykowany profil huba jest osobnym, zależnym wycinkiem.

## Kryteria odbioru

- [ ] AC-01: Rejestr zawiera dokładnie po jednym wpisie dla każdej reguły
  `C-*` odczytanej z bieżącego `CONTRIBUTING.md`.
- [ ] AC-02: Każdy wpis deklaruje klasę `deterministic`, `protected`, `human`
  albo `procedural`, zamknięty identyfikator egzekutora, stan
  `FULL`/`PARTIAL`/`MISSING` oraz referencję do dowodu/testu.
- [ ] AC-03: `scripts/runtime.sh policy` kończy się błędem dla brakującej,
  zduplikowanej, nieznanej albo fałszywie pełnej mapy.
- [ ] AC-04: Raport policy podaje liczbę wszystkich reguł oraz osobne liczniki
  `FULL`, `PARTIAL` i `MISSING`; zielony wynik składni nie ukrywa luk pokrycia.
- [ ] AC-05: Test mutacyjny usuwa wpis, dodaje nieznany adapter i oznacza regułę
  bez dowodu jako `FULL`; wszystkie trzy przypadki są odrzucane.
- [ ] AC-06: Rejestr i jego schemat są częścią immutable adoption package.
- [ ] AC-07: Istniejące testy change-evaluation i governance pozostają zielone.

## Proponowany bounded delivery po akceptacji

- Wynik: jeden wyczerpujący, fail-closed rejestr pokrycia `C-*`.
- Złożoność: `S`, limit 30 minut, 5 plików implementacyjnych, 2 komponenty,
  bez nowych zależności i zmian publicznego API.
- Komponent kontraktu: schemat, rejestr i wpisy immutable package manifest.
- Komponent runtime: `scripts/runtime.sh` oraz testy mutacyjne w istniejącym
  zestawie governance scripts.
- Rollback: odwrócenie jednego commita ticketu; istniejąca walidacja
  change-evaluation pozostaje dostępna.
- Dokładny `acceptedBaseSha` i `delivery.architecture.status=accepted` zostaną
  dopisane do intentu dopiero po zakończeniu kolizji i zatwierdzeniu planu.

## Kolejne, zależne wycinki po tym ticketcie

1. Domknąć semantykę `C-EVALUATION-006..010`: project direction, LLM
   provenance, Contribution Ledger, `merge_group`, atestację i status check.
2. Dodać osobny manifest self-governance huba i obowiązkową walidację diffu w
   `ci.yml`, aby przypadek wykryty na PR #34 nie mógł mieć zielonego CI.
3. Dopiero potem rozszerzyć zamknięty orchestrator o Docker, GitHub API i
   chronione adaptery; runtime lokalny nie może udawać trust rootu.

## Ryzyka i uwagi

- Rejestr pokrycia może sam ulec dezaktualizacji; dlatego zestaw ID jest
  zawsze wyprowadzany z bieżącego `CONTRIBUTING.md`, a nie kopiowany do testu.
- `FULL` oznacza pełne egzekwowanie w zadeklarowanej klasie i musi wskazywać
  istniejący egzekutor oraz test. Nie oznacza, że reguła wymagająca decyzji
  człowieka staje się lokalnie automatyzowalna.
- Ticket pozostaje w `PLAN`, ponieważ aktywny ticket 023 i PR #34 zmieniają
  nakładające się pliki governance/CI. Implementacja zacznie się dopiero po
  ich zakończeniu i ponownej synchronizacji bazy.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-026/`.
