# Ticket 082: Point governance identifiers at the live host

- **ID**: ticket-082
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-14

## Cel i Zakres

Standard publikuje dziesięć identyfikatorów wskazujących na `wellmanifest.dev`,
który nie jest już żywym hostem. Dziewięć repozytoriów w organizacji zaczęło
naprawiać to u siebie: tam, gdzie nie ma locka adopcji, zmiana weszła prosto na
`main`; w repozytoriach adoptowanych stoi zaparkowana na gałęzi
`chore/wellmanifest-com-host` bez PR-a, bo dotyka plików, których digesty
trzyma `manifest.lock.json`.

Ten ticket przenosi zmianę tam, gdzie jest jej miejsce — do pakietu, z którego
te pliki pochodzą. Repozytoria adoptujące przejmą ją przez ponowną adopcję
generatorem, a nie przez ręczną edycję plików zarządzanych.

Zakres obejmuje dwa `$id` schematów oraz `signedAttestationPredicateType` w
pięciu miejscach. Rozdzielenie ich jest niemożliwe: `manifest.schema.json`
pinuje predykat jako `const`, więc częściowa zmiana unieważniłaby każdy manifest
adoptującego repozytorium.

Poza zakresem: wydanie nowej rewizji do adopcji (decyzja właściciela) oraz
jakakolwiek edycja wewnątrz repozytoriów adoptujących.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Żaden identyfikator governance nie wskazuje już wycofanego hosta.
- [x] AC-02: Zestaw testów walidatora governance przechodzi z nową nazwą
  predykatu.
- [x] AC-03: Bramka hub przechodzi, a zmiana rozwiązuje się do dokładnie
  jednego ticketu workstreamu `governance`.

## Ryzyka i Uwagi
- Atestacje podpisane starym predykatem przestaną być uznawane po podniesieniu
  adopcji. Są związane z konkretnym HEAD-em i krótkożyciowe, więc mitygacją jest
  ponowne wystawienie atestacji po upgradzie, a nie akceptowanie dwóch wartości
  naraz — dwa dopuszczalne predykaty osłabiłyby granicę zaufania.
- `subactor/validator-agent` nie zawiera tej stałej na sztywno; czyta ją z
  manifestu repozytorium docelowego, więc weryfikator nie wymaga zmiany
  równoległej.
- Repozytoria adoptowane pozostają nienaruszone do momentu, w którym same
  wykonają `goal governance adopt --upgrade`.

## Dowody publikacji

- Pull request [#124](https://github.com/wellmanifest/new-project/pull/124)
  przeszedł `test` i `windows-governance` na dokładnym HEAD
  `7019ddd120caf94e628dc1fb5c7598919532ecb6`.
- Validator App `ifuri-validator-agent[bot]` zatwierdził ten sam HEAD, po czym
  chroniony merge zintegrował zmianę jako
  `e0c87a753d6ce7cda9dc1719993107f124b1b90d`.
- Gałąź implementacyjna została usunięta przed utworzeniem tego
  governance-only closure ze zintegrowanego `main`.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-claude.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-082/`.
